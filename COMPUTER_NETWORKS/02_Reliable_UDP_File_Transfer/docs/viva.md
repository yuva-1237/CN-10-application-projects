# Project 02: Reliable UDP File Transfer — Viva Questions & Answers

### Q1: What makes UDP inherently "unreliable"?
**Answer:** UDP (User Datagram Protocol) does not establish a connection, does not track sequence numbers, does not acknowledge receipt of packets, does not retransmit lost packets, does not prevent duplicates, and does not perform flow or congestion control.

### Q2: What is an ARQ protocol?
**Answer:** Automatic Repeat reQuest (ARQ) is an error-control mechanism for data transmission that utilizes acknowledgments (ACKs) and timeouts to achieve reliable data transmission over an unreliable communication channel.

### Q3: How does this project achieve reliability over UDP?
**Answer:** By implementing four core components at the application layer: (1) packet sequencing to reorder chunks, (2) explicit ACK datagrams from the receiver, (3) sender socket timeouts, and (4) automatic retransmission of unacknowledged packets.

### Q4: Why is a sequence number needed in the packet header?
**Answer:** Datagrams may arrive out of order or be duplicated. The sequence number allows the receiver to identify where each chunk belongs in the reconstructed file and ignore duplicate transmissions.

### Q5: What is Stop-and-Wait ARQ?
**Answer:** It is a flow control and reliability mechanism where the sender transmits a single packet, starts a timer, and waits for an acknowledgment from the receiver before transmitting the next packet. If the timer expires before the ACK arrives, the sender retransmits the same packet.

### Q6: Why do we use CRC-32 on each datagram in addition to UDP's built-in checksum?
**Answer:** UDP's native checksum is an optional 16-bit one's complement sum with a high collision probability for multiple bit flips. A 32-bit Cyclic Redundancy Check (CRC-32) offers significantly stronger error detection for detecting corrupted bits in flight.

### Q7: What is MTU and why is our chunk size set to 1024 bytes?
**Answer:** Maximum Transmission Unit (MTU) is the largest size of a packet that can be transmitted across a physical link without fragmentation (standard Ethernet MTU is 1500 bytes). A 1024-byte payload + 17-byte header stays comfortably below 1500 bytes, avoiding IP layer fragmentation.

### Q8: What happens if an ACK packet itself gets lost?
**Answer:** If the receiver receives the data packet and sends an ACK, but the ACK is lost in transit, the sender's timer expires and it retransmits the packet. The receiver recognizes the sequence number as already received, discards the duplicate payload to avoid corruption, and re-sends the ACK.

### Q9: What is the trade-off between TCP and Application-Level Reliable UDP?
**Answer:** TCP handles reliability inside the OS kernel with complex flow/congestion control, but introduces connection setup latency and head-of-line blocking. Application-level UDP (like Google QUIC / HTTP/3) provides customizable reliability, no head-of-line blocking across independent streams, and immediate transmission.

### Q10: Why do we verify SHA-256 at the end of the transfer?
**Answer:** CRC-32 verifies packet-level integrity during transit, while the end-to-end SHA-256 cryptographic hash ensures that the completely reassembled file on the receiver's disk is identical byte-for-byte to the sender's original file.
