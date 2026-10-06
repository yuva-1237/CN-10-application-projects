# DNS Resolver & Domain Lookup System

## 1. Objective
To build an educational DNS resolver and domain inspection utility in Python, demonstrating RFC 1035 UDP wire packet construction, DNS resource record unpacking (A, AAAA, MX, PTR), recursive name resolution, resolution latency benchmarking, and in-memory TTL caching.

## 2. Problem Statement
The Internet functions through numerical IP addresses, yet users navigate using domain names. The translation of human-readable hostnames to IP addresses occurs through the Domain Name System (DNS). Many students treat DNS as a black box without understanding how DNS queries are packaged into binary UDP datagrams, how resource records are parsed, or how DNS caching mitigates network latency. This project makes the internal mechanisms of DNS transparent and inspectable.

## 3. Computer Networks Concepts Used
* **Domain Name System (DNS, RFC 1035):** Distributed hierarchical database.
* **UDP Socket Communication:** Transmitting single-packet queries on port 53.
* **DNS Wire Format:** Structuring 12-byte headers, label-encoded questions, and answer sections.
* **DNS Resource Records:** `A` (IPv4), `AAAA` (IPv6), `MX` (Mail Exchange), `CNAME` (Alias), `PTR` (Reverse Pointer).
* **Pointer Compression:** Bitmask decoding (`0xC0`) for compressed domain labels.
* **Caching & TTL:** Managing local record validity to prevent redundant network lookups.

## 4. Protocol Used
* **Application:** DNS Protocol (RFC 1035 / RFC 3596).
* **Transport:** UDP over IPv4 (`AF_INET`, `SOCK_DGRAM`) on Port 53 (with OS resolver fallback).

## 5. Architecture
* **`app/dns_wire.py`:** Low-level encoder/decoder. Formats QNAME label byte sequences, packs binary query headers, and decodes incoming answer records.
* **`app/resolver.py`:** Main resolution coordinator. Dispatches queries to public DNS servers (default `8.8.8.8` / `1.1.1.1`), benchmarks network round-trip time, queries reverse PTR records, and integrates the local TTL cache.
* **`app/utils.py` (`DNSCache`):** Thread-safe cache storing previously resolved domain records with expiration timestamps.

```
Client (User)
      |
      v
+-------------+      Cache Hit (<0.1ms)
|  DNS Cache  | ------------------------> Return Cached Record
+-------------+
      | Cache Miss
      v
+-------------------+
| Raw UDP Query Gen |
+-------------------+
      | (UDP Port 53)
      v
+-----------------------------------+
| Upstream DNS Server (8.8.8.8)     |
+-----------------------------------+
      | Binary UDP Answer
      v
+-----------------------------------+
| RFC 1035 Unpacker & Cache Storage |
+-----------------------------------+
```

## 6. System Requirements
* **Operating System:** Windows 10/11, Linux, or macOS.
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only.

## 7. Technologies Used
* `socket`: UDP datagram transmission (`SOCK_DGRAM`) and address parsing.
* `struct`: Binary packing and bitfield parsing of RFC 1035 headers.
* `time`: High-resolution latency profiling (`perf_counter`).
* `pytest`: Automated test framework.

## 8. Project Structure
```
04_DNS_Resolver_and_Domain_Lookup/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── dns_wire.py
│   ├── resolver.py
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
cd COMPUTER_NETWORKS/04_DNS_Resolver_and_Domain_Lookup
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Run Domain Lookup
```bash
python app/resolver.py google.com
```

### Step 2: Query via Custom DNS Server (e.g. Cloudflare 1.1.1.1)
```bash
python app/resolver.py wikipedia.org --server 1.1.1.1
```

### Step 3: Perform Reverse DNS (PTR) Lookup
```bash
python app/resolver.py 8.8.8.8 --reverse
```

## 11. How the Network Communication Works
1. **Cache Inspection:** Resolver queries `DNSCache`. If found and valid, returns cached record in < 0.1 ms.
2. **Datagram Packaging:** Builds binary header with random 16-bit Query ID, flags `0x0100` (Standard Query, Recursion Desired), and encodes hostname into RFC labels.
3. **UDP Transport:** Transmits the query datagram via `sendto()` to `8.8.8.8:53`.
4. **Unpacking:** Reads response datagram via `recvfrom()`, verifies response Query ID, skips Question section, and iterates through Answer Resource Records.
5. **Reverse Resolution:** Invokes `socket.gethostbyaddr()` to discover PTR canonical hostnames.

## 12. Example Input
```bash
python app/resolver.py example.com
```

## 13. Example Output
```
Resolving Domain: example.com via 8.8.8.8...
============================================================
  DNS RESOLUTION REPORT
============================================================
Domain Name     : example.com
IPv4 Addresses  : 93.184.216.34
IPv6 Addresses  : 2606:2800:220:1:248:1893:25c8:1946
Reverse Hostname: Not Available (No PTR Record)
Resolution Time : 34.12 ms
DNS Server Used : 8.8.8.8
Resolver Engine : RAW_UDP_PORT_53
Cache Status    : LIVE NETWORK QUERY
============================================================
```

## 14. Testing
Run the automated test suite:
```bash
pytest tests/test_basic.py -v
```
Validates RFC 1035 label serialization, DNS query packet formatting, mock answer parsing, cache hit/miss behavior, and localhost domain resolution.

## 15. Real-World Applications
* System DNS resolvers embedded in operating systems (Linux `systemd-resolved`, Windows DNS Client).
* High-performance public DNS resolvers (Cloudflare 1.1.1.1, Google 8.8.8.8, Quad9 9.9.9.9).
* Edge caching and content distribution networks (CDN routing).

## 16. Limitations
* Does not perform iterative root-hints traversal from the 13 Root DNS servers directly (it delegates recursion to an upstream recursive resolver like 8.8.8.8).
* Does not validate DNSSEC cryptographic signatures.

## 17. Future Enhancements
* Implementation of full iterative root traversal starting at `a.root-servers.net`.
* DNS over HTTPS (DoH) / DNS over TLS (DoT) encryption wrapper.

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is DNS and what is its primary function?
2. On which port and transport protocol does DNS normally operate?
3. What is the difference between an 'A' record and an 'AAAA' record?
4. What is a Reverse DNS (PTR) lookup?
5. What does the Recursion Desired (RD) flag indicate?
6. What is DNS caching and why is TTL important?
7. What is DNS label compression in RFC 1035?
8. What is the hierarchical structure of DNS?
9. When does DNS use TCP instead of UDP?
10. What is the purpose of an MX record?
