# Master Academic Lab Screenshot Guide

This guide details the specific screens and execution steps that students must capture for their academic laboratory record notebooks, project reports, and viva evaluation presentations across all 10 Computer Networks projects.

---

## Project 01: LAN Chat & File Sharing System
* **Screenshot 1 — Server Startup & IP Binding:**
  - Command: `python app/server.py --port 5001`
  - What to capture: Server startup banner displaying LAN Host IP (e.g. `192.168.x.x` or `127.0.0.1`), Port `5001`, and socket listening state.
* **Screenshot 2 — Multi-Client Duplex Chat:**
  - Terminals: Two client terminal windows (`Alice` and `Bob`) side-by-side.
  - What to capture: Alice sending a broadcast message, Bob receiving it, followed by a direct `/msg` private message between them.
* **Screenshot 3 — Chunked File Transmission & Checksum:**
  - Command: Alice sending `/sendfile data/test.pdf Bob`
  - What to capture: Outgoing chunk progress on Alice's terminal, incoming chunks on Bob's terminal, and the final verification message: `[Checksum Verified: SHA-256 OK]`.

---

## Project 02: Reliable UDP File Transfer System
* **Screenshot 1 — Clean UDP Transfer:**
  - Receiver Terminal: `python app/receiver.py --port 5002`
  - Sender Terminal: `python app/sender.py data/sender_files/test.txt --port 5002 --loss 0.0`
  - What to capture: Receiver sequential chunk reassembly and sender transfer summary (0 retransmissions).
* **Screenshot 2 — Simulated Packet Loss & Retransmission Recovery:**
  - Command: `python app/sender.py data/sender_files/test.txt --port 5002 --loss 0.20`
  - What to capture: Yellow/warning log lines showing simulated packet drops (`[SIMULATION] Dropped SEQ #...`), timeout expirations, automatic retransmission attempts, and final `[VERIFIED MATCH - 100% RELIABLE]` integrity message.

---

## Project 03: Mini HTTP Web Server & Client
* **Screenshot 1 — Web Browser Rendering:**
  - Server Terminal: `python app/server.py --port 8080`
  - Browser: Open `http://localhost:8080`
  - What to capture: Full browser window showing formatted homepage (`index.html`), stylesheet formatting (`styles.css`), and navigation bar.
* **Screenshot 2 — 404 Not Found Page:**
  - Browser: Navigate to `http://localhost:8080/nonexistent.html`
  - What to capture: Styled 404 error page and corresponding terminal log line (`"GET /nonexistent.html" 404 Not Found`).
* **Screenshot 3 — Educational TCP Client Protocol Dissection:**
  - Command: `python app/client.py --method GET --path /api/status.json`
  - What to capture: Terminal breakdown showing raw ASCII request headers, status code 200, MIME content-type, and formatted JSON payload.

---

## Project 04: DNS Resolver & Domain Lookup System
* **Screenshot 1 — Domain Lookup & Latency:**
  - Command: `python app/resolver.py google.com`
  - What to capture: Output table displaying Domain Name, IPv4 addresses, IPv6 addresses, reverse hostname, and resolution time in milliseconds.
* **Screenshot 2 — Cache Hit vs Live Query:**
  - Command: Run lookup on the same domain twice consecutively.
  - What to capture: First query showing `LIVE NETWORK QUERY` with multi-millisecond latency; second query showing `CACHE HIT` with near-zero latency (<0.1 ms).
* **Screenshot 3 — Reverse DNS (PTR) Lookup:**
  - Command: `python app/resolver.py 8.8.8.8 --reverse`
  - What to capture: IP address `8.8.8.8` resolving back to canonical hostname `dns.google`.

---

## Project 05: Network Routing Simulator
* **Screenshot 1 — Topology Display & Routing Table:**
  - Command: Run `python app/simulator.py`, select Option 1 (Display Topology) and Option 3 (View Routing Table for Node A).
  - What to capture: Configured routers, link weights, and computed forwarding table with destinations and next hops.
* **Screenshot 2 — Shortest Path Calculation:**
  - Option 2: Source `A`, Destination `F`.
  - What to capture: Computed path `A -> B -> C -> F` with Total Cost = 4 and Next Hop = B.
* **Screenshot 3 — Dynamic Link Failure Recalculation:**
  - Option 7: Simulate failure on link `C <---> F`.
  - Option 2: Re-run path calculation for `A -> F`.
  - What to capture: Automatic detour recalculation to `A -> B -> E -> F` with Total Cost = 6.

---

## Project 06: Packet Sniffer & Network Analyzer
* **Screenshot 1 — Multi-Layer Decapsulation Feed:**
  - Command: `python app/analyzer.py --sample --count 15`
  - What to capture: Stream of dissected packet frames showing protocol tags (`[TCP]`, `[UDP]`, `[ICMP]`), source/destination IP and port pairs, and packet lengths.
* **Screenshot 2 — Statistical Protocol Distribution Report:**
  - What to capture: Terminal summary showing total packet count, byte volume, protocol distribution histogram bars (`#`), and top source IPs.

---

## Project 07: TCP Congestion Control Simulator
* **Screenshot 1 — Discrete Round-by-Round Trace Table:**
  - Command: `python app/simulator.py --variant RENO`
  - What to capture: Trace table detailing `Round`, `cwnd`, `ssthresh`, `State`, and transition events (Slow Start exponential doubling, Congestion Avoidance linear growth, Timeout, and Fast Recovery).
* **Screenshot 2 — ASCII Congestion Window Graph:**
  - What to capture: Terminal ASCII line graph displaying the classic AIMD "sawtooth" waveform of the congestion window over transmission rounds.

---

## Project 08: Multi-Client Network Server
* **Screenshot 1 — Concurrent 5-Client Swarm Load Test:**
  - Server Terminal: `python app/server.py --port 5008`
  - Client Terminal: `python app/client.py --port 5008 --swarm 5`
  - What to capture: Rapid registration of `Swarm_Bot_1` through `Swarm_Bot_5` simultaneously, broadcast message exchange, and server telemetry report displaying 5 active clients on a single event-loop thread.
* **Screenshot 2 — Interactive Private Messaging:**
  - Client Terminals: Alice and Bob connected concurrently, sending `/msg Bob Hello!` and receiving the direct message.

---

## Project 09: Network Monitoring & Device Discovery
* **Screenshot 1 — Live Dashboard Table:**
  - Command: `python app/monitor.py --targets 127.0.0.1,localhost --ports 80,443,8080,5001,5008 --cycles 2`
  - What to capture: Formatted status dashboard table showing Target, IP, Status (`ONLINE`), Latency (ms), Uptime Percentage, and Open Ports.
* **Screenshot 2 — JSON Incident / Uptime Report:**
  - What to capture: Exported JSON report file (`logs/monitor_report_*.json`) opened in an editor or terminal.

---

## Project 10: Network Intrusion & Port Scan Detection System
* **Screenshot 1 — IDS Engine Honeypot Listener Startup:**
  - Terminal 1: `python app/ids_engine.py`
  - What to capture: IDS startup banner showing monitored ports (5010 to 5017), detection threshold ($N=5$), and sliding time window ($T=10.0$s).
* **Screenshot 2 — High-Visibility Security Alert Box:**
  - Terminal 2: `python app/simulator.py`
  - Terminal 1: What to capture: Security Alert Box triggered in real time showing Incident ID, Source IP (`127.0.0.1`), Ports Contacted, Severity Level (`MEDIUM` / `HIGH`), and mitigation recommendation.
