"""Multi-Client TCP Client with Interactive and Swarm Load-Testing Modes."""
import argparse
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import SERVER_PORT
from app.utils import pack_frame, setup_logger, unpack_frames

logger = setup_logger("MultiClient_Client")

class MultiClient:
    def __init__(self, host: str, port: int, username: str):
        self.host = host
        self.port = port
        self.username = username
        self.sock: Optional[socket.socket] = None
        self.is_connected = False
        self.in_buffer = bytearray()
        self.on_message: Optional[Callable[[dict], None]] = None
        self.last_stats: Optional[dict] = None

    def connect(self) -> bool:
        """Connect to TCP server, start listener, and register username."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.is_connected = True

            threading.Thread(target=self._read_loop, daemon=True).start()

            # Send registration frame
            self.send({"type": "register", "username": self.username})
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port}: {e}")
            if self.sock:
                self.sock.close()
            return False

    def _read_loop(self) -> None:
        """Background thread unpacking incoming frames."""
        while self.is_connected and self.sock:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                self.in_buffer.extend(data)
                messages, self.in_buffer = unpack_frames(self.in_buffer)
                for msg in messages:
                    if msg.get("type") == "stats":
                        self.last_stats = msg
                    if self.on_message:
                        self.on_message(msg)
            except Exception:
                break
        self.is_connected = False

    def send(self, msg: dict) -> None:
        """Send framed message over socket."""
        if self.sock and self.is_connected:
            self.sock.sendall(pack_frame(msg))

    def broadcast(self, text: str) -> None:
        self.send({"type": "broadcast", "message": text})

    def private(self, recipient: str, text: str) -> None:
        self.send({"type": "private", "recipient": recipient, "message": text})

    def get_stats(self) -> None:
        self.send({"type": "get_stats"})

    def disconnect(self) -> None:
        self.is_connected = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

def run_swarm(host: str, port: int, count: int = 5) -> None:
    """Launch N simultaneous concurrent clients to demonstrate concurrent capacity."""
    print("\n" + "=" * 65)
    print(f"  LAUNCHING CONCURRENT CLIENT SWARM ({count} SIMULTANEOUS CLIENTS)")
    print("=" * 65)

    clients: List[MultiClient] = []
    received_counts = [0] * count

    for i in range(count):
        user = f"Swarm_Bot_{i + 1}"
        c = MultiClient(host, port, user)

        def make_cb(idx):
            return lambda m: None  # silent callback
        c.on_message = make_cb(i)

        if c.connect():
            clients.append(c)
            print(f"[{i + 1}/{count}] Connected & Registered '{user}'")
        time.sleep(0.05)

    time.sleep(0.5)
    print(f"\nAll {len(clients)} clients actively connected simultaneously.")
    print("Broadcasting test payload from Swarm_Bot_1 to all peers...")
    clients[0].broadcast("Hello swarm network!")
    time.sleep(0.5)

    # Query stats from client 0
    clients[0].get_stats()
    time.sleep(0.3)
    if clients[0].last_stats:
        s = clients[0].last_stats
        print("\n" + "=" * 65)
        print("  SERVER TELEMETRY REPORT")
        print("=" * 65)
        print(f"Active Connected Clients : {s['active_clients']}")
        print(f"Total Connections Logged : {s['total_connections']}")
        print(f"Peak Concurrent Clients  : {s['peak_clients']}")
        print(f"Messages Processed       : {s['messages_received']} recv / {s['messages_sent']} sent")
        print("=" * 65)

    print("\nTearing down client swarm...")
    for c in clients:
        c.disconnect()
    time.sleep(0.3)
    print("Swarm simulation complete.")

def main():
    parser = argparse.ArgumentParser(description="Multi-Client TCP Client")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Server port")
    parser.add_argument("--user", default=None, help="Username")
    parser.add_argument("--swarm", type=int, default=None, help="Run automated concurrent swarm of N clients")
    args = parser.parse_args()

    if args.swarm:
        run_swarm(args.host, args.port, count=args.swarm)
        return

    username = args.user or input("Enter username: ").strip()
    client = MultiClient(args.host, args.port, username)

    def print_msg(m):
        m_type = m.get("type")
        if m_type == "chat":
            print(f"\n[{m.get('sender')}]: {m.get('message')}\n> ", end="", flush=True)
        elif m_type == "private":
            print(f"\n[PRIVATE from {m.get('sender')}]: {m.get('message')}\n> ", end="", flush=True)
        elif m_type == "system":
            print(f"\n[SYSTEM]: {m.get('message')}\n> ", end="", flush=True)
        elif m_type == "stats":
            print(f"\n[STATS]: Active={m.get('active_clients')}, Peak={m.get('peak_clients')}, Total={m.get('total_connections')}\n> ", end="", flush=True)
        elif m_type == "error":
            print(f"\n[ERROR]: {m.get('message')}\n> ", end="", flush=True)

    client.on_message = print_msg
    if not client.connect():
        print("Connection failed.")
        return

    print(f"Connected to {args.host}:{args.port} as '{username}'.")
    print("Commands: /stats, /msg <user> <text>, /quit, or type text to broadcast.\n")

    try:
        while client.is_connected:
            line = input("> ").strip()
            if not line:
                continue
            if line == "/quit":
                break
            elif line == "/stats":
                client.get_stats()
            elif line.startswith("/msg"):
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    client.private(parts[1], parts[2])
                else:
                    print("Usage: /msg <username> <text>")
            else:
                client.broadcast(line)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
