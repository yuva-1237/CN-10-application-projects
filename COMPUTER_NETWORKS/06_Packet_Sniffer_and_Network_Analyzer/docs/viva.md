# Project 06: Packet Sniffer & Network Analyzer — Viva Questions & Answers

### Q1: What is a packet sniffer?
**Answer:** A packet sniffer (or packet analyzer) is a software program or hardware device that intercepts, decodes, and inspects data packets as they flow across a computer network or interface.

### Q2: What is "promiscuous mode" on a Network Interface Card (NIC)?
**Answer:** By default, a NIC only processes frames addressed directly to its own MAC address, broadcast frames, or joined multicast groups. In promiscuous mode, the NIC passes all incoming frames to the operating system, regardless of target MAC address.

### Q3: Why does packet sniffing require administrator or root privileges?
**Answer:** Opening raw sockets (`SOCK_RAW`) bypasses the OS transport layer stack and allows direct observation of all raw packets crossing network hardware. Operating systems restrict this capability to root/admin to safeguard user privacy and credentials.

### Q4: How is an IP header's length (IHL) converted into bytes?
**Answer:** The Internet Header Length (IHL) is stored in 4 bits as the number of 32-bit (4-byte) words. Multiplying the IHL value by 4 gives the total header size in bytes (e.g. standard $\text{IHL} = 5 \implies 5 \times 4 = 20\text{ bytes}$).

### Q5: How do we determine which transport protocol is carried inside an IPv4 packet?
**Answer:** By inspecting the 8-bit `Protocol` field at byte offset 9 of the IPv4 header: `1` indicates ICMP, `6` indicates TCP, and `17` indicates UDP.

### Q6: What are the primary TCP flags and what do they mean?
**Answer:**
- `SYN`: Synchronize sequence numbers (connection initiation).
- `ACK`: Acknowledgment field is significant.
- `FIN`: Finish; sender has finished sending data.
- `RST`: Reset connection.
- `PSH`: Push; deliver data directly to application without buffering.
- `URG`: Urgent pointer field is valid.

### Q7: What is the difference between TCP and UDP headers?
**Answer:** A standard TCP header is at least 20 bytes long and contains sequence numbers, ACK numbers, window sizing, and flags for reliability. A UDP header is fixed at only 8 bytes containing source port, destination port, datagram length, and checksum.

### Q8: What does ICMP Type 8 and Type 0 represent?
**Answer:** Type 8 is an ICMP Echo Request (used by the `ping` utility to test reachability). Type 0 is the corresponding ICMP Echo Reply returned by the target host.

### Q9: What is the purpose of the TTL (Time-To-Live) field in the IP header?
**Answer:** TTL is an 8-bit counter decremented by 1 at each router hop. If TTL reaches 0, the packet is discarded and an ICMP Time Exceeded message is returned, preventing packets from looping infinitely in routing loops.

### Q10: What are the ethical and legal boundaries of packet sniffing?
**Answer:** Packet sniffing may only be conducted on networks and devices owned by the analyst or where explicit, written authorization has been granted. Unauthorized sniffing on public or third-party networks constitutes illegal wiretapping and unauthorized surveillance.
