# Architecture Overview

This document presents the overarching architectural designs, concurrency patterns, and socket lifecycle models implemented across the 10 Computer Networks academic projects.

---

## 1. High-Level Architectural Models

Across the collection, three primary networking architectures are developed and contrasted:

```mermaid
graph TD
    subgraph Model1["1. Multi-Threaded Client-Server (Projects 01, 03)"]
        C1[Client 1] -->|TCP Connection| S1[Master Listener Socket]
        C2[Client 2] -->|TCP Connection| S1
        S1 -->|accept| T1[Worker Thread 1]
        S1 -->|accept| T2[Worker Thread 2]
    end

    subgraph Model2["2. Application-Level Datagram ARQ (Project 02)"]
        US[UDP Sender] -->|Datagram SEQ#n| UR[UDP Receiver]
        UR -->|Datagram ACK#n| US
        US -.->|Simulated Drop / Timeout| US
    end

    subgraph Model3["3. I/O Multiplexed Server (Project 08)"]
        CA[Client A] -->|Non-blocking Socket| SEL[Selectors Event Loop]
        CB[Client B] -->|Non-blocking Socket| SEL
        CC[Client C] -->|Non-blocking Socket| SEL
        SEL -->|Ready for READ/WRITE| DISP[Dispatcher & Message Broker]
    end
```

---

## 2. Standard Socket Lifecycle

### TCP Socket State Machine (RFC 793)
Implemented in Projects 01, 03, 08, 09, 10:

```mermaid
sequenceDiagram
    autonumber
    participant Server
    participant Client

    Note over Server: socket(AF_INET, SOCK_STREAM)
    Note over Server: setsockopt(SO_REUSEADDR)
    Note over Server: bind((host, port))
    Note over Server: listen(backlog)

    Note over Client: socket(AF_INET, SOCK_STREAM)
    Client->>Server: SYN (connect)
    Server-->>Client: SYN-ACK
    Client->>Server: ACK (Connection Established)
    Note over Server: accept() returns (conn, addr)

    Client->>Server: sendall(Data Stream)
    Server->>Server: recv(buffer_size)
    Server-->>Client: sendall(Response Stream)

    Client->>Server: FIN (close / shutdown)
    Server-->>Client: ACK
    Server->>Client: FIN
    Client-->>Server: ACK
    Note over Server,Client: Sockets Closed (TIME_WAIT)
```

### UDP Socket State Machine (RFC 768)
Implemented in Projects 02, 04:

```mermaid
sequenceDiagram
    autonumber
    participant Client / Sender
    participant Server / Receiver

    Note over Server: socket(AF_INET, SOCK_DGRAM)
    Note over Server: bind((host, port))

    Note over Client: socket(AF_INET, SOCK_DGRAM)
    Client->>Server: sendto(Datagram, (server_ip, port))
    Note over Server: recvfrom(buf_size) -> (data, client_addr)
    Server-->>Client: sendto(ACK / Response, client_addr)
```

---

## 3. Data Framing and Serialization Strategies

TCP provides an unstructured byte stream with no intrinsic record delimiters. A common pitfall in academic networking projects is assuming `recv(1024)` always yields exactly one complete message. Our projects employ explicit framing protocols:

1. **Length-Prefixed Framing (Project 01 & 08):**
   - Each frame begins with a fixed 4-byte big-endian unsigned integer (`struct.pack("!I", length)`) representing the byte length of the ensuing payload.
   - The receiver performs exact-length buffered reading until the expected payload is received in full.
2. **HTTP/1.1 Delimited Framing (Project 03):**
   - Uses `\r\n\r\n` (CRLF CRLF) delimiters to identify the termination of HTTP headers, followed by `Content-Length` bounded reads for message bodies.
3. **Structured Binary Datagram Framing (Project 02):**
   - Encodes a binary packet header using Python `struct` containing:
     - `Transfer_ID` (16-bit unsigned integer)
     - `Sequence_Number` (32-bit unsigned integer)
     - `Total_Packets` (32-bit unsigned integer)
     - `Payload_Length` (16-bit unsigned integer)
     - `Checksum` (32-bit CRC32 / Adler32 integer)
     - Variable-length raw binary payload (up to 1400 bytes, avoiding IP fragmentation).

---

## 4. Error Handling and Resilience Architecture

All projects implement structured exception hierarchies for network anomalies:

- `socket.error` / `OSError`: Trapped during `bind()` when a port is already bound, raising user-friendly warnings (`Address already in use`).
- `socket.timeout`: Trapped in non-blocking or timed socket operations to prevent indefinite deadlocks.
- `ConnectionResetError` / `BrokenPipeError`: Detected when a remote peer abruptly drops the connection, triggering resource cleanup without crashing the server.
- Context managers (`with socket.socket(...)`) and `finally:` blocks to guarantee socket descriptor deallocation.
