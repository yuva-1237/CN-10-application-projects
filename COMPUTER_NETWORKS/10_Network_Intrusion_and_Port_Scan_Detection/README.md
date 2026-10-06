# Network Intrusion & Port Scan Detection System

## 1. Objective
To build an educational defensive Network Intrusion Detection System (NIDS) in Python that monitors inbound connection telemetry across multi-port honeypot listeners, detects horizontal and sequential port reconnaissance using a sliding time-window threshold heuristic, classifies threat severity, and generates forensic security incident reports.

## 2. Problem Statement
Port scanning is universally the first phase of an adversary's cyber-attack lifecycle, allowing attackers to identify open services and unpatched software versions. Modern Security Operations Centers (SOCs) rely on intrusion detection algorithms to catch reconnaissance before exploitation occurs. This project implements a transparent, threshold-based intrusion detection engine over low-level TCP sockets to teach students how behavioral anomaly detection works without relying on complex black-box security suites.

## 3. Computer Networks Concepts Used
* **Network Security & Defense (OSI Layers 3 & 4):** Monitoring incoming IP traffic and TCP handshakes.
* **Intrusion Detection System (IDS) Architecture:** Honeypot listeners, event ingestion, heuristic anomaly detection, and alert generation.
* **Traffic Pattern Analysis:** Distinguishing benign single-service connections from distributed and sequential port sweeps.
* **Sliding Time-Window Counter:** Pruning stale connection telemetry outside a duration window $T$.
* **Defensive Threat Classification:** Evaluating severity (LOW, MEDIUM, HIGH, CRITICAL) based on distinct ports and consecutive sequencing.

## 4. Protocol Used
* TCP over IPv4 (`AF_INET`, `SOCK_STREAM`), monitoring test ports on `127.0.0.1`.

## 5. Architecture
* **`app/detector.py` (`PortScanDetector`):** Core anomaly engine. Tracks per-IP connection attempts, discards expired records outside window $T$, evaluates the distinct port threshold ($|P| \ge N$), detects sequential patterns, and scales severity.
* **`app/ids_engine.py` (`IDSEngine`):** Multi-port socket listener. Listens on local test ports (default: 5010 to 5017), ingests connection attempts, prints formatted alerts, and exports JSON security reports.
* **`app/simulator.py`:** Safe, controlled local test scanner strictly targeting `127.0.0.1` to trigger detection for lab demonstrations.
* **`app/utils.py`:** Security alert formatting and logging helpers.

```
+-------------------------------------------------------------+
|              Inbound Network Connections                    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|            Multi-Port Honeypot Listeners (:5010 - :5017)    |
+-------------------------------------------------------------+
                              | (Extract: src_ip, dst_port, time)
                              v
+-------------------------------------------------------------+
|          Sliding Time-Window Anomaly Engine (T=10s)         |
|  - Prune events older than T                                |
|  - Count distinct destination ports (N >= 5)                |
|  - Classify Pattern: Sequential vs Distributed              |
|  - Compute Severity: MEDIUM / HIGH / CRITICAL               |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               SOC Security Alert Box & JSON Report          |
+-------------------------------------------------------------+
```

## 6. System Requirements
* **Operating System:** Cross-platform (Windows 10/11, Linux, macOS).
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only (`socket`, `threading`, `time`, `uuid`, `json`, `argparse`).

## 7. Technologies Used
* `socket`: Multi-port non-privileged honeypot listeners.
* `threading`: Concurrent socket listener threads.
* `collections.defaultdict`: In-memory telemetry sliding-window queues.
* `pytest`: Test automation.

## 8. Project Structure
```
10_Network_Intrusion_and_Port_Scan_Detection/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── detector.py
│   ├── ids_engine.py
│   ├── simulator.py
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
cd COMPUTER_NETWORKS/10_Network_Intrusion_and_Port_Scan_Detection
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Step 1: Start the Defensive IDS Engine
In Terminal 1:
```bash
python app/ids_engine.py
```
*The IDS will bind local honeypot listeners across ports 5010 to 5017 on 127.0.0.1 and await connection events.*

### Step 2: Trigger a Simulated Test Scan
In Terminal 2:
```bash
python app/simulator.py
```
*This safe test scanner attempts connections across the local test ports, visibly triggering the IDS anomaly heuristic in Terminal 1 in real time.*

### Step 3: Inspect Generated Alert & Exported Report
Terminate the IDS with `Ctrl+C` in Terminal 1 to output the final forensic JSON incident report.

## 11. How the Network Communication Works
1. **Multi-Port Listening:** The IDS initializes multiple TCP sockets listening on high development ports.
2. **Telemetry Ingestion:** When a client attempts a TCP connection, the listener extracts `src_ip`, `dst_port`, and timestamp.
3. **Sliding-Window Pruning:** The detector purges connection entries older than $(t - T)$.
4. **Heuristic Evaluation:** It checks if the number of distinct destination ports touched by the source IP is $\ge N$.
5. **Pattern Recognition:** If ports form consecutive numbers (e.g. 5010, 5011, 5012), it flags `Sequential Port Reconnaissance`.
6. **Alert Emission:** A formatted security incident box is printed with CVSS-aligned severity and mitigation guidance.

## 12. Example Input
```bash
# In Terminal 2 (Local test trigger):
python app/simulator.py
```

## 13. Example Output
```
!====================================================================!
!  [SECURITY ALERT] - SEQUENTIAL PORT RECONNAISSANCE                 !
!====================================================================!
!  Incident ID      : IDS-4A82F10C                                   !
!  Detected At      : 2026-10-06 10:05:12                            !
!  Source IP        : 127.0.0.1                                      !
!  Ports Contacted  : 5010, 5011, 5012, 5013, 5014, 5015             !
!  Total Attempts   : 6                                              !
!  Severity Level   : MEDIUM                                         !
!  Action Taken     : Rate-limit or block 127.0.0.1 at edge firewall !
!====================================================================!
```

## 14. Testing
Run the 5 automated unit and heuristic tests:
```bash
pytest tests/test_basic.py -v
```
Validates normal single-port traffic suppression (zero false positives), distinct port threshold triggers, severity scaling (MEDIUM to HIGH), sliding window time pruning, and JSON security incident report export.

## 15. Real-World Applications
* Intrusion Detection & Prevention Systems: Snort, Suricata, Zeek.
* Automated IP banning daemons: Fail2Ban, CrowdSec.
* Cloud Security Group anomaly monitors (AWS GuardDuty, Azure Sentinel).

## 16. Limitations
* Operates on transport-layer connection attempt telemetry; does not inspect deep application-layer packet payloads.

## 17. Future Enhancements
* Automated iptables / Windows Firewall rule injection upon alert generation.
* Machine learning clustering (k-means) for slow-and-low stealth scan detection.

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is a port scan and why do adversaries perform them?
2. What is an Intrusion Detection System (IDS)?
3. What is the difference between a NIDS and a HIDS?
4. What is the difference between signature-based and anomaly-based detection?
5. How does the sliding-window heuristic algorithm work in this project?
6. What is the difference between a horizontal scan and a vertical scan?
7. What is a honeypot in network security?
8. What does a sequential port scan pattern indicate?
9. Why is alert throttling / cooldown necessary in an IDS?
10. What are the legal and ethical implications of port scanning?
