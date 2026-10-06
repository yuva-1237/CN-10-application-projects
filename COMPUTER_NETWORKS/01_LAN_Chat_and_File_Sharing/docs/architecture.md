# Project 01: LAN Chat and File Sharing — Architecture

## 1. Architectural Overview

Project 01 implements a multi-threaded, connection-oriented client-server communication system over TCP/IP. It allows multiple heterogeneous client nodes situated on a Local Area Network (LAN) to exchange text messages (broadcast and unicast) and transfer binary files of arbitrary size with end-to-end cryptographic checksum verification.

```mermaid
graph TD
    subgraph LAN_Network["Local Area Network (LAN)"]
        Server["LAN Chat Server<br>(Port 5001)"]
        ClientA["Client A<br>(Alice)"]
        ClientB["Client B<br>(Bob)"]
        ClientC["Client C<br>(Charlie)"]

        ClientA -->|TCP Handshake & Frames| Server
        ClientB -->|TCP Handshake & Frames| Server
        ClientC -->|TCP Handshake & Frames| Server
    end
```

---

## 2. Core Components

1. **`app/server.py` (`ChatServer`):**
   - Creates a master listening socket (`socket.AF_INET`, `socket.SOCK_STREAM`).
   - Uses `SO_REUSEADDR` to prevent port binding locks after restart.
   - Listens on `0.0.0.0` to accept connections across physical LAN network adapters.
   - Spawns an isolated background daemon worker thread for every connected client (`_handle_client`).
   - Maintains a thread-synchronized dictionary mapping `username -> (socket, address)`.
   - Routes broadcast frames to all connected sockets and private frames to target sockets.

2. **`app/client.py` (`ChatClient`):**
   - Connects to the server's LAN IP and assigned port.
   - Registers a unique username during the initial handshake.
   - Spawns a background listener thread (`_listen_loop`) that continuously parses incoming network frames without blocking user CLI input.
   - Streams outbound files in discrete 32 KB blocks to prevent buffer exhaustion.

3. **`app/protocol.py` (Framing Engine):**
   - Solves the fundamental TCP "stream without boundaries" problem.
   - Encodes a 4-byte big-endian length prefix (`!I`) specifying the length of a JSON control header, followed by a 4-byte binary payload length prefix, followed by the optional binary payload.
   - Uses an exact-byte receiver (`recv_exact`) to reassemble fragmented TCP segments reliably.

---

## 3. Communication Sequence

### Client Connection and Registration
```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Server

    Note over Server: bind(('0.0.0.0', 5001)), listen()
    Client->>Server: TCP SYN
    Server-->>Client: TCP SYN-ACK
    Client->>Server: TCP ACK
    Client->>Server: Frame: {"type": "register", "sender": "Alice"}
    Note over Server: Validate uniqueness in clients map
    Server-->>Client: Frame: {"type": "ack", "message": "Welcome, Alice!"}
    Server-->>Server: Broadcast {"type": "system", "message": "User 'Alice' joined"}
```

### File Streaming Sequence
```mermaid
sequenceDiagram
    autonumber
    participant Alice (Sender)
    participant Server
    participant Bob (Receiver)

    Note over Alice (Sender): Compute SHA-256(file)
    Alice (Sender)->>Server: Frame: {"type": "file_meta", "filename": "doc.pdf", "filesize": 1048576, "sha256": "..."}
    Server->>Bob (Receiver): Forward file_meta Frame
    loop For each 32KB Chunk
        Alice (Sender)->>Server: Frame: {"type": "file_chunk", "filename": "doc.pdf"} + [Binary Bytes]
        Server->>Bob (Receiver): Forward Chunk + [Binary Bytes]
    end
    Alice (Sender)->>Server: Frame: {"type": "file_complete", "filename": "doc.pdf", "sha256": "..."}
    Server->>Bob (Receiver): Forward file_complete Frame
    Note over Bob (Receiver): Reassemble chunks & verify SHA-256 match
```

---

## 4. Error Handling and Edge Cases

- **Address In Use:** Trapped during `bind()` with clear guidance to wait for socket teardown or select an alternate port.
- **Premature Remote Disconnect:** `recv_exact()` raises `ConnectionError` on encountering zero-length reads, prompting the server to clean up client registries and alert peer clients.
- **Concurrent Dictionary Access:** Sychronized with a `threading.Lock()` to prevent race conditions during simultaneous user logins or logouts.
- **Transmission Integrity:** Reassembled files that fail SHA-256 verification are flagged as corrupted and not endorsed for execution.
