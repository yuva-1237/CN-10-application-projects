# Project 10: Network Intrusion & Port Scan Detection — Viva Questions & Answers

### Q1: What is a port scan and why do adversaries perform them?
**Answer:** A port scan is a reconnaissance technique where an attacker probes a range of server ports on a target host to identify active listening services, daemon versions, and potential security vulnerabilities prior to exploitation.

### Q2: What is an Intrusion Detection System (IDS)?
**Answer:** An IDS is a security monitoring tool that inspects network traffic or system logs to identify unauthorized activity, policy violations, or known adversarial attack signatures.

### Q3: What is the difference between a NIDS and a HIDS?
**Answer:**
- **NIDS (Network IDS):** Analyzes network traffic packets crossing network segments or interfaces (e.g. Snort, Zeek).
- **HIDS (Host-based IDS):** Analyzes local system events, system call logs, file integrity, and authentication attempts on a specific endpoint host (e.g. OSSEC, Wazuh).

### Q4: What is the difference between signature-based and anomaly-based detection?
**Answer:**
- **Signature-based:** Matches traffic against predefined patterns or byte strings of known attacks (fails against novel zero-day attacks).
- **Anomaly-based:** Establishes a baseline of normal behavior and flags statistical deviations or heuristic threshold violations (detects unknown attack patterns).

### Q5: How does the sliding-window heuristic algorithm work in this project?
**Answer:** It tracks connection events per source IP within a rolling time window of $T$ seconds. If the number of distinct destination ports touched by that IP exceeds threshold $N$, an intrusion alert is generated. Events older than $T$ seconds are continuously pruned.

### Q6: What is the difference between a horizontal scan and a vertical scan?
**Answer:**
- **Horizontal Scan:** Scanning a single port (or few ports) across many different target IP addresses on a subnet.
- **Vertical Scan:** Scanning many different ports on a single specific target host (the primary pattern detected in this project).

### Q7: What is a honeypot in network security?
**Answer:** A honeypot is a decoy network service or host deliberately exposed to monitor, log, and study unauthorized connection attempts and adversarial behavior without hosting production data.

### Q8: What does a sequential port scan pattern indicate?
**Answer:** Sequential port scans probe ports in numeric order (e.g. 21, 22, 23, 24, 25), typical of basic scanning scripts and default scanner configurations. The detector recognizes consecutive port increments and flags the reconnaissance pattern.

### Q9: Why is alert throttling / cooldown necessary in an IDS?
**Answer:** Without cooldown suppression, an attacker scanning 1,000 ports would generate 995 redundant alerts within seconds, overwhelming security analysts (alert fatigue) and consuming excessive disk and database resources.

### Q10: What are the legal and ethical implications of port scanning?
**Answer:** Port scanning third-party external networks without explicit authorization may violate computer misuse legislation (e.g. CFAA in the US, IT Act in India, CMA in the UK) and terms of service of internet service providers. All testing must be confined to localhost or authorized lab networks.
