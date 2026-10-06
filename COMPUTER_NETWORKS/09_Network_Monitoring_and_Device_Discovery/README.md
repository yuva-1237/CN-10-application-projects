# Network Monitoring & Device Discovery System

## 1. Objective
To build a local network device monitoring and reachability engine in Python, demonstrating ICMP echo latency benchmarking, cross-platform ping execution, TCP connect service reachability fallback, uptime percentage tracking, status transition alerting, and structured report exports.

## 2. Problem Statement
Maintaining high availability across enterprise server clusters and IoT fleets requires continuous reachability and latency monitoring. However, network firewalls frequently block standard ICMP Echo (ping) requests. Students must understand how to combine Layer 3 (ICMP) and Layer 4 (TCP SYN/Connect) probing techniques, measure round-trip latency accurately, and calculate service availability metrics without generating unauthorized or destructive network traffic.

## 3. Computer Networks Concepts Used
* **Network Layer (OSI Layer 3):** Internet Control Message Protocol (ICMP) Echo Request/Reply.
* **Transport Layer (OSI Layer 4):** TCP stream connection handshake probing.
* **Round-Trip Time (RTT):** High-precision network latency measurement in milliseconds.
* **Service Reachability:** Discerning between `OPEN`, `CLOSED` (connection refused / RST), and `FILTERED` (timeout) port states.
* **Availability Metrics:** Computing uptime percentages over recurring monitoring sweeps.
* **Network Security & Ethical Scoping:** Restricting discovery to authorized loopback or local subnet scopes.

## 4. Protocol Used
* ICMP (Echo Request Type 8 / Echo Reply Type 0)
* TCP over IPv4 (`AF_INET`, `SOCK_STREAM`) on targeted service ports.

## 5. Architecture
* **`app/probe.py`:** Core low-level reachability engine. Issues platform-specific ICMP ping commands (`ping -n 1` on Windows, `ping -c 1` on Linux/macOS) and executes non-blocking TCP connect probes with timeout traps.
* **`app/monitor.py` (`NetworkMonitor`):** Central coordinator managing target host inventory, scheduling periodic check sweeps, tracking state changes ($ONLINE \leftrightarrow OFFLINE$), rendering an ASCII terminal dashboard, and exporting JSON telemetry.
* **`app/utils.py`:** ASCII table rendering and logging utilities.

```
+-------------------------------------------------------------+
|                     NetworkMonitor                          |
+-------------------------------------------------------------+
               |                               |
       (Layer 3 ICMP Ping)             (Layer 4 TCP Probe)
               |                               |
               v                               v
    +----------------------+       +-----------------------+
    | Host Liveness & RTT  |       | Service Availability  |
    | (Echo Reply / Dropped)|      | (OPEN / CLOSED / FLTR)|
    +----------------------+       +-----------------------+
               \                               /
                \                             /
                 v                           v
+-------------------------------------------------------------+
|             Real-Time Terminal Dashboard & Report           |
| Target | IP | Status | Latency ms | Uptime % | Open Ports   |
+-------------------------------------------------------------+
```

## 6. System Requirements
* **Operating System:** Cross-platform (Windows 10/11, Linux, macOS).
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only (`subprocess`, `socket`, `re`, `json`, `argparse`).

## 7. Technologies Used
* `subprocess`: Native operating system ICMP ping execution.
* `socket`: Direct TCP connect and port state determination.
* `time.perf_counter`: Microsecond-precision latency benchmarking.
* `pytest`: Test automation.

## 8. Project Structure
```
09_Network_Monitoring_and_Device_Discovery/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── probe.py
│   ├── monitor.py
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
cd COMPUTER_NETWORKS/09_Network_Monitoring_and_Device_Discovery
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Run Single Monitoring Sweep on Localhost
```bash
python app/monitor.py
```

### Step 2: Continuous Multi-Cycle Monitoring (e.g. 3 cycles every 3 seconds)
```bash
python app/monitor.py --cycles 3 --interval 3
```

### Step 3: Monitor Specific Authorized Host and Ports
```bash
python app/monitor.py --targets 127.0.0.1,localhost --ports 80,443,8080,5001 --export logs/my_report.json
```

## 11. How the Network Communication Works
1. **Target IP Resolution:** Hostnames are resolved to IPv4 addresses via `socket.gethostbyname()`.
2. **Layer 3 ICMP Ping:** The monitor invokes a single-packet ping with timeout. The returned output is parsed via regular expressions to extract round-trip latency in milliseconds.
3. **Layer 4 TCP Fallback:** If ICMP is blocked or yields no response, a TCP socket attempt is made to common service ports (80, 443, 22). Receiving either a successful connection (`0`) or an active connection refusal (`ECONNREFUSED` / `10061` / `111`) proves the target host is alive.
4. **Port Inspection:** Dedicated TCP `connect()` probes inspect specified ports, registering `OPEN`, `CLOSED`, or `FILTERED` states.
5. **Uptime Aggregation:** Cumulative metrics update successful vs total checks to maintain the host uptime percentage.

## 12. Example Input
```bash
python app/monitor.py --targets 127.0.0.1 --cycles 2
```

## 13. Example Output
```
======================================================================
         NETWORK MONITORING & DEVICE DISCOVERY SYSTEM
======================================================================
* AUTHORIZATION NOTICE:
  Use only on systems/networks that you own or have explicit
  permission to test. Default scope is strictly local/loopback.
======================================================================

Running Check Cycle 1/2...

================================================================================
          REAL-TIME LOCAL NETWORK MONITORING DASHBOARD
================================================================================
+-----------+------------+--------+--------------+----------+------------+--------------+
| Target    | IP Address | Status | Latency (ms) | Uptime % | Open Ports | Last Checked |
+-----------+------------+--------+--------------+----------+------------+--------------+
| 127.0.0.1 | 127.0.0.1  | ONLINE | 0.45         | 100.0%   | None       | 09:54:12     |
+-----------+------------+--------+--------------+----------+------------+--------------+
================================================================================

[EXPORT] Status report saved to: logs/monitor_report_1728200000.json
```

## 14. Testing
Run the 5 automated unit and probe tests:
```bash
pytest tests/test_basic.py -v
```
Validates localhost ping reachability, dynamic open TCP port discovery, closed port reset recognition, uptime calculation, and automated JSON telemetry generation.

## 15. Real-World Applications
* Infrastructure monitoring platforms: Nagios, Zabbix, PRTG, Datadog.
* Cloud health-check probes (AWS Route 53 health checkers, GCP load balancer uptime probes).
* IoT fleet liveness monitors in industrial smart factories.

## 16. Limitations
* Does not send raw ICMP packets directly from Python without elevated OS privileges (uses native OS ping subprocess or TCP connect fallback).

## 17. Future Enhancements
* SNMP (Simple Network Management Protocol) v2c/v3 telemetry integration (CPU, RAM, bandwidth).
* Web-based live dashboard with WebSocket streaming graphs.

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is network monitoring and why is it vital?
2. What protocol does the `ping` utility use and how does it work?
3. Why does this project implement a TCP connection fallback?
4. What does a TCP `RST` packet signify during a port check?
5. What is the difference between `OPEN`, `CLOSED`, and `FILTERED` ports?
6. How is host uptime percentage calculated?
7. What is Round-Trip Time (RTT) and why is it measured in ms?
8. What is link flapping and how does the monitor detect it?
9. Why is multi-threaded or timed socket probing necessary?
10. What ethical safeguards are built into this monitoring tool?
