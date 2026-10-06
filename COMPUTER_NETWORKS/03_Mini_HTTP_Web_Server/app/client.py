"""Educational Raw TCP HTTP Client.

Constructs manual ASCII HTTP requests, sends them directly over a TCP stream socket,
and parses the raw incoming HTTP response bytes into clear academic sections.
"""
import argparse
import socket
import sys
from pathlib import Path
from typing import Dict, Tuple

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import HTTP_HOST, HTTP_PORT

class HTTPClient:
    def __init__(self, host: str = HTTP_HOST, port: int = HTTP_PORT):
        self.host = host
        self.port = port

    def send_request(
        self,
        method: str = "GET",
        path: str = "/",
        headers: Dict[str, str] | None = None,
        body: bytes = b""
    ) -> Tuple[int, Dict[str, str], bytes, str]:
        """Send raw HTTP request over TCP socket and return parsed response."""
        req_headers = {
            "Host": f"{self.host}:{self.port}",
            "User-Agent": "AcademicHTTPClient/1.0 (Python Socket)",
            "Accept": "*/*",
            "Connection": "close"
        }
        if headers:
            req_headers.update(headers)

        # Build raw ASCII request
        header_lines = [f"{method.upper()} {path} HTTP/1.1"]
        for k, v in req_headers.items():
            header_lines.append(f"{k}: {v}")
        raw_request = "\r\n".join(header_lines) + "\r\n\r\n"
        req_bytes = raw_request.encode("iso-8859-1") + body

        # Establish TCP Socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((self.host, self.port))
        sock.sendall(req_bytes)

        # Receive complete response stream
        raw_response = bytearray()
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            raw_response.extend(chunk)
        sock.close()

        # Parse response
        resp_data = bytes(raw_response)
        if b"\r\n\r\n" in resp_data:
            header_bytes, body_bytes = resp_data.split(b"\r\n\r\n", 1)
        else:
            header_bytes, body_bytes = resp_data, b""

        lines = header_bytes.decode("iso-8859-1", errors="replace").splitlines()
        status_code = 0
        status_line = lines[0] if lines else ""
        if lines:
            parts = lines[0].split(maxsplit=2)
            if len(parts) >= 2 and parts[1].isdigit():
                status_code = int(parts[1])

        parsed_headers = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                parsed_headers[k.strip().lower()] = v.strip()

        return status_code, parsed_headers, body_bytes, raw_request

def main():
    parser = argparse.ArgumentParser(description="Educational Raw HTTP Socket Client")
    parser.add_argument("--host", default=HTTP_HOST, help="Target HTTP server host")
    parser.add_argument("--port", type=int, default=HTTP_PORT, help="Target HTTP server port")
    parser.add_argument("--method", default="GET", help="HTTP Method (GET, HEAD, POST, etc.)")
    parser.add_argument("--path", default="/index.html", help="Resource URL path")
    args = parser.parse_args()

    client = HTTPClient(host=args.host, port=args.port)
    try:
        status_code, headers, body, raw_req = client.send_request(method=args.method, path=args.path)

        print("\n" + "=" * 60)
        print("  HTTP REQUEST TRANSMITTED (RAW TCP STREAM)")
        print("=" * 60)
        print(raw_req.strip())

        print("\n" + "=" * 60)
        print("  HTTP RESPONSE RECEIVED (PARSED BREAKDOWN)")
        print("=" * 60)
        print(f"METHOD   : {args.method.upper()}")
        print(f"PATH     : {args.path}")
        print(f"STATUS   : {status_code}")
        print("HEADERS  :")
        for k, v in headers.items():
            print(f"  {k}: {v}")

        print(f"\nBODY PREVIEW ({len(body)} bytes):")
        try:
            preview = body.decode("utf-8")
            if len(preview) > 500:
                print(preview[:500] + "\n... [TRUNCATED FOR DISPLAY] ...")
            else:
                print(preview)
        except UnicodeDecodeError:
            print(f"<Binary content: {len(body)} bytes>")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"Error communicating with HTTP server: {e}")

if __name__ == "__main__":
    main()
