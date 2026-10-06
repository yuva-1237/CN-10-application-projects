"""TCP Client for LAN Chat and File Sharing.

Supports full duplex interactive communication:
- Background listener thread for incoming broadcasts, private messages, and file streams.
- Interactive terminal input loop or programmatic API for automated testing.
"""
import argparse
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import CHUNK_SIZE, DOWNLOADS_DIR, LOGS_DIR, SERVER_PORT
from app.protocol import recv_msg, send_msg
from app.utils import calculate_sha256, format_bytes, setup_logger

logger = setup_logger("LAN_Client", LOGS_DIR / "client.log")

class ChatClient:
    def __init__(self, host: str, port: int, username: str, downloads_dir: Path = DOWNLOADS_DIR):
        self.host = host
        self.port = port
        self.username = username
        self.downloads_dir = downloads_dir
        self.sock: Optional[socket.socket] = None
        self.is_connected = False
        self.listener_thread: Optional[threading.Thread] = None

        # Tracking active incoming file streams
        self.incoming_files: dict[str, dict] = {}
        self.online_users: list[str] = []
        self.on_message_callback: Optional[Callable[[dict, bytes], None]] = None

    def connect(self) -> bool:
        """Connect to the TCP server and perform registration handshake."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            # Send registration
            send_msg(self.sock, {"type": "register", "sender": self.username})
            resp_header, _ = recv_msg(self.sock)

            if resp_header.get("type") == "ack":
                self.is_connected = True
                logger.info(f"Connected to server {self.host}:{self.port} as '{self.username}'.")
                self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
                self.listener_thread.start()
                return True
            else:
                logger.error(f"Registration failed: {resp_header.get('message')}")
                self.sock.close()
                return False

        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            if self.sock:
                self.sock.close()
            return False

    def _listen_loop(self) -> None:
        """Background thread receiving server frames."""
        while self.is_connected and self.sock:
            try:
                header, payload = recv_msg(self.sock)
                msg_type = header.get("type")

                if self.on_message_callback:
                    self.on_message_callback(header, payload)

                if msg_type == "chat":
                    sender = header.get("sender")
                    msg = header.get("message")
                    print(f"\n[{sender} (Broadcast)]: {msg}\n> ", end="", flush=True)

                elif msg_type == "private":
                    sender = header.get("sender")
                    msg = header.get("message")
                    print(f"\n[PRIVATE from {sender}]: {msg}\n> ", end="", flush=True)

                elif msg_type == "system":
                    print(f"\n[SYSTEM]: {header.get('message')}\n> ", end="", flush=True)

                elif msg_type == "client_list":
                    self.online_users = header.get("clients", [])

                elif msg_type == "file_meta":
                    sender = header.get("sender")
                    fname = header.get("filename")
                    fsize = header.get("filesize", 0)
                    sha = header.get("sha256")
                    dest_path = self.downloads_dir / f"recvd_{int(time.time())}_{fname}"
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    self.incoming_files[fname] = {
                        "path": dest_path,
                        "file": open(dest_path, "wb"),
                        "expected_size": fsize,
                        "received_size": 0,
                        "expected_sha": sha,
                        "sender": sender
                    }
                    print(f"\n[FILE INCOMING]: Receiving '{fname}' ({format_bytes(fsize)}) from {sender}...\n> ", end="", flush=True)

                elif msg_type == "file_chunk":
                    fname = header.get("filename")
                    if fname in self.incoming_files:
                        entry = self.incoming_files[fname]
                        entry["file"].write(payload)
                        entry["received_size"] += len(payload)

                elif msg_type == "file_complete":
                    fname = header.get("filename")
                    if fname in self.incoming_files:
                        entry = self.incoming_files.pop(fname)
                        entry["file"].close()
                        actual_sha = calculate_sha256(entry["path"])
                        if actual_sha == entry["expected_sha"]:
                            print(f"\n[FILE COMPLETE]: '{fname}' saved to {entry['path']} [Checksum Verified: SHA-256 OK]\n> ", end="", flush=True)
                        else:
                            print(f"\n[FILE CORRUPTED]: Checksum mismatch for '{fname}'!\n> ", end="", flush=True)

                elif msg_type == "error":
                    print(f"\n[ERROR]: {header.get('message')}\n> ", end="", flush=True)

            except (ConnectionError, OSError):
                if self.is_connected:
                    print("\n[DISCONNECTED]: Server connection terminated.")
                break

        self.is_connected = False

    def send_chat(self, message: str) -> None:
        """Send a public broadcast chat message."""
        if not self.is_connected or not self.sock:
            raise ConnectionError("Client is not connected.")
        send_msg(self.sock, {
            "type": "chat",
            "sender": self.username,
            "recipient": "ALL",
            "message": message
        })

    def send_private(self, recipient: str, message: str) -> None:
        """Send a direct message to a specific user."""
        if not self.is_connected or not self.sock:
            raise ConnectionError("Client is not connected.")
        send_msg(self.sock, {
            "type": "chat",
            "sender": self.username,
            "recipient": recipient,
            "message": message
        })

    def request_client_list(self) -> None:
        """Request the latest connected client list."""
        if self.sock:
            send_msg(self.sock, {"type": "get_clients"})

    def send_file(self, filepath: Path, recipient: str = "ALL") -> bool:
        """Stream a local file across the network in chunks with SHA-256 integrity check."""
        if not self.is_connected or not self.sock:
            raise ConnectionError("Client is not connected.")

        if not filepath.exists() or not filepath.is_file():
            logger.error(f"File not found: {filepath}")
            return False

        filesize = filepath.stat().st_size
        sha256_hash = calculate_sha256(filepath)
        filename = filepath.name

        # 1. Send metadata announcement
        send_msg(self.sock, {
            "type": "file_meta",
            "sender": self.username,
            "recipient": recipient,
            "filename": filename,
            "filesize": filesize,
            "sha256": sha256_hash
        })

        # 2. Stream chunks
        sent_bytes = 0
        with open(filepath, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                send_msg(self.sock, {
                    "type": "file_chunk",
                    "sender": self.username,
                    "recipient": recipient,
                    "filename": filename
                }, binary_payload=chunk)
                sent_bytes += len(chunk)

        # 3. Send completion notice
        send_msg(self.sock, {
            "type": "file_complete",
            "sender": self.username,
            "recipient": recipient,
            "filename": filename,
            "sha256": sha256_hash
        })

        logger.info(f"File '{filename}' ({format_bytes(filesize)}) sent to '{recipient}'.")
        return True

    def disconnect(self) -> None:
        """Gracefully disconnect from the server."""
        if self.sock and self.is_connected:
            try:
                send_msg(self.sock, {"type": "disconnect", "sender": self.username})
                self.sock.close()
            except Exception:
                pass
        self.is_connected = False
        logger.info("Disconnected from server.")

def print_help():
    print("""
Commands:
  /help                       Show this help menu
  /list                       List active online users
  /msg <username> <message>   Send a private message to a specific user
  /sendfile <path> [user]     Send a file (defaults to ALL if user omitted)
  /quit                       Disconnect and exit
  <any text>                  Broadcast message to all users
    """)

def main():
    parser = argparse.ArgumentParser(description="LAN Chat & File Sharing Client")
    parser.add_argument("--host", default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Server port (default: {SERVER_PORT})")
    parser.add_argument("--user", default=None, help="Username to register with")
    args = parser.parse_args()

    username = args.user or input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    client = ChatClient(host=args.host, port=args.port, username=username)
    if not client.connect():
        print("Unable to connect to server.")
        return

    print(f"\n=== Logged in as '{username}' on {args.host}:{args.port} ===")
    print_help()

    try:
        while client.is_connected:
            line = input("> ").strip()
            if not line:
                continue

            if line.startswith("/help"):
                print_help()
            elif line.startswith("/list"):
                client.request_client_list()
                time.sleep(0.2)
                print(f"Online users ({len(client.online_users)}): {', '.join(client.online_users)}")
            elif line.startswith("/msg"):
                parts = line.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: /msg <username> <message>")
                else:
                    client.send_private(parts[1], parts[2])
            elif line.startswith("/sendfile"):
                parts = line.split(maxsplit=2)
                if len(parts) < 2:
                    print("Usage: /sendfile <filepath> [recipient]")
                else:
                    fpath = Path(parts[1])
                    recip = parts[2] if len(parts) >= 3 else "ALL"
                    if fpath.exists():
                        print(f"Transmitting file '{fpath.name}' to '{recip}'...")
                        client.send_file(fpath, recipient=recip)
                    else:
                        print(f"File does not exist: {fpath}")
            elif line.startswith("/quit"):
                break
            else:
                client.send_chat(line)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
