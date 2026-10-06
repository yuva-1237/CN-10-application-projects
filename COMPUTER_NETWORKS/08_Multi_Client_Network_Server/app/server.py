"""High-Concurrency Non-Blocking TCP Server using Selectors I/O Multiplexing."""
import argparse
import selectors
import socket
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import BUFFER_SIZE, LOGS_DIR, SERVER_HOST, SERVER_PORT
from app.utils import ServerStats, pack_frame, setup_logger, unpack_frames

logger = setup_logger("MultiClient_Server", LOGS_DIR / "server.log")

class ClientSession:
    def __init__(self, sock: socket.socket, addr: Tuple[str, int]):
        self.sock = sock
        self.addr = addr
        self.username: Optional[str] = None
        self.in_buffer = bytearray()
        self.out_buffer = bytearray()

class MultiClientServer:
    def __init__(self, host: str = SERVER_HOST, port: int = SERVER_PORT):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
        self.server_sock: Optional[socket.socket] = None
        self.is_running = False
        # socket -> ClientSession
        self.sessions: Dict[socket.socket, ClientSession] = {}
        # username -> ClientSession
        self.users: Dict[str, ClientSession] = {}
        self.stats = ServerStats()

    def start(self) -> None:
        """Initialize non-blocking socket listener and run the event loop."""
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(128)
        self.server_sock.setblocking(False)

        # Register server socket with selector for READ events (incoming connections)
        self.selector.register(self.server_sock, selectors.EVENT_READ, data=self._accept_connection)
        self.is_running = True

        logger.info("=" * 65)
        logger.info("  MULTI-CLIENT TCP SERVER STARTED (I/O MULTIPLEXING)")
        logger.info(f"  Multiplexer Engine : {self.selector.__class__.__name__}")
        logger.info(f"  Listening on       : {self.host}:{self.port}")
        logger.info("=" * 65)

        try:
            while self.is_running:
                events = self.selector.select(timeout=0.5)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
        finally:
            self.stop()

    def _accept_connection(self, sock: socket.socket, mask: int) -> None:
        """Accept new TCP connection and register for non-blocking I/O."""
        try:
            conn, addr = sock.accept()
            conn.setblocking(False)
            session = ClientSession(conn, addr)
            self.sessions[conn] = session

            self.stats.total_connections += 1
            self.stats.active_clients = len(self.sessions)
            self.stats.peak_clients = max(self.stats.peak_clients, self.stats.active_clients)

            # Register client socket for READ events
            self.selector.register(conn, selectors.EVENT_READ, data=self._service_client)
            logger.info(f"Accepted connection #{self.stats.total_connections} from {addr[0]}:{addr[1]} (Active: {self.stats.active_clients})")
        except OSError:
            pass

    def _service_client(self, conn: socket.socket, mask: int) -> None:
        """Process readable and writable events for a connected client socket."""
        session = self.sessions.get(conn)
        if not session:
            return

        if mask & selectors.EVENT_READ:
            try:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    session.in_buffer.extend(data)
                    messages, session.in_buffer = unpack_frames(session.in_buffer)
                    for msg in messages:
                        self.stats.messages_received += 1
                        self._process_message(session, msg)
                else:
                    # Connection closed by client
                    self._close_session(session)
                    return
            except (ConnectionError, OSError):
                self._close_session(session)
                return

        if mask & selectors.EVENT_WRITE:
            if session.out_buffer:
                try:
                    sent = conn.send(session.out_buffer)
                    session.out_buffer = session.out_buffer[sent:]
                    self.stats.messages_sent += 1
                except (ConnectionError, OSError):
                    self._close_session(session)
                    return

            # If output buffer is flushed, remove EVENT_WRITE interest to avoid busy-wait
            if not session.out_buffer and conn in self.sessions:
                try:
                    self.selector.modify(conn, selectors.EVENT_READ, data=self._service_client)
                except Exception:
                    pass

    def _process_message(self, session: ClientSession, msg: dict) -> None:
        """Route framed messages based on message type."""
        m_type = msg.get("type")

        if m_type == "register":
            req_user = msg.get("username", "").strip()
            if not req_user or req_user in self.users:
                self._queue_message(session, {"type": "error", "message": "Username taken or invalid."})
            else:
                session.username = req_user
                self.users[req_user] = session
                self._queue_message(session, {"type": "ack", "message": f"Welcome {req_user}!"})
                logger.info(f"Registered user '{req_user}' [{session.addr[0]}:{session.addr[1]}]")
                self._broadcast({"type": "system", "message": f"{req_user} joined."}, exclude=req_user)

        elif m_type == "broadcast":
            sender = session.username or "Anonymous"
            self._broadcast({
                "type": "chat",
                "sender": sender,
                "message": msg.get("message", "")
            }, exclude=sender)

        elif m_type == "private":
            sender = session.username or "Anonymous"
            recipient = msg.get("recipient")
            target = self.users.get(recipient)
            if target:
                self._queue_message(target, {
                    "type": "private",
                    "sender": sender,
                    "message": msg.get("message", "")
                })
            else:
                self._queue_message(session, {"type": "error", "message": f"User '{recipient}' not found."})

        elif m_type == "get_clients":
            names = list(self.users.keys())
            self._queue_message(session, {"type": "clients", "users": names})

        elif m_type == "get_stats":
            self._queue_message(session, {
                "type": "stats",
                "active_clients": self.stats.active_clients,
                "total_connections": self.stats.total_connections,
                "peak_clients": self.stats.peak_clients,
                "messages_received": self.stats.messages_received,
                "messages_sent": self.stats.messages_sent
            })

    def _queue_message(self, session: ClientSession, msg: dict) -> None:
        """Append message to client's outbound buffer and arm EVENT_WRITE."""
        frame = pack_frame(msg)
        session.out_buffer.extend(frame)
        try:
            self.selector.modify(
                session.sock,
                selectors.EVENT_READ | selectors.EVENT_WRITE,
                data=self._service_client
            )
        except Exception:
            pass

    def _broadcast(self, msg: dict, exclude: str = "") -> None:
        """Queue frame for all active registered clients."""
        for user, s in list(self.users.items()):
            if user != exclude:
                self._queue_message(s, msg)

    def _close_session(self, session: ClientSession) -> None:
        """Deregister client socket, clean up user map, and notify peers."""
        conn = session.sock
        if conn in self.sessions:
            try:
                self.selector.unregister(conn)
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
            del self.sessions[conn]

        if session.username and session.username in self.users:
            user = session.username
            del self.users[user]
            logger.info(f"User '{user}' disconnected.")
            self._broadcast({"type": "system", "message": f"{user} left the server."})

        self.stats.active_clients = len(self.sessions)

    def stop(self) -> None:
        """Gracefully terminate server and release multiplexer."""
        self.is_running = False
        for s in list(self.sessions.values()):
            self._close_session(s)
        if self.server_sock:
            try:
                self.selector.unregister(self.server_sock)
                self.server_sock.close()
            except Exception:
                pass
        self.selector.close()
        logger.info("Multi-Client Server stopped.")

def main():
    parser = argparse.ArgumentParser(description="Multi-Client High-Concurrency TCP Server")
    parser.add_argument("--host", default=SERVER_HOST, help="Host address")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Port number")
    args = parser.parse_args()

    server = MultiClientServer(host=args.host, port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main()
