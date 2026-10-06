"""TCP Server for LAN Chat and File Sharing.

Handles multiple client connections via threads, manages client registration,
relays broadcast/private messages, and streams file transfers.
"""
import argparse
import socket
import sys
import threading
from pathlib import Path
from typing import Dict, Tuple

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import BUFFER_SIZE, LOGS_DIR, SERVER_HOST, SERVER_PORT
from app.protocol import recv_msg, send_msg
from app.utils import get_local_ip, setup_logger

logger = setup_logger("LAN_Server", LOGS_DIR / "server.log")

class ChatServer:
    def __init__(self, host: str = SERVER_HOST, port: int = SERVER_PORT):
        self.host = host
        self.port = port
        self.server_sock: socket.socket | None = None
        self.is_running = False
        # username -> (client_socket, address)
        self.clients: Dict[str, Tuple[socket.socket, Tuple[str, int]]] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        """Bind, listen, and accept client TCP connections."""
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen(20)
            self.is_running = True
            local_ip = get_local_ip()

            logger.info("=" * 60)
            logger.info("  LAN CHAT & FILE SHARING SERVER STARTED")
            logger.info(f"  Bind Address : {self.host}:{self.port}")
            logger.info(f"  LAN Host IP  : {local_ip}")
            logger.info(f"  Port         : {self.port}")
            logger.info("=" * 60)

            while self.is_running:
                try:
                    client_sock, client_addr = self.server_sock.accept()
                    logger.info(f"Accepted TCP connection from {client_addr[0]}:{client_addr[1]}")
                    threading.Thread(
                        target=self._handle_client,
                        args=(client_sock, client_addr),
                        daemon=True
                    ).start()
                except OSError:
                    break

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
        finally:
            self.stop()

    def _handle_client(self, client_sock: socket.socket, client_addr: Tuple[str, int]) -> None:
        """Per-client worker thread lifecycle."""
        username = ""
        try:
            # First frame must be registration
            header, _ = recv_msg(client_sock)
            if header.get("type") != "register" or not header.get("sender"):
                send_msg(client_sock, {"type": "error", "message": "Invalid registration."})
                client_sock.close()
                return

            req_username = header["sender"].strip()
            with self.lock:
                if req_username in self.clients:
                    send_msg(client_sock, {"type": "error", "message": "Username already taken."})
                    client_sock.close()
                    return
                self.clients[req_username] = (client_sock, client_addr)
                username = req_username

            send_msg(client_sock, {"type": "ack", "message": f"Welcome, {username}!"})
            logger.info(f"Client registered: '{username}' from {client_addr}")
            self._broadcast({"type": "system", "message": f"User '{username}' has joined the network."}, exclude=username)
            self._send_client_list()

            # Message processing loop
            while self.is_running:
                header, binary_payload = recv_msg(client_sock)
                msg_type = header.get("type")

                if msg_type == "chat":
                    # Broadcast chat message
                    recipient = header.get("recipient", "ALL")
                    if recipient == "ALL":
                        self._broadcast({
                            "type": "chat",
                            "sender": username,
                            "recipient": "ALL",
                            "message": header.get("message", "")
                        }, exclude=username)
                    else:
                        # Private message
                        self._send_private(username, recipient, header.get("message", ""))

                elif msg_type == "file_meta":
                    # File transfer header announcement
                    recipient = header.get("recipient", "ALL")
                    if recipient == "ALL":
                        self._broadcast({
                            "type": "file_meta",
                            "sender": username,
                            "recipient": "ALL",
                            "filename": header.get("filename"),
                            "filesize": header.get("filesize"),
                            "sha256": header.get("sha256")
                        }, exclude=username)
                    else:
                        self._forward_to(recipient, header)

                elif msg_type == "file_chunk":
                    # Stream file chunk to recipient
                    recipient = header.get("recipient", "ALL")
                    if recipient == "ALL":
                        self._broadcast_binary(header, binary_payload, exclude=username)
                    else:
                        self._forward_to(recipient, header, binary_payload)

                elif msg_type == "file_complete":
                    recipient = header.get("recipient", "ALL")
                    if recipient == "ALL":
                        self._broadcast(header, exclude=username)
                    else:
                        self._forward_to(recipient, header)

                elif msg_type == "get_clients":
                    with self.lock:
                        names = list(self.clients.keys())
                    send_msg(client_sock, {"type": "client_list", "clients": names})

                elif msg_type == "disconnect":
                    break

        except (ConnectionError, OSError) as e:
            logger.warning(f"Connection lost for client '{username or client_addr}': {e}")
        finally:
            self._disconnect_client(username, client_sock)

    def _broadcast(self, header: dict, exclude: str = "") -> None:
        """Send a JSON control message to all registered clients except 'exclude'."""
        with self.lock:
            for name, (sock, _) in list(self.clients.items()):
                if name != exclude:
                    try:
                        send_msg(sock, header)
                    except Exception:
                        pass

    def _broadcast_binary(self, header: dict, payload: bytes, exclude: str = "") -> None:
        """Broadcast a message containing binary data to all clients."""
        with self.lock:
            for name, (sock, _) in list(self.clients.items()):
                if name != exclude:
                    try:
                        send_msg(sock, header, payload)
                    except Exception:
                        pass

    def _send_private(self, sender: str, recipient: str, message: str) -> None:
        """Route a private message between two clients."""
        with self.lock:
            if recipient in self.clients:
                sock, _ = self.clients[recipient]
                send_msg(sock, {
                    "type": "private",
                    "sender": sender,
                    "recipient": recipient,
                    "message": message
                })
            elif sender in self.clients:
                sock, _ = self.clients[sender]
                send_msg(sock, {
                    "type": "error",
                    "message": f"User '{recipient}' not found."
                })

    def _forward_to(self, recipient: str, header: dict, payload: bytes = b"") -> None:
        """Forward packet to a targeted client."""
        with self.lock:
            if recipient in self.clients:
                sock, _ = self.clients[recipient]
                send_msg(sock, header, payload)

    def _send_client_list(self) -> None:
        """Broadcast updated online client list."""
        with self.lock:
            names = list(self.clients.keys())
            for _, (sock, _) in self.clients.items():
                try:
                    send_msg(sock, {"type": "client_list", "clients": names})
                except Exception:
                    pass

    def _disconnect_client(self, username: str, sock: socket.socket) -> None:
        """Clean up disconnected client socket and notify peers."""
        try:
            sock.close()
        except Exception:
            pass

        if username:
            with self.lock:
                if username in self.clients:
                    del self.clients[username]
            logger.info(f"Client '{username}' disconnected.")
            self._broadcast({"type": "system", "message": f"User '{username}' left the chat."})
            self._send_client_list()

    def stop(self) -> None:
        """Gracefully shut down the server and terminate client connections."""
        self.is_running = False
        with self.lock:
            for name, (sock, _) in list(self.clients.items()):
                try:
                    send_msg(sock, {"type": "system", "message": "Server shutting down."})
                    sock.close()
                except Exception:
                    pass
            self.clients.clear()

        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        logger.info("Server stopped.")

def main():
    parser = argparse.ArgumentParser(description="LAN Chat & File Sharing Server")
    parser.add_argument("--host", default=SERVER_HOST, help=f"Host address to bind (default: {SERVER_HOST})")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Port number (default: {SERVER_PORT})")
    args = parser.parse_args()

    server = ChatServer(host=args.host, port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("\nReceived keyboard interrupt, shutting down server.")
        server.stop()

if __name__ == "__main__":
    main()
