# Network Concept Mapping

This document provides a comprehensive curriculum mapping of the 10 Computer Networks academic projects across the OSI 7-Layer Reference Model, the TCP/IP 4-Layer Architecture, foundational protocols, core socket primitives, and engineering learning outcomes.

---

## 1. Master Curriculum Mapping Table

| # | Project Name | Primary Network Concept | OSI Layer(s) | TCP/IP Layer | Primary Protocol(s) | Key Socket Primitives / APIs | Real-World Application Analogy |
|---|---|---|---|---|---|---|---|
| **01** | [LAN Chat & File Sharing](../01_LAN_Chat_and_File_Sharing/) | Connection-oriented duplex communication, streaming data framing | Layer 4 (Transport), Layer 7 (Application) | Transport, Application | TCP, Custom Binary/JSON Framing | `socket()`, `bind()`, `listen()`, `accept()`, `send()`, `recv()`, `threading` | WhatsApp LAN, AirDrop, IRC |
| **02** | [Reliable UDP File Transfer](../02_Reliable_UDP_File_Transfer/) | Application-layer reliability, ARQ, Stop-and-Wait / Sliding Window, checksumming | Layer 4 (Transport), Layer 7 (Application) | Transport, Application | UDP, Custom ARQ protocol | `socket(AF_INET, SOCK_DGRAM)`, `sendto()`, `recvfrom()`, `settimeout()` | TFTP, QUIC (HTTP/3), Real-time gaming sync |
| **03** | [Mini HTTP Web Server](../03_Mini_HTTP_Web_Server/) | Request-Response paradigm, stateless framing, MIME types, HTTP/1.1 lifecycle | Layer 7 (Application), Layer 4 (Transport) | Application, Transport | HTTP/1.1 over TCP | TCP stream parsing, request-line tokenization, header extraction | Apache, Nginx, Embedded IoT Web Admin |
| **04** | [DNS Resolver & Domain Lookup](../04_DNS_Resolver_and_Domain_Lookup/) | Hierarchical name resolution, recursive lookups, DNS record wire format, caching | Layer 7 (Application), Layer 4 (Transport) | Application, Transport | DNS (RFC 1035) over UDP/TCP | Raw UDP query generation, bitfield packing (`struct`), OS resolver fallback (`getaddrinfo`) | BIND9, Unbound, CoreDNS, Cloudflare 1.1.1.1 |
| **05** | [Network Routing Simulator](../05_Network_Routing_Simulator/) | Graph-theoretic routing, Link-State (Dijkstra), Distance-Vector (Bellman-Ford), convergence | Layer 3 (Network) | Internet / Network | Simulated IP forwarding, RIP/OSPF logic | Graph adjacency matrix, priority queue (`heapq`), routing table computation | OSPF, IS-IS, Internet BGP backbone routing |
| **06** | [Packet Sniffer & Network Analyzer](../06_Packet_Sniffer_and_Network_Analyzer/) | Packet demultiplexing, protocol header dissection, payload decapsulation | Layers 2, 3, 4, 7 (Data Link to Application) | Network Interface, Internet, Transport, Application | Ethernet, IPv4, TCP, UDP, ICMP | Raw sockets (`AF_INET, SOCK_RAW`), struct unpacking, promiscuous sniffing / Scapy | Wireshark, tcpdump, Zeek |
| **07** | [TCP Congestion Control Simulator](../07_TCP_Congestion_Control_Simulator/) | End-to-end congestion control, AIMD, Slow Start, Congestion Avoidance, Fast Retransmit | Layer 4 (Transport) | Transport | TCP Reno / Tahoe state machine | Mathematical state-machine (`cwnd`, `ssthresh`, RTT feedback, duplicate ACK tracking) | Linux TCP stack (Cubic, BBR, Reno) |
| **08** | [Multi-Client Network Server](../08_Multi_Client_Network_Server/) | Concurrency models, non-blocking I/O multiplexing, connection pooling | Layer 4 (Transport), Layer 5 (Session) | Transport | TCP | `selectors` (`epoll`/`kqueue`/`select`), thread pools, non-blocking sockets | Node.js event loop, Redis, Netty |
| **09** | [Network Monitoring & Device Discovery](../09_Network_Monitoring_and_Device_Discovery/) | Host liveness probing, round-trip latency, service reachability | Layer 3 (Network), Layer 4 (Transport) | Internet, Transport | ICMP (Echo Request/Reply), TCP SYN/Connect probing | Subprocess ping invocation, TCP connect probes, non-blocking socket timeouts | Nagios, Zabbix, Pingdom, Prometheus Blackbox |
| **10** | [Network Intrusion & Port Scan Detection](../10_Network_Intrusion_and_Port_Scan_Detection/) | Traffic anomaly detection, threshold-based heuristics, sliding window time correlation | Layer 3 (Network), Layer 4 (Transport) | Internet, Transport | TCP, UDP, IP connection telemetry | Socket listener honeypot / connection monitor, sliding-window counter | Snort, Suricata, Fail2Ban |

---

## 2. OSI Model Layer-by-Layer Decomposition

### Layer 7 — Application Layer
- **Protocols:** HTTP, DNS, Custom Chat/File Protocol, ARQ Protocol.
- **Projects:**
  - `01_LAN_Chat_and_File_Sharing`: Formats message frames (JSON payloads: type, sender, recipient, payload length).
  - `03_Mini_HTTP_Web_Server`: Implements HTTP/1.1 grammar (RFC 2616/7230) — request line (`GET /path HTTP/1.1`), headers, and CRLF separators.
  - `04_DNS_Resolver_and_Domain_Lookup`: Packs and decodes DNS questions, answers, and record resource records (A, AAAA, MX, CNAME, TXT).

### Layer 6 — Presentation Layer
- **Concepts:** Data representation, serialization, character encoding, compression, and checksum hashing.
- **Projects:**
  - `01_LAN_Chat_and_File_Sharing` & `02_Reliable_UDP_File_Transfer`: Handles UTF-8 string encoding, raw byte chunking, and MD5/SHA-256 cryptographic verification of transmitted chunks.
  - `03_Mini_HTTP_Web_Server`: Translates file binary streams into appropriate MIME content types (`text/html`, `image/png`, `application/json`).

### Layer 5 — Session Layer
- **Concepts:** Dialogue control, connection lifetime management, session tokenization.
- **Projects:**
  - `01_LAN_Chat_and_File_Sharing`: Manages user login, presence status (online/offline), and active file transfer handshakes.
  - `08_Multi_Client_Network_Server`: Tracks client session state, unique client identifiers, and graceful heartbeat/disconnect teardowns.

### Layer 4 — Transport Layer
- **Protocols:** TCP (Transmission Control Protocol), UDP (User Datagram Protocol).
- **Projects:**
  - `01_LAN_Chat_and_File_Sharing` & `08_Multi_Client_Network_Server`: Relies on TCP for 3-way handshakes (`SYN`, `SYN-ACK`, `ACK`), reliable byte streams, and in-order delivery.
  - `02_Reliable_UDP_File_Transfer`: Exposes the raw, unreliable nature of UDP datagrams and constructs an application-layer transport protocol with sequence numbers, timeouts, and retransmissions.
  - `07_TCP_Congestion_Control_Simulator`: Deconstructs transport-layer congestion management (`cwnd`, `ssthresh`, multiplicative decrease, slow start exponential growth).

### Layer 3 — Network Layer
- **Protocols:** IP (IPv4 / IPv6), ICMP (Internet Control Message Protocol), Routing protocols (OSPF, RIP, BGP).
- **Projects:**
  - `05_Network_Routing_Simulator`: Evaluates topological graphs, computes shortest paths using Dijkstra's Link-State algorithm, and builds next-hop routing tables.
  - `09_Network_Monitoring_and_Device_Discovery`: Measures network reachability using ICMP Echo Request / Echo Reply packets and calculates round-trip time (RTT).
  - `10_Network_Intrusion_and_Port_Scan_Detection`: Analyzes incoming source IP addresses and correlates connection frequencies across IP networks.

### Layer 2 — Data Link Layer
- **Protocols:** Ethernet (IEEE 802.3), ARP.
- **Projects:**
  - `06_Packet_Sniffer_and_Network_Analyzer`: Inspects raw frame headers, extracting source and destination MAC addresses, EtherType identifiers (0x0800 for IPv4, 0x86DD for IPv6, 0x0806 for ARP).

### Layer 1 — Physical Layer
- While software applications cannot directly manipulate physical voltages or radio frequencies, packet sizing, MTU limits (1500 bytes on typical Ethernet), and fragmentation boundaries are directly considered in `02_Reliable_UDP_File_Transfer` and `06_Packet_Sniffer_and_Network_Analyzer`.

---

## 3. TCP vs. UDP Comparative Matrix

| Characteristic | TCP (Demonstrated in Projects 01, 03, 07, 08) | UDP (Demonstrated in Projects 02, 04) |
|---|---|---|
| **Connection Paradigm** | Connection-oriented (requires explicit 3-way handshake) | Connectionless (fire-and-forget datagrams) |
| **Reliability** | Guaranteed delivery (kernel handles retransmission) | Unreliable (datagrams may be lost or reordered) |
| **Data Ordering** | Strictly ordered byte-stream (reassembled via sequence numbers) | No ordering guarantees (handled manually in Project 02) |
| **Header Overhead** | 20 to 60 bytes | Lightweight: exactly 8 bytes |
| **Flow & Congestion Control**| Window-based flow control (rwnd) & congestion control (cwnd) | None native (sender can flood link unless throttled) |
| **Communication Style** | Stream (no message boundaries preserved in raw stream) | Message / Datagram boundaries preserved per packet |
| **Typical Protocols** | HTTP, SSH, FTP, SMTP, TLS | DNS, TFTP, DHCP, VoIP, QUIC |
