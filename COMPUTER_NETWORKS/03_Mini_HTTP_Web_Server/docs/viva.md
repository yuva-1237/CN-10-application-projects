# Project 03: Mini HTTP Web Server — Viva Questions & Answers

### Q1: What layer of the OSI model does HTTP belong to, and which transport protocol does it use?
**Answer:** HTTP belongs to Layer 7 (Application Layer). It operates on top of the Transmission Control Protocol (TCP) at Layer 4 (Transport Layer) to ensure reliable, in-sequence message exchange.

### Q2: Why is HTTP called a "stateless" protocol?
**Answer:** Each HTTP request is handled independently by the server. The server retains no session state or memory of prior interactions between the same client unless explicit state tokens (such as HTTP cookies or authorization tokens) are supplied.

### Q3: What is the anatomy of an HTTP request?
**Answer:** An HTTP request comprises three parts:
1. **Request Line:** Method, Request URI, and HTTP Version (`GET /index.html HTTP/1.1`).
2. **Headers:** Key-value pairs ending with a double CRLF (`\r\n\r\n`).
3. **Optional Message Body:** Payload bytes (e.g. JSON, form data in POST/PUT).

### Q4: What is the difference between the GET and HEAD methods?
**Answer:** `GET` retrieves the complete representation of the requested resource (headers plus response body). `HEAD` requests the identical headers that a `GET` would produce, but the server must omit the entity body entirely. This is used for caching checks and header inspection.

### Q5: What is the significance of the `Content-Length` header?
**Answer:** It informs the receiving socket how many raw octets (bytes) are in the message body. In persistent connections, this tells the client exactly when one response ends and the next begins.

### Q6: What is a MIME type and why is `Content-Type` essential?
**Answer:** Multipurpose Internet Mail Extensions (MIME) describes the media format of the payload (e.g., `text/html`, `image/png`, `application/json`). Without it, a web browser would not know whether to render HTML, style CSS, or execute JavaScript.

### Q7: What are the primary HTTP status code families?
**Answer:**
- `1xx`: Informational
- `2xx`: Success (e.g. 200 OK)
- `3xx`: Redirection (e.g. 301 Moved Permanently)
- `4xx`: Client Error (e.g. 400 Bad Request, 404 Not Found, 405 Method Not Allowed)
- `5xx`: Server Error (e.g. 500 Internal Server Error)

### Q8: What character sequence delimits HTTP headers?
**Answer:** A carriage return followed by a line feed (`\r\n`, ASCII `0x0D 0x0A`). Headers terminate when an empty line is encountered (`\r\n\r\n`).

### Q9: How does the server prevent Directory Traversal attacks (e.g., `GET /../../etc/passwd`)?
**Answer:** The server canonicalizes the requested file path using `Path.resolve()` and checks that the resolved absolute path strictly begins with the root `public/` web directory string. If it points outside, a `403 Forbidden` status is returned.

### Q10: How does a web browser interact with this server?
**Answer:** The browser performs DNS resolution to obtain the server's IP, initiates a TCP 3-way handshake on port 8080, sends an ASCII `GET /index.html HTTP/1.1` request, parses the incoming `HTTP/1.1 200 OK` stream, requests linked assets (`styles.css`), and closes the TCP connection.
