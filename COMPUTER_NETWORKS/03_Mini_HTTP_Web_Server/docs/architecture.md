# Project 03: Mini HTTP Web Server — Architecture

## 1. Architectural Overview

Project 03 implements a standards-compliant Hypertext Transfer Protocol (HTTP/1.1 per RFC 2616 / RFC 7230) server and client from foundational primitives using low-level TCP stream sockets. It eliminates high-level framework wrappers (e.g. Flask, Django, FastAPI) in order to clearly expose the raw socket mechanics: accepting a connection, parsing ASCII text headers separated by Carriage Return Line Feeds (`\r\n`), resolving MIME types, and streaming binary HTTP responses.

```mermaid
graph TD
    Browser["Web Browser / HTTP Client"] -->|1. TCP 3-Way Handshake<br>SYN -> SYN-ACK -> ACK| Sock[TCP Listener Socket :8080]
    Sock -->|2. accept| Worker[Daemon Worker Thread]
    Browser -->|3. Raw ASCII Stream<br>GET /index.html HTTP/1.1| Worker
    Worker -->|4. Request Parser| P[http_parser.py]
    P -->|Method, Path, Headers| Router{File Router}
    Router -->|Valid File| Read[Read File + MIME Lookup]
    Router -->|Invalid File| Err404[404 Not Found Generator]
    Router -->|Method != GET/HEAD| Err405[405 Method Not Allowed]
    Read --> Build[HTTPResponse.build]
    Err404 --> Build
    Err405 --> Build
    Build -->|5. Binary Stream<br>HTTP/1.1 200 OK ...| Browser
    Worker -->|6. TCP FIN / close| Browser
```

---

## 2. Request and Response Framing

### HTTP/1.1 Request Wire Format
```
+-------------------------------------------------------+
| METHOD SP Request-URI SP HTTP-Version CRLF            |  <- Request Line
+-------------------------------------------------------+
| Header-Name: Header-Value CRLF                        |  <- Headers
| Header-Name: Header-Value CRLF                        |
+-------------------------------------------------------+
| CRLF (\r\n)                                           |  <- Empty line delimiter
+-------------------------------------------------------+
| Optional Request Body (e.g. POST data)                |  <- Body
+-------------------------------------------------------+
```

### HTTP/1.1 Response Wire Format
```
+-------------------------------------------------------+
| HTTP-Version SP Status-Code SP Reason-Phrase CRLF     |  <- Status Line
+-------------------------------------------------------+
| Server: MiniHTTPServer/1.0 CRLF                       |  <- Response Headers
| Date: Tue, 06 Oct 2026 04:00:00 GMT CRLF              |
| Content-Type: text/html; charset=utf-8 CRLF           |
| Content-Length: 1245 CRLF                             |
| Connection: close CRLF                                |
+-------------------------------------------------------+
| CRLF (\r\n)                                           |  <- Empty line delimiter
+-------------------------------------------------------+
| Response Body Stream (HTML, CSS, JSON, Binary Image)  |  <- Entity Body
+-------------------------------------------------------+
```

---

## 3. Communication Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Client as Web Browser / Client
    participant Server as Mini HTTP Server (:8080)

    Note over Client,Server: Transport Layer Handshake
    Client->>Server: TCP SYN
    Server-->>Client: TCP SYN-ACK
    Client->>Server: TCP ACK

    Note over Client,Server: Application Layer Request
    Client->>Server: GET /index.html HTTP/1.1\r\nHost: localhost:8080\r\n\r\n
    Note over Server: Parse Request-Line & Headers
    Note over Server: Check Path & Determine MIME (text/html)
    Note over Server: Read public/index.html

    Note over Client,Server: Application Layer Response
    Server-->>Client: HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 1042\r\n\r\n<!DOCTYPE html>...

    Note over Client,Server: Connection Teardown
    Server->>Client: TCP FIN
    Client-->>Server: TCP ACK
```

---

## 4. Security Considerations: Directory Traversal Protection

A critical vulnerability in hand-crafted HTTP servers is directory traversal (e.g., `GET /../../../../etc/passwd HTTP/1.1` or `GET /..%2f..%2fWindows/win.ini HTTP/1.1`).
This server implements strict path canonicalization:
```python
target_file = (self.public_dir / req_rel).resolve()
if not str(target_file).startswith(str(self.public_dir)):
    # Prohibit directory traversal with 403 Forbidden
```
Any request attempting to escape the designated `public/` directory root is immediately trapped and answered with `403 Forbidden`.
