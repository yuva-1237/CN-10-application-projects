# LAN Chat and File Sharing System

## 1. Objective
To design and construct a functional, multi-client, bidirectional communication and file transmission system across a Local Area Network (LAN) using low-level TCP/IP stream sockets in Python.

## 2. Problem Statement
Distributed devices on a local enterprise or campus network frequently need to exchange real-time textual data and transfer files without relying on external internet servers or third-party cloud brokers. The challenge is to maintain persistent, ordered, in-sequence delivery between multiple concurrent users, isolate private communications, stream binary files of arbitrary size without memory exhaustion, and guarantee data integrity across transmission boundaries.

## 3. Computer Networks Concepts Used
* **Local Area Network (LAN):** Interconnection of computing nodes within a localized physical scope (RFC 1918 private IPv4 spaces).
* **TCP/IP Protocol Suite:** Transport Layer reliable byte-stream transport.
* **Client-Server Architecture:** Centralized coordination server facilitating connection pooling, client discovery, and message routing.
* **IP Addressing & Port Multiplexing:** Binding sockets to specific transport ports and addressing endpoints via IPv4.
* **Socket Lifecycle:** Explicit sequence of `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `sendall()`, `recv()`, and `close()`.
* **Framing & Packet Serialization:** Prefixing data streams with 4-byte big-endian length headers to resolve TCP packet fragmentation and concatenation.
* **Data Integrity:** Verification of transmitted binaries via SHA-256 cryptographic hashing.

## 4. Protocol Used
* **Transport:** Transmission Control Protocol (TCP) over IPv4 (`AF_INET`, `SOCK_STREAM`).
* **Application-Layer Framing:** Custom binary/JSON framing protocol:
  `[4-byte Header Length][JSON Control Header][4-byte Binary Length][Raw Binary Stream]`

## 5. Architecture
The system adopts a centralized, multi-threaded client-server architecture:
* **Server:** Listens on port `5001` (by default on all interfaces `0.0.0.0`). For each accepted client, it allocates a dedicated daemon worker thread. It maintains a thread-safe registry of connected users.
* **Client:** Connects to the server, exchanges registration credentials, and spawns an asynchronous background thread dedicated to receiving incoming server frames while the main thread manages user interactions.

```
Client A (Alice) ───[TCP]───┐
Client B (Bob)   ───[TCP]───┼──> [TCP Server: Port 5001]
Client C (Carol) ───[TCP]───┘
```

## 6. System Requirements
* **Operating System:** Windows 10/11, Linux (Ubuntu, Debian, Fedora), or macOS.
* **Python Runtime:** Python 3.11+
* **Network Hardware:** Standard Ethernet NIC or 802.11 Wi-Fi interface connected to a common LAN or local loopback (`127.0.0.1`).

## 7. Technologies Used
* `socket`: Low-level network interface.
* `threading`: Multi-threaded client concurrency.
* `struct`: Binary packing and unpacking of network byte orders (`!I`).
* `json`: Structured control headers.
* `hashlib`: SHA-256 checksum calculation.
* `pytest`: Test automation.

## 8. Project Structure
```
01_LAN_Chat_and_File_Sharing/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── protocol.py
│   ├── server.py
│   ├── client.py
│   └── utils.py
├── tests/
│   └── test_basic.py
├── docs/
│   ├── architecture.md
│   └── viva.md
├── data/
│   ├── uploads/
│   └── downloads/
└── logs/
```

## 9. Installation
Clone the repository or navigate to this folder:
```bash
cd COMPUTER_NETWORKS/01_LAN_Chat_and_File_Sharing
# Virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Start the Central Server
```bash
python app/server.py --port 5001
```
*The server will display its local LAN IP address (e.g. `192.168.1.15` or `127.0.0.1`).*

### Step 2: Connect Clients
Open another terminal (or multiple terminals/machines on the same LAN):
```bash
python app/client.py --host 127.0.0.1 --port 5001 --user Alice
```
In another window:
```bash
python app/client.py --host 127.0.0.1 --port 5001 --user Bob
```

### Step 3: Interactive Commands
* `/list`: View all currently connected online users.
* `<text>`: Broadcast a message to all users.
* `/msg <username> <text>`: Send a private direct message.
* `/sendfile <filepath> [recipient]`: Send a file to everyone or a specific user.
* `/quit`: Disconnect cleanly.

## 11. How the Network Communication Works
1. **Three-Way Handshake:** Initiated when `client.connect()` sends a TCP `SYN`. Server accepts with `SYN-ACK`, client replies with `ACK`.
2. **Registration Frame:** Client transmits a 4-byte packed length followed by a JSON payload `{"type": "register", "sender": "Alice"}`.
3. **Registry Update:** Server checks for username collisions, adds the connection descriptor to its internal map, and broadcasts a system join alert.
4. **File Transmission:** The sender reads the file in 32 KB chunks, emitting a `file_meta` frame containing the total size and SHA-256 hash, sequentially streaming `file_chunk` binary frames, and concluding with `file_complete`.
5. **Reassembly & Hash Validation:** The receiving client reconstructs chunks sequentially on disk, computes its local SHA-256 hash, and compares it to the header hash.

## 12. Example Input
```
> Hello LAN users!
> /msg Bob Are you working on the networking assignment?
> /sendfile data/sample_report.pdf Bob
```

## 13. Example Output
```
[2026-10-06 09:20:00] [INFO] [LAN_Server]: Client registered: 'Alice' from ('127.0.0.1', 52310)
[2026-10-06 09:20:05] [INFO] [LAN_Server]: Client registered: 'Bob' from ('127.0.0.1', 52314)
[Alice (Broadcast)]: Hello LAN users!
[PRIVATE from Alice]: Are you working on the networking assignment?
[FILE INCOMING]: Receiving 'sample_report.pdf' (1.45 MB) from Alice...
[FILE COMPLETE]: 'sample_report.pdf' saved to data/downloads/recvd_1728200000_sample_report.pdf [Checksum Verified: SHA-256 OK]
```

## 14. Testing
Run the automated test suite with verbose reporting:
```bash
pytest tests/test_basic.py -v
```
All 5 comprehensive test cases validate server startup, protocol framing, client registration, multi-client routing, and file transmission integrity.

## 15. Real-World Applications
* Local enterprise communication systems operating in air-gapped secure facilities.
* Peer-to-peer and client-server file synchronization tools (e.g. AirDrop, LANdrop).
* Multiplayer game lobby chat and asset replication servers.

## 16. Limitations
* A thread-per-client model creates kernel thread overhead when scaling to thousands of concurrent users (addressed in Project 08 using I/O multiplexing).
* Traffic is unencrypted (raw plain text). For production environments over untrusted WANs, TLS wrappers (`ssl` module) should be introduced.

## 17. Future Enhancements
* Implementation of Transport Layer Security (TLS 1.3) wrapping over the TCP sockets.
* Multi-threaded chunk transfers with pause and resume capabilities.
* Terminal GUI using `curses` or `rich`.

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is a socket and which socket type is used in this project?
2. Why is TCP preferred over UDP for file sharing and chat applications?
3. What is the purpose of `SO_REUSEADDR`?
4. What is the "TCP sticky packet" or stream boundary problem, and how does your project solve it?
5. What does `bind()` do in socket programming?
6. What is the difference between binding to `127.0.0.1` vs `0.0.0.0`?
7. Why is multi-threading necessary on the server?
8. How is file integrity verified across the network?
9. What happens when a client disconnects abruptly?
10. How does private messaging differ from broadcast messaging in this architecture?
