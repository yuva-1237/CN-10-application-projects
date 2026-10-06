# Computer Networks — 10 Application-Based Academic Projects

A comprehensive collection of 10 fully functional, independent, application-based Computer Networks academic projects built in Python 3.11+. Every project implements core networking algorithms, protocols, and socket mechanisms without masking functionality behind heavy black-box frameworks.

Designed specifically for undergraduate and graduate Computer Science / Information Technology laboratory curricula, semester mini-projects, and academic viva examinations.

---

## 1. Project Directory Matrix

| # | Project Directory | Primary Networking Concept | Protocol | Core Technologies | How to Run |
|---|---|---|---|---|---|
| **01** | [01_LAN_Chat_and_File_Sharing](01_LAN_Chat_and_File_Sharing/) | Duplex TCP Client-Server, Message Framing, File Streaming | TCP | Sockets, Threading, JSON/Binary Framing | `python app/server.py` <br> `python app/client.py` |
| **02** | [02_Reliable_UDP_File_Transfer](02_Reliable_UDP_File_Transfer/) | Application-Layer Reliability (ARQ, Sequence Numbers, ACKs, Retransmission, Checksumming) | UDP | Datagram Sockets, `struct`, CRC32 | `python app/receiver.py` <br> `python app/sender.py` |
| **03** | [03_Mini_HTTP_Web_Server](03_Mini_HTTP_Web_Server/) | HTTP/1.1 Protocol Parser, Request/Response Lifecycle, MIME Types | HTTP over TCP | Sockets, RFC 2616 parsing, Threading | `python app/server.py` <br> `python app/client.py` |
| **04** | [04_DNS_Resolver_and_Domain_Lookup](04_DNS_Resolver_and_Domain_Lookup/) | DNS Wire Protocol, Recursive Resolution, Resource Records (A/AAAA/MX/TXT), Caching | DNS over UDP/TCP | Sockets, DNS packet packing, `ipaddress` | `python app/resolver.py` |
| **05** | [05_Network_Routing_Simulator](05_Network_Routing_Simulator/) | Dynamic Routing Algorithms, Dijkstra Link-State, Distance-Vector, Link Failure Convergence | Simulated IP/Routing | Graph Theory, `heapq`, CLI / Topology Engine | `python app/simulator.py` |
| **06** | [06_Packet_Sniffer_and_Network_Analyzer](06_Packet_Sniffer_and_Network_Analyzer/) | Packet Decapsulation, Protocol Dissection (Eth/IP/TCP/UDP/ICMP), Traffic Metrics | Raw Sockets / Scapy | Raw Sockets, `struct`, Packet Dissector | `python app/analyzer.py` |
| **07** | [07_TCP_Congestion_Control_Simulator](07_TCP_Congestion_Control_Simulator/) | Congestion Control Mechanics (Slow Start, Congestion Avoidance, Fast Retransmit, Reno AIMD) | TCP State Simulation | Mathematical Model, Matplotlib / ASCII plotter | `python app/simulator.py` |
| **08** | [08_Multi_Client_Network_Server](08_Multi_Client_Network_Server/) | Concurrency Architecture, Non-blocking I/O Multiplexing, Event Loop (`selectors`) | TCP | Sockets, `selectors` (epoll/select), Threading | `python app/server.py` <br> `python app/client.py` |
| **09** | [09_Network_Monitoring_and_Device_Discovery](09_Network_Monitoring_and_Device_Discovery/) | ICMP Echo Latency Probing, Active Port Probing, Uptime Tracking, Health Dashboard | ICMP, TCP | Sockets, Subprocess Ping, ThreadPoolExecutor | `python app/monitor.py` |
| **10** | [10_Network_Intrusion_and_Port_Scan_Detection](10_Network_Intrusion_and_Port_Scan_Detection/) | Intrusion Detection (IDS), Heuristic Anomaly Detection, Sliding Window Threshold Correlation | TCP / IP Telemetry | Socket Listener, Sliding Window Counter | `python app/ids_engine.py` |

---

## 2. Collection Objective & Philosophy

Traditional networking lab curricula often suffer from two extremes:
1. **Trivial toy scripts:** 10-line echo servers that fail to demonstrate real-world networking concerns like message boundaries, concurrency, packet loss, or error handling.
2. **Framework opacity:** Web applications built on heavyweight frameworks (e.g. Django, Spring) where networking concepts are hidden behind high-level abstractions.

This repository provides **10 production-grade, pedagogically transparent projects**. Each project clearly exposes:
- **Operating system socket primitives:** `socket()`, `bind()`, `listen()`, `accept()`, `send()`, `recv()`, `sendto()`, `recvfrom()`.
- **Packet and stream handling:** Binary struct packing, header extraction, explicit framing, and byte-ordering (`!`).
- **Network fault tolerance:** Connection timeouts, broken pipes, packet corruption, retransmissions, and resource cleanup.

---

## 3. System Requirements & Prerequisites

- **Operating System:** Cross-platform support for Windows 10/11, Ubuntu/Debian Linux, and macOS.
- **Python Version:** Python 3.11 or higher (Python 3.13 recommended).
- **Core Dependencies:** The vast majority of projects use Python standard library modules (`socket`, `threading`, `selectors`, `struct`, `ipaddress`, `hashlib`, `queue`, `time`, `json`, `logging`). Optional visualization packages (`matplotlib`, `pytest`) are specified where needed.

---

## 4. Setup & Virtual Environment

Follow these steps from the repository root:

```bash
# 1. Clone or navigate to the repository directory
cd COMPUTER_NETWORKS

# 2. Create an isolated virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
# On Linux / macOS:
source venv/bin/activate

# 4. Install test framework and optional tools
pip install pytest
```

---

## 5. Security & Ethical Computing Guidelines

> [!WARNING]
> **Educational & Authorized Use Only:**
> All network scanning, probing, packet capture, and intrusion detection utilities contained in this repository are engineered exclusively for educational study and local laboratory analysis.
> - Default target configurations strictly bind to `127.0.0.1` (`localhost`) or private RFC 1918 test subnets.
> - Do not target or scan external public networks or any system without prior explicit, written authorization.
> - The software contains no exploits, no malware mechanisms, and no credential harvesting routines.

---

## 6. Project Recommendations for Academic Assessments

- **Best for Viva Examination:**
  - `01_LAN_Chat_and_File_Sharing` (demonstrates TCP socket lifecycle and multi-threading)
  - `02_Reliable_UDP_File_Transfer` (explains why UDP is unreliable and how TCP achieves reliability)
  - `07_TCP_Congestion_Control_Simulator` (explains AIMD, Slow Start, cwnd vs ssthresh)
- **Best for Lab Demonstrations:**
  - `03_Mini_HTTP_Web_Server` (serve browser-accessible pages using raw TCP sockets)
  - `05_Network_Routing_Simulator` (dynamic recalculation upon link failure)
  - `09_Network_Monitoring_and_Device_Discovery` (real-time live ping/port latency table)
- **Best for Major / Mini Academic Projects:**
  - `02_Reliable_UDP_File_Transfer`
  - `08_Multi_Client_Network_Server`
  - `10_Network_Intrusion_and_Port_Scan_Detection`
- **Best for Lab Record Submissions:**
  - `04_DNS_Resolver_and_Domain_Lookup`
  - `06_Packet_Sniffer_and_Network_Analyzer`
