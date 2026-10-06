# Reliable UDP File Transfer System

## 1. Objective
To design and construct an application-layer reliable transport protocol over User Datagram Protocol (UDP) sockets in Python, demonstrating sequence numbering, explicit acknowledgments (ACKs), timeout detection, automatic retransmissions (ARQ), CRC-32 packet validation, and simulated packet loss recovery.

## 2. Problem Statement
The User Datagram Protocol (UDP) is fundamentally connectionless and unreliable. Packets can be dropped by routers, duplicated, arrive out of sequence, or suffer bit corruption. Applications that require low overhead or custom multiplexing (e.g. TFTP, DNS, QUIC/HTTP-3, game state synchronization) must implement reliability mechanisms manually at the application layer. This project solves these challenges by engineering an ARQ protocol over raw UDP sockets.

## 3. Computer Networks Concepts Used
* **User Datagram Protocol (UDP):** Connectionless, best-effort transport layer protocol (`SOCK_DGRAM`).
* **Datagram Framing & Header Serialization:** Binary encoding using `struct` with Big-Endian network byte order.
* **Stop-and-Wait ARQ:** Transmission flow control where the sender waits for an explicit ACK before advancing.
* **Sequence Numbers & Duplication Filter:** Tracking datagram order and rejecting repeated packets.
* **Error Detection:** 32-bit Cyclic Redundancy Check (CRC-32) per packet and end-to-end SHA-256 file hashing.
* **Simulated Network Impairment:** Configurable artificial packet drop rates to demonstrate real-time retransmissions.

## 4. Protocol Used
* **Transport:** UDP over IPv4 (`AF_INET`, `SOCK_DGRAM`).
* **Application Protocol:** Custom Binary RUDP Protocol (17-byte data header, 11-byte ACK header).

## 5. Architecture
* **Sender:** Breaks a source file into chunks (default: 1024 bytes), encodes headers with sequence numbers and CRC-32 checksums, sends datagrams via `sendto()`, and manages an active timeout timer. If an ACK is not received within `TIMEOUT_SECONDS`, it retransmits up to `MAX_RETRIES`.
* **Receiver:** Binds to a UDP port via `bind()`, receives datagrams via `recvfrom()`, validates CRC-32 integrity, drops corrupted frames, sends ACKs back to sender address, and reassembles valid chunks sequentially.

```
Sender (Client)                                Receiver (Server)
      |                                              |
      |--------- UDP DATA (SEQ #1, CRC32) ---------->|
      |<-------- UDP ACK  (ACK #1, Status=OK) -------|
      |                                              |
      |--X [Simulated Loss / Dropped]                |
      |                                              |
      | [Timeout Timer Expires: 0.5s]                |
      |--------- UDP RETRANSMIT (SEQ #2) ----------->|
      |<-------- UDP ACK (ACK #2, Status=OK) --------|
```

## 6. System Requirements
* **Operating System:** Windows 10/11, Linux, or macOS.
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library (`socket`, `struct`, `zlib`, `hashlib`, `json`, `argparse`).

## 7. Technologies Used
* `socket.SOCK_DGRAM`: Raw UDP datagram transmission.
* `struct`: Binary packing and unpacking of custom headers.
* `zlib.crc32`: Fast cyclic redundancy checking.
* `hashlib.sha256`: Cryptographic end-to-end file verification.
* `pytest`: Test automation.

## 8. Project Structure
```
02_Reliable_UDP_File_Transfer/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── packet.py
│   ├── sender.py
│   ├── receiver.py
│   └── utils.py
├── tests/
│   └── test_basic.py
├── docs/
│   ├── architecture.md
│   └── viva.md
├── data/
│   ├── sender_files/
│   └── received_files/
└── logs/
```

## 9. Installation
```bash
cd COMPUTER_NETWORKS/02_Reliable_UDP_File_Transfer
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Start the Receiver
```bash
python app/receiver.py --port 5002
```
*To simulate receiver-side drop rate, pass `--loss 0.15` (15% drop rate).*

### Step 2: Prepare a Sample File
```bash
# Create a test file
echo "Computer Networks Lab - UDP Reliability Test" > data/sender_files/test.txt
```

### Step 3: Run the Sender with Simulated Loss
```bash
python app/sender.py data/sender_files/test.txt --port 5002 --loss 0.20
```
*The `--loss 0.20` flag simulates 20% random packet drop, visibly triggering timeouts and retransmissions in real-time.*

## 11. How the Network Communication Works
1. **Metadata Phase:** Sender constructs a `TYPE_START` packet containing filename, filesize, and SHA-256 hash. Receiver receives, logs the transfer, and emits `ACK #0`.
2. **Chunking & Datagram Sizing:** File is partitioned into chunks of 1024 bytes (well within the standard 1500-byte Ethernet MTU).
3. **Transmission & Checksum:** For each chunk, a 17-byte header is prepended with `transfer_id`, `seq_num`, and `crc32`.
4. **Reliability Loop:** Sender sends datagram and blocks on `recvfrom()` for at most 0.5s. If an ACK arrives with matching sequence number, it proceeds; otherwise, it triggers a retransmission attempt.
5. **Reassembly & Verification:** Receiver collects all chunks, writes them sequentially to disk, and runs SHA-256 hashing to confirm 100% bit-for-bit parity with sender.

## 12. Example Input
```bash
python app/sender.py data/sender_files/sample_presentation.pdf --port 5002 --loss 0.20
```

## 13. Example Output
```
[2026-10-06 09:28:00] [INFO] [RUDP_Sender]: Initiated Transfer #4812: 'sample_presentation.pdf' (1.20 MB across 1230 packets)
[2026-10-06 09:28:02] [WARNING] [RUDP_Sender]: [SIMULATION] Dropped SEQ #42 on attempt 1/6 (Simulated Loss)
[2026-10-06 09:28:02] [WARNING] [RUDP_Sender]: Timeout waiting for ACK #42! Retransmitting (Attempt 1/6)...
[2026-10-06 09:28:03] [INFO] [RUDP_Receiver]: Reassembling 1230/1230 packets into rudp_sample_presentation.pdf...
[2026-10-06 09:28:03] [INFO] [RUDP_Receiver]: >> INTEGRITY STATUS: [VERIFIED MATCH - 100% RELIABLE] <<
```

## 14. Testing
Run the 5 automated unit and integration tests:
```bash
pytest tests/test_basic.py -v
```
Tests validate packet serialization, corrupted bit detection, zero-loss transfer, 30% simulated packet loss recovery, and final cryptographic checksum matching.

## 15. Real-World Applications
* **QUIC / HTTP/3:** Modern internet protocol developed by Google, running multiplexed reliable streams over UDP.
* **TFTP (Trivial File Transfer Protocol):** Lightweight PXE network bootloaders.
* **Multiplayer Video Games:** State synchronization where game physics use UDP with selective reliability for critical events (e.g. player death, inventory changes).

## 16. Limitations
* Uses Stop-and-Wait ARQ for pedagogical clarity, which yields lower throughput over high-latency satellite or WAN links compared to pipelined Sliding Window protocols (Go-Back-N or Selective Repeat).

## 17. Future Enhancements
* Implementation of Selective Repeat Sliding Window with configurable window size ($W$).
* Dynamic Round Trip Time (RTT) estimation using Jacobson's algorithm ($RTO = SRTT + 4 \times RTTVAR$).

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What makes UDP inherently "unreliable"?
2. What is an ARQ protocol?
3. How does this project achieve reliability over UDP?
4. Why is a sequence number needed in the packet header?
5. What is Stop-and-Wait ARQ?
6. Why do we use CRC-32 on each datagram in addition to UDP's built-in checksum?
7. What is MTU and why is our chunk size set to 1024 bytes?
8. What happens if an ACK packet itself gets lost?
9. What is the trade-off between TCP and Application-Level Reliable UDP?
10. Why do we verify SHA-256 at the end of the transfer?
