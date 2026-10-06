"""HTTP/1.1 Request and Response protocol parser."""
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

STATUS_PHRASES = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

@dataclass
class HTTPRequest:
    method: str
    path: str
    raw_path: str
    version: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    @classmethod
    def parse(cls, raw_data: bytes) -> Optional["HTTPRequest"]:
        """Parse raw TCP stream into structured HTTPRequest."""
        try:
            # Split headers and body at double CRLF
            if b"\r\n\r\n" in raw_data:
                header_part, body_part = raw_data.split(b"\r\n\r\n", 1)
            elif b"\n\n" in raw_data:
                header_part, body_part = raw_data.split(b"\n\n", 1)
            else:
                header_part, body_part = raw_data, b""

            lines = header_part.decode("iso-8859-1").splitlines()
            if not lines:
                return None

            # Request Line: METHOD PATH HTTP/VERSION
            request_line = lines[0].strip()
            tokens = request_line.split()
            if len(tokens) != 3:
                return None

            method, raw_path, version = tokens
            method = method.upper()

            # Sanitize path: URL decode and prevent directory traversal
            clean_path = urllib.parse.unquote(raw_path.split("?")[0])
            if clean_path == "" or clean_path == "/":
                clean_path = "/index.html"

            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            return cls(
                method=method,
                path=clean_path,
                raw_path=raw_path,
                version=version,
                headers=headers,
                body=body_part
            )
        except Exception:
            return None

class HTTPResponse:
    @staticmethod
    def build(
        status_code: int,
        content_type: str = "text/html; charset=utf-8",
        body: bytes = b"",
        extra_headers: Optional[Dict[str, str]] = None,
        server_name: str = "MiniHTTPServer/1.0",
        date_str: str = ""
    ) -> bytes:
        """Construct raw RFC-compliant HTTP/1.1 response bytes."""
        phrase = STATUS_PHRASES.get(status_code, "Unknown")
        headers = {
            "Server": server_name,
            "Date": date_str,
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "Connection": "close",
        }
        if extra_headers:
            headers.update(extra_headers)

        header_lines = [f"HTTP/1.1 {status_code} {phrase}"]
        for k, v in headers.items():
            header_lines.append(f"{k}: {v}")

        header_bytes = "\r\n".join(header_lines).encode("iso-8859-1") + b"\r\n\r\n"
        return header_bytes + body
