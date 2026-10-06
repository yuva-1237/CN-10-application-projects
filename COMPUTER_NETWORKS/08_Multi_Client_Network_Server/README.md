# Multi-Client Network Server

## 1. Objective
To construct a high-concurrency, asynchronous TCP network server using non-blocking sockets and I/O multiplexing (`selectors` module in Python), demonstrating simultaneous client management, event-driven socket dispatch, broadcast/private messaging, and real-time connection telemetry.

## 2. Problem Statement
Traditional multi-threaded servers allocate one dedicated operating system thread per connected client socket. As concurrent connections grow to hundreds or thousands, thread context switching and stack allocation severely degrade system performance. This project proves how an event-driven I/O multiplexing server can manage multiple concurrent client connections on a single thread without blocking.

## 3. Computer Networks Concepts Used
* **Transport Layer (OSI Layer 4):** TCP stream connections (`SOCK_STREAM`).
* **Non-Blocking Sockets:** `setblocking(False)` preventing thread starvation.
* **I/O Multiplexing:** Operating system event notification (`epoll`, `kqueue`, `select` via `selectors.DefaultSelector`).
* **Event Dispatching:** `EVENT_READ` and `EVENT_WRITE` lifecycle coordination.
* **Message Framing:** Length-prefixed binary frames preventing TCP sticky packet corruption.
* **Concurrency Telemetry:** Active connections, peak concurrent users, and message throughput tracking.

## 4. Protocol Used
* **Transport:** TCP over IPv4 (`AF_INET`, `SOCK_STREAM`), default port `5008`.
* **Framing:** Length-prefixed JSON protocol frames.

## 5. Architecture
* **`app/server.py` (`MultiClientServer`):** Runs an event loop polling non-blocking sockets, handles new connections without spawning new threads, and buffers reads and writes.
* **`app/client.py` (`MultiClient`):** Interactive terminal client and automated multi-client swarm generator for load testing.
* **`app/utils.py`:** Buffer reassembly and server telemetry trackers (`ServerStats`).

```
Client 1 (Non-blocking) ──┐
Client 2 (Non-blocking) ──┼──> [Selectors Event Loop: DefaultSelector]
Client 3 (Non-blocking) ──┤          |
Client 4 (Non-blocking) ──┤     (EVENT_READ / EVENT_WRITE)
Client 5 (Non-blocking) ──┘          v
                             [Message Router & Telemetry]
```

## 6. System Requirements
* **Operating System:** Cross-platform (Linux, Windows, macOS).
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only.

## 7. Technologies Used
* `selectors.DefaultSelector`: Platform-optimized asynchronous I/O multiplexer.
* `socket`: Non-blocking stream socket configuration.
* `struct`: 4-byte network byte-order length framing.
* `pytest`: Test automation.

## 8. Project Structure
```
08_Multi_Client_Network_Server/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── server.py
│   ├── client.py
│   └── utils.py
├── tests/
│   └── test_basic.py
├── docs/
│   ├── architecture.md
│   └── viva.md
└── logs/
```

## 9. Installation
```bash
cd COMPUTER_NETWORKS/08_Multi_Client_Network_Server
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Start the Multi-Client Server
```bash
python app/server.py --port 5008
```

### Step 2: Run the Automated Concurrent Swarm (5+ simultaneous clients)
In a second terminal window:
```bash
python app/client.py --port 5008 --swarm 5
```
*Spawns 5 simultaneous clients concurrently, registers each, verifies multi-client broadcast, and queries server statistics.*

### Step 3: Connect Interactive Clients Manually
```bash
python app/client.py --port 5008 --user Alice
python app/client.py --port 5008 --user Bob
```
Commands inside interactive client:
- `/stats`: View server active connections and message totals.
- `/msg <user> <message>`: Send a private direct message.
- `/quit`: Disconnect.

## 11. How the Network Communication Works
1. **Selector Registration:** Listener socket is registered with `selectors.EVENT_READ`.
2. **Event Polling:** `selector.select()` waits until the OS reports a readable socket.
3. **Accepting Connection:** Newly accepted client socket is marked non-blocking (`conn.setblocking(False)`) and registered for `EVENT_READ`.
4. **Buffered Streaming:** Incoming bytes are appended to the client's `in_buffer`. Once a full message is decoded, it is processed.
5. **Output Queueing & Write Readiness:** Outbound messages are placed into `out_buffer` and the socket is registered for `EVENT_WRITE`. When the OS send buffer is ready, data is flushed.

## 12. Example Input
```bash
python app/client.py --swarm 5
```

## 13. Example Output
```
=================================================================
  LAUNCHING CONCURRENT CLIENT SWARM (5 SIMULTANEOUS CLIENTS)
=================================================================
[1/5] Connected & Registered 'Swarm_Bot_1'
[2/5] Connected & Registered 'Swarm_Bot_2'
[3/5] Connected & Registered 'Swarm_Bot_3'
[4/5] Connected & Registered 'Swarm_Bot_4'
[5/5] Connected & Registered 'Swarm_Bot_5'

All 5 clients actively connected simultaneously.
Broadcasting test payload from Swarm_Bot_1 to all peers...

=================================================================
  SERVER TELEMETRY REPORT
=================================================================
Active Connected Clients : 5
Total Connections Logged : 5
Peak Concurrent Clients  : 5
Messages Processed       : 6 recv / 5 sent
=================================================================
Tearing down client swarm...
Swarm simulation complete.
```

## 14. Testing
Run the 5 automated unit and load tests:
```bash
pytest tests/test_basic.py -v
```
Validates non-blocking server startup, single client registration, 5 simultaneous concurrent connections, broadcast delivery across concurrent peers, and clean disconnection cleanup.

## 15. Real-World Applications
* Architecture used by **Redis** (single-threaded in-memory database handling 100k+ ops/sec).
* High-performance edge reverse proxies (**Nginx** worker process model).
* Node.js and Python `asyncio` event loop backends.

## 16. Limitations
* Single-threaded event loops are bound to one CPU core. In multi-core systems, running multiple worker processes (like Nginx master-worker) scales across cores.

## 17. Future Enhancements
* Multi-core process clustering (SO_REUSEPORT).
* Integration of WebSocket framing for browser-based connectivity.

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. Why can't a single-threaded blocking socket server handle multiple clients?
2. What is I/O Multiplexing?
3. What is the Python `selectors` module?
4. What does `sock.setblocking(False)` do?
5. What are `EVENT_READ` and `EVENT_WRITE` in selectors?
6. Why must we remove `EVENT_WRITE` when the buffer is empty?
7. What is the "C10K problem"?
8. How does this project handle message fragmentation?
9. What happens when a client disconnects unexpectedly?
10. How do production servers like Nginx and Redis relate to this architecture?
