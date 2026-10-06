# Packet Sniffer & Network Analyzer

## 1. Objective
To build an educational packet sniffing and network protocol analysis utility in Python that captures or ingests raw network frames, performs multi-layer decapsulation (Ethernet, IPv4, TCP, UDP, ICMP), filters traffic by protocol, and calculates statistical metrics across network sessions.

## 2. Problem Statement
Network administrators and security engineers depend heavily on packet analyzers like Wireshark and tcpdump to diagnose communication faults, investigate latency anomalies, and inspect protocol headers. For students, GUI sniffers often obscure the underlying binary bitfields and header formats. This project dissects packet frames from the bit level up using Python's standard `struct` unpacking primitives.

## 3. Computer Networks Concepts Used
* **Multi-Layer Protocol Decapsulation:** Navigating from Layer 2 (Ethernet) to Layer 3 (IPv4) to Layer 4 (TCP/UDP/ICMP) and Layer 7 (Application hints).
* **Binary Header Parsing:** Bitwise shifting and unpacking of fields like IHL, ToS, TTL, TCP Flags, and ports.
* **Network Sockets:** Raw sockets (`SOCK_RAW`) and promiscuous mode (`SIO_RCVALL`).
* **Traffic Analytics:** Calculating protocol distributions, bandwidth totals, top communicating IP pairs, and port utilization.
* **Controlled Fallback:** `SAMPLE DATA MODE` ensuring academic viability in non-privileged environments.

## 4. Protocol Used
* Dissects Ethernet II, IPv4, TCP, UDP, ICMP, DNS (port 53), HTTP (port 80/8080).

## 5. Architecture
* **`app/dissector.py`:** Protocol dissector that parses raw byte buffers into structured `PacketMetadata` objects.
* **`app/sniffer.py` (`PacketSniffer`):** Manages raw socket binding. If permission is denied, switches to `SAMPLE DATA MODE`.
* **`app/analyzer.py` (`NetworkTrafficAnalyzer`):** Aggregates captured packet data, produces terminal summaries, and exports JSON reports.

```
       +------------------------------------+
       |  Raw Socket / Synthetic Feed      |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  Dissector: Ethernet -> IP -> L4   |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  Protocol Filtering (TCP/UDP/ICMP) |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  Traffic Aggregator & JSON Report  |
       +------------------------------------+
```

## 6. System Requirements
* **Operating System:** Windows 10/11, Linux, or macOS.
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only.

## 7. Technologies Used
* `socket.SOCK_RAW`: Low-level network interface access.
* `struct`: Binary unpacking of network byte orders (`!`).
* `collections.Counter`: High-speed traffic frequency analysis.
* `pytest`: Test automation.

## 8. Project Structure
```
06_Packet_Sniffer_and_Network_Analyzer/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── dissector.py
│   ├── sniffer.py
│   ├── analyzer.py
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
cd COMPUTER_NETWORKS/06_Packet_Sniffer_and_Network_Analyzer
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Run in Default Mode (Automatically checks privileges)
```bash
python app/analyzer.py --count 30
```
*If executed with Administrator / root privileges, it engages `LIVE CAPTURE`. Otherwise, it falls back to `SAMPLE DATA MODE`.*

### Step 2: Filter by Protocol
```bash
python app/analyzer.py --count 20 --filter TCP
python app/analyzer.py --count 20 --filter DNS
python app/analyzer.py --count 20 --filter ICMP
```

### Step 3: Force Sample Mode & Export JSON Report
```bash
python app/analyzer.py --sample --count 25 --export logs/lab_report.json
```

## 11. How the Network Communication Works
1. **Frame Capture:** Raw socket captures binary frame from the physical or loopback adapter.
2. **IP Decapsulation:** Unpacks 20-byte IP header, calculates header length via IHL, extracts source and destination IPv4 addresses.
3. **Transport Demultiplexing:** Inspects IP protocol number (`6` for TCP, `17` for UDP, `1` for ICMP) and delegates to corresponding dissector.
4. **TCP Flag Bitfield Analysis:** Evaluates 9-bit TCP flag field to detect connection handshakes (`SYN`, `ACK`) and terminations (`FIN`).
5. **Statistical Aggregation:** Counter data structures aggregate endpoint frequencies and protocol percentages.

## 12. Example Input
```bash
python app/analyzer.py --sample --count 10
```

## 13. Example Output
```
============================================================
           PACKET SNIFFER & NETWORK ANALYZER
============================================================
* EDUCATIONAL USE ONLY: Capture only on authorized interfaces.
============================================================
[TCP ] 192.168.1.50:54120     -> 93.184.216.34:80       | Len: 40   [HTTP]
[TCP ] 93.184.216.34:80       -> 192.168.1.50:54120     | Len: 40   [HTTP]
[UDP ] 192.168.1.50:53123     -> 8.8.8.8:53             | Len: 62   [DNS]
[ICMP] 192.168.1.50           -> 192.168.1.1            | Len: 60   [ECHO_REQUEST (Ping)]
[ICMP] 192.168.1.1            -> 192.168.1.50           | Len: 60   [ECHO_REPLY (Pong)]

=================================================================
         NETWORK TRAFFIC ANALYSIS REPORT
=================================================================
Total Packets Analyzed : 10
Total Volume Captured  : 484 bytes
Average Packet Size    : 48.4 bytes

[Protocol Distribution]
  TCP       :    4 pkts ( 40.0%) | ##########
  UDP       :    2 pkts ( 20.0%) | #####
  ICMP      :    4 pkts ( 40.0%) | ##########

[Top Source IPs]
  192.168.1.50        : 6 packets
  93.184.216.34       : 2 packets
  192.168.1.1         : 2 packets
=================================================================
```

## 14. Testing
Run the 5 automated unit tests:
```bash
pytest tests/test_basic.py -v
```
Validates IPv4 header unpacking, TCP SYN-ACK flag decoding, UDP length extraction, ICMP echo dissection, and statistical report generation with JSON export.

## 15. Real-World Applications
* Network troubleshooting tools: Wireshark, tcpdump, TShark.
* Intrusion Detection Systems (IDS): Snort, Suricata.
* Enterprise network bandwidth monitoring and NetFlow collectors.

## 16. Limitations
* In user mode without root/admin privileges, cannot place physical network adapters into promiscuous mode (mitigated via `SAMPLE DATA MODE`).

## 17. Future Enhancements
* Decapsulation of IPv6 headers and IPv6 extension header chains.
* PCAP file export and import (.pcap format for Wireshark interoperability).

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is a packet sniffer?
2. What is "promiscuous mode" on a NIC?
3. Why does packet sniffing require administrator privileges?
4. How is an IP header's IHL converted into bytes?
5. How do we determine which transport protocol is carried in IPv4?
6. What are the primary TCP flags and what do they mean?
7. What is the difference between TCP and UDP headers?
8. What does ICMP Type 8 and Type 0 represent?
9. What is the purpose of the TTL field in the IP header?
10. What are the ethical and legal boundaries of packet sniffing?
