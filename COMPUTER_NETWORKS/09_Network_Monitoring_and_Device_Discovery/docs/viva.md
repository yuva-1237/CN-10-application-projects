# Project 09: Network Monitoring & Device Discovery — Viva Questions & Answers

### Q1: What is network monitoring and why is it vital for infrastructure?
**Answer:** Network monitoring is the systematic oversight of a computer network's components (routers, switches, servers, interfaces) to track availability, detect failures, measure latency, and alert administrators before downtime impacts users.

### Q2: What protocol does the `ping` utility use and how does it work?
**Answer:** Ping uses the Internet Control Message Protocol (ICMP) at Layer 3 (Network Layer). It sends an ICMP Echo Request (Type 8) to the target host and listens for an incoming ICMP Echo Reply (Type 0), measuring the elapsed Round-Trip Time (RTT).

### Q3: Why does this project implement a TCP connection fallback for ICMP?
**Answer:** Many corporate networks, cloud platforms, and personal firewalls drop incoming ICMP Echo requests by default to reduce reconnaissance exposure. Probing common TCP ports (e.g. 80, 443) allows reachability detection even when ICMP is blocked.

### Q4: What does a TCP `RST` (Reset) packet signify during a port check?
**Answer:** A TCP `RST` indicates that the target IP address is online and actively responding, but no service is listening on that specific port (the connection is refused). This confirms host liveness.

### Q5: What is the difference between an `OPEN`, `CLOSED`, and `FILTERED` port?
**Answer:**
- `OPEN`: A service is listening and completed the TCP handshake.
- `CLOSED`: The host is reachable but actively resets the connection (no service listening).
- `FILTERED`: No response packet is received before timeout; a firewall or network ACL dropped the request.

### Q6: How is host uptime percentage calculated in this system?
**Answer:**
$$\text{Uptime \%} = \left( \frac{\text{Successful Liveness Checks}}{\text{Total Checks Conducted}} \right) \times 100\%$$

### Q7: What is Round-Trip Time (RTT) and why is it measured in milliseconds?
**Answer:** RTT is the total elapsed time required for a packet to travel from the sender to the destination host and for the acknowledgment or reply to return back. Because modern networks operate at near speed-of-light propagation, millisecond precision is standard.

### Q8: What is link flapping and how does the monitor detect it?
**Answer:** Link flapping occurs when a network node rapidly alternates between `ONLINE` and `OFFLINE` due to loose physical cabling, failing NICs, or routing instability. The monitor tracks state transitions and logs alerts on every status delta.

### Q9: Why is multi-threaded or timed socket probing necessary?
**Answer:** Probing unresponsive offline hosts or filtered ports involves waiting for a network timeout. Without per-socket timeouts or concurrent execution, probing an offline host would freeze the entire monitoring dashboard for multiple seconds.

### Q10: What ethical safeguards are built into this monitoring tool?
**Answer:** The tool is configured by default to target strictly local loopback addresses (`127.0.0.1`, `localhost`) and requires explicit user targets for any external inspection. It includes prominent warnings to only probe networks owned by the operator or tested under explicit authorization.
