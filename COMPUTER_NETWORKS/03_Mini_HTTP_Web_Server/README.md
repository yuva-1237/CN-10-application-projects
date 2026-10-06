# Mini HTTP Web Server & Client

## 1. Objective
To build a functional HTTP/1.1 web server and companion diagnostic client using low-level TCP stream sockets in Python, illustrating request tokenization, header extraction, MIME negotiation, status codes, and the complete HTTP request-response cycle without third-party frameworks.

## 2. Problem Statement
Modern web developers commonly use high-level web frameworks (Flask, Django, Express, Spring) where socket primitives and raw protocol frames are entirely obscured. Students frequently fail to grasp how an HTTP request is structured over a transport stream, how CRLF delimiters function, or how web browsers communicate with network sockets. This project directly addresses this gap by implementing an RFC-compliant HTTP engine purely using standard Python `socket` calls.

## 3. Computer Networks Concepts Used
* **Application Layer Protocol (OSI Layer 7):** Hypertext Transfer Protocol (HTTP/1.1 per RFC 2616 / RFC 7230).
* **Transport Layer (OSI Layer 4):** TCP stream communication (`SOCK_STREAM`), handling three-way handshakes and connection teardowns.
* **HTTP Grammar & Framing:** Parsing Request-Line (`Method`, `URI`, `HTTP-Version`), headers (`Key: Value`), and body delimiters (`\r\n\r\n`).
* **HTTP Status Codes:** `200 OK`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `405 Method Not Allowed`.
* **MIME Media Types:** Mapping file extensions to `Content-Type` headers (`text/html`, `text/css`, `application/json`, `image/png`).
* **Security & Path Sanitization:** Guarding against directory traversal attacks via path canonicalization.

## 4. Protocol Used
* **Application:** HTTP/1.1
* **Transport:** TCP over IPv4 (`AF_INET`, `SOCK_STREAM`), standard port `8080`.

## 5. Architecture
* **`app/server.py`:** Listens on port 8080, accepts TCP connections, assigns client sockets to worker threads, reads raw HTTP requests, calls `http_parser.py`, resolves target files in `public/`, and transmits RFC-compliant HTTP response bytes.
* **`app/client.py`:** Diagnostic TCP client that constructs raw ASCII HTTP requests, sends them over a TCP socket, and decomposes the received raw response bytes into status code, headers, and body previews.
* **`public/`:** Static web directory containing HTML pages (`index.html`, `about.html`, `404.html`), stylesheet (`styles.css`), and an API endpoint (`api/status.json`).

```
Browser / HTTP Client                 Mini HTTP Server (:8080)
         |                                       |
         |---------- TCP SYN ------------------->|
         |<--------- TCP SYN-ACK ----------------|
         |---------- TCP ACK ------------------->|
         |                                       |
         |---- GET /index.html HTTP/1.1 -------->| [Parses Request Line & Headers]
         |     Host: 127.0.0.1:8080              | [Resolves MIME: text/html]
         |     \r\n\r\n                          | [Reads public/index.html]
         |                                       |
         |<--- HTTP/1.1 200 OK ------------------|
         |     Content-Type: text/html           |
         |     Content-Length: 1042              |
         |     \r\n\r\n                          |
         |     <!DOCTYPE html>...                |
         |                                       |
         |<--- TCP FIN (Connection: close) ------|
```

## 6. System Requirements
* **Operating System:** Cross-platform (Windows, Linux, macOS).
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only.

## 7. Technologies Used
* `socket`: Direct TCP stream socket programming.
* `threading`: Concurrent client request handling.
* `urllib.parse`: URL decoding and query string stripping.
* `email.utils`: Formatting HTTP IMF-fixdate timestamps per RFC 7231.
* `pytest`: Automated test framework.

## 8. Project Structure
```
03_Mini_HTTP_Web_Server/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── http_parser.py
│   ├── server.py
│   ├── client.py
│   └── utils.py
├── public/
│   ├── index.html
│   ├── about.html
│   ├── 404.html
│   ├── styles.css
│   └── api/
│       └── status.json
├── tests/
│   └── test_basic.py
├── docs/
│   ├── architecture.md
│   └── viva.md
└── logs/
```

## 9. Installation
```bash
cd COMPUTER_NETWORKS/03_Mini_HTTP_Web_Server
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Start the Mini HTTP Server
```bash
python app/server.py --port 8080
```

### Step 2: Open in Any Web Browser
Open your browser and navigate to:
```
http://localhost:8080
```
Browse between **Home**, **About Protocol**, **JSON API**, and test the **404 Not Found** page.

### Step 3: Run the Educational Diagnostic Client
In a separate terminal window:
```bash
python app/client.py --method GET --path /index.html
python app/client.py --method HEAD --path /index.html
python app/client.py --method GET --path /api/status.json
python app/client.py --method POST --path /index.html
```

## 11. How the Network Communication Works
1. **TCP Handshake:** Browser or client connects to `127.0.0.1:8080`.
2. **Request Framing:** Client sends ASCII text terminated by `\r\n\r\n`.
3. **Parsing:** Server splits headers, validates method (`GET` or `HEAD`), and normalizes path.
4. **MIME Negotiation:** Based on file extension (`.html`, `.css`, `.json`), server sets `Content-Type`.
5. **Streaming Response:** Server writes status line, response headers, empty line delimiter, and file binary bytes.
6. **Teardown:** Server closes socket per `Connection: close` header.

## 12. Example Input
```bash
python app/client.py --method GET --path /api/status.json
```

## 13. Example Output
```
============================================================
  HTTP REQUEST TRANSMITTED (RAW TCP STREAM)
============================================================
GET /api/status.json HTTP/1.1
Host: 127.0.0.1:8080
User-Agent: AcademicHTTPClient/1.0 (Python Socket)
Accept: */*
Connection: close

============================================================
  HTTP RESPONSE RECEIVED (PARSED BREAKDOWN)
============================================================
METHOD   : GET
PATH     : /api/status.json
STATUS   : 200
HEADERS  :
  server: MiniHTTPServer/1.0 (Python/CustomSocket)
  date: Tue, 06 Oct 2026 04:00:00 GMT
  content-type: application/json; charset=utf-8
  content-length: 348
  connection: close

BODY PREVIEW (348 bytes):
{
  "server": "Mini HTTP Web Server",
  "status": "ONLINE",
  "protocol": "HTTP/1.1",
  "transport": "TCP",
  "layer": "Application Layer (OSI Layer 7)",
  "features": [
    "Raw TCP socket implementation",
    "RFC 2616 tokenized header parsing",
    "MIME content negotiation",
    "GET and HEAD method handlers",
    "Safe filesystem traversal protection"
  ],
  "author": "Computer Networks Student"
}
============================================================
```

## 14. Testing
Run the 5 automated unit and protocol compliance tests:
```bash
pytest tests/test_basic.py -v
```
Validates TCP socket binding, GET method 200 OK delivery, HEAD method header inspection with empty body, 404 Not Found error handling, and 405 Method Not Allowed rejection for invalid HTTP verbs.

## 15. Real-World Applications
* Foundational architecture behind production web servers like Apache HTTP Server and Nginx.
* Embedded web servers for IoT edge devices (e.g. Raspberry Pi, ESP32 web configuration portals).
* Internal diagnostic micro-services and health-check endpoints.

## 16. Limitations
* Operates on HTTP/1.1 without TLS encryption (plain HTTP).
* Implements a subset of HTTP methods (`GET` and `HEAD`). `POST`, `PUT`, `DELETE` are intentionally rejected with 405 per scope.

## 17. Future Enhancements
* Persistent connection pooling (`Connection: keep-alive`).
* TLS wrapping via standard Python `ssl` module to create an HTTPS server.
* Chunked Transfer Encoding (`Transfer-Encoding: chunked`).

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What layer of the OSI model does HTTP belong to, and which transport protocol does it use?
2. Why is HTTP called a "stateless" protocol?
3. What is the anatomy of an HTTP request?
4. What is the difference between the GET and HEAD methods?
5. What is the significance of the `Content-Length` header?
6. What is a MIME type and why is `Content-Type` essential?
7. What are the primary HTTP status code families?
8. What character sequence delimits HTTP headers?
9. How does the server prevent Directory Traversal attacks?
10. How does a web browser interact with this server?
