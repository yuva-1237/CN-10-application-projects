"""Mini HTTP/1.1 Web Server built directly on TCP stream sockets."""
import argparse
import socket
import sys
import threading
from pathlib import Path
from typing import Tuple

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import HTTP_HOST, HTTP_PORT, LOGS_DIR, PUBLIC_DIR, SERVER_NAME
from app.http_parser import HTTPRequest, HTTPResponse
from app.utils import get_http_date, get_mime_type, setup_logger

logger = setup_logger("MiniHTTP_Server", LOGS_DIR / "http_server.log")

class MiniHTTPServer:
    def __init__(self, host: str = HTTP_HOST, port: int = HTTP_PORT, public_dir: Path = PUBLIC_DIR):
        self.host = host
        self.port = port
        self.public_dir = public_dir.resolve()
        self.server_sock: socket.socket | None = None
        self.is_running = False

    def start(self) -> None:
        """Initialize TCP socket and listen for HTTP client connections."""
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen(50)
            self.is_running = True

            logger.info("=" * 60)
            logger.info("  MINI HTTP/1.1 WEB SERVER STARTED (RAW TCP SOCKET)")
            logger.info(f"  URL            : http://{self.host}:{self.port}")
            logger.info(f"  Public Web Root: {self.public_dir}")
            logger.info("=" * 60)

            while self.is_running:
                try:
                    conn, client_addr = self.server_sock.accept()
                    threading.Thread(
                        target=self._handle_client,
                        args=(conn, client_addr),
                        daemon=True
                    ).start()
                except OSError:
                    break
        finally:
            self.stop()

    def _handle_client(self, conn: socket.socket, client_addr: Tuple[str, int]) -> None:
        """Read and serve single HTTP request over TCP."""
        conn.settimeout(5.0)
        try:
            # Read initial request buffer (up to 8KB)
            raw_req = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                raw_req.extend(chunk)
                if b"\r\n\r\n" in raw_req or len(raw_req) > 65536:
                    break

            if not raw_req:
                return

            req = HTTPRequest.parse(bytes(raw_req))
            date_str = get_http_date()

            if req is None:
                # 400 Bad Request
                resp = HTTPResponse.build(
                    400,
                    content_type="text/plain; charset=utf-8",
                    body=b"400 Bad Request: Malformed HTTP request line or headers.\r\n",
                    server_name=SERVER_NAME,
                    date_str=date_str
                )
                conn.sendall(resp)
                logger.warning(f"{client_addr[0]} - - \"MALFORMED\" 400")
                return

            # Check supported methods: GET and HEAD
            if req.method not in ("GET", "HEAD"):
                # 405 Method Not Allowed
                body = f"405 Method Not Allowed: {req.method} is not supported by MiniHTTPServer.\r\n".encode("utf-8")
                resp = HTTPResponse.build(
                    405,
                    content_type="text/plain; charset=utf-8",
                    body=body,
                    extra_headers={"Allow": "GET, HEAD"},
                    server_name=SERVER_NAME,
                    date_str=date_str
                )
                conn.sendall(resp)
                logger.warning(f"{client_addr[0]} - - \"{req.method} {req.path}\" 405 Method Not Allowed")
                return

            # Resolve filesystem path securely (prevent directory traversal)
            req_rel = req.path.lstrip("/")
            target_file = (self.public_dir / req_rel).resolve()

            # Security check: Ensure target_file is strictly inside self.public_dir
            if not str(target_file).startswith(str(self.public_dir)):
                # Directory traversal attempt
                resp = HTTPResponse.build(
                    403,
                    content_type="text/plain",
                    body=b"403 Forbidden: Path traversal prohibited.\r\n",
                    server_name=SERVER_NAME,
                    date_str=date_str
                )
                conn.sendall(resp)
                logger.warning(f"{client_addr[0]} - - \"{req.method} {req.path}\" 403 Forbidden")
                return

            if target_file.is_dir():
                target_file = target_file / "index.html"

            if target_file.exists() and target_file.is_file():
                content_type = get_mime_type(target_file)
                file_bytes = target_file.read_bytes()

                # For HEAD method, body is omitted per RFC 2616 Sec 9.4
                body_to_send = b"" if req.method == "HEAD" else file_bytes

                resp = HTTPResponse.build(
                    200,
                    content_type=content_type,
                    body=body_to_send,
                    extra_headers={"Content-Length": str(len(file_bytes))},
                    server_name=SERVER_NAME,
                    date_str=date_str
                )
                conn.sendall(resp)
                logger.info(f"{client_addr[0]} - - \"{req.method} {req.path}\" 200 OK ({len(file_bytes)} bytes)")
            else:
                # 404 Not Found
                not_found_file = self.public_dir / "404.html"
                if not_found_file.exists():
                    body = not_found_file.read_bytes()
                    ctype = "text/html; charset=utf-8"
                else:
                    body = b"<h1>404 Not Found</h1><p>The requested file does not exist.</p>"
                    ctype = "text/html; charset=utf-8"

                body_to_send = b"" if req.method == "HEAD" else body
                resp = HTTPResponse.build(
                    404,
                    content_type=ctype,
                    body=body_to_send,
                    extra_headers={"Content-Length": str(len(body))},
                    server_name=SERVER_NAME,
                    date_str=date_str
                )
                conn.sendall(resp)
                logger.warning(f"{client_addr[0]} - - \"{req.method} {req.path}\" 404 Not Found")

        except Exception as e:
            logger.error(f"Error handling HTTP connection from {client_addr}: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def stop(self) -> None:
        """Stop listening and close server socket."""
        self.is_running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        logger.info("Mini HTTP Server stopped.")

def main():
    parser = argparse.ArgumentParser(description="Mini HTTP/1.1 Socket Web Server")
    parser.add_argument("--host", default=HTTP_HOST, help=f"Host interface (default: {HTTP_HOST})")
    parser.add_argument("--port", type=int, default=HTTP_PORT, help=f"Port (default: {HTTP_PORT})")
    args = parser.parse_args()

    server = MiniHTTPServer(host=args.host, port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main()
