# Project 07: TCP Congestion Control Simulator — Viva Questions & Answers

### Q1: What is congestion collapse in computer networks?
**Answer:** Congestion collapse occurs when a network is swamped with more traffic than intermediate routers can buffer, causing severe packet drops. Senders aggressively retransmit dropped packets, consuming even more bandwidth and reducing useful throughput to near zero.

### Q2: What is the Congestion Window (`cwnd`)?
**Answer:** `cwnd` is a sender-side variable that limits the maximum amount of unacknowledged data (in bytes or Maximum Segment Size / MSS) that a TCP sender can transmit into the network before waiting for an ACK.

### Q3: What is the difference between Flow Control and Congestion Control?
**Answer:** Flow control prevents the sender from overwhelming the specific receiving host (governed by the receiver's advertised window `rwnd`). Congestion control prevents senders collectively from overwhelming intermediate network routers and links (governed by `cwnd`).

### Q4: How does the Slow Start phase work?
**Answer:** Despite its name, Slow Start increases transmission rate exponentially. Starting at 1 MSS, `cwnd` doubles every round trip time (RTT) until it reaches the slow start threshold (`ssthresh`).

### Q5: What is Congestion Avoidance and AIMD?
**Answer:** Once `cwnd >= ssthresh`, TCP enters Congestion Avoidance. It switches from exponential growth to Additive Increase, Multiplicative Decrease (AIMD): increasing `cwnd` linearly by +1 MSS per RTT, and cutting it upon packet loss.

### Q6: What is `ssthresh`?
**Answer:** The Slow Start Threshold (`ssthresh`) is a cutoff metric that determines whether TCP is in Slow Start (exponential growth) or Congestion Avoidance (linear growth).

### Q7: What is the difference between a Timeout and Triple Duplicate ACKs?
**Answer:** A Timeout means no ACKs are arriving, indicating severe network congestion or a broken link. Triple duplicate ACKs indicate that subsequent packets are still arriving at the receiver, implying an isolated segment drop rather than total collapse.

### Q8: How does TCP Reno differ from TCP Tahoe on Triple Duplicate ACKs?
**Answer:** Tahoe resets `cwnd = 1` and reverts to Slow Start on both timeouts and duplicate ACKs. Reno introduces Fast Recovery: on 3 duplicate ACKs, it sets `ssthresh = cwnd/2`, sets `cwnd = ssthresh`, and continues with linear Congestion Avoidance without dropping back to 1.

### Q9: Why does TCP congestion control produce a "sawtooth" pattern?
**Answer:** Additive increase gradually probes for available bandwidth by climbing linearly. When link capacity is exceeded, multiplicative decrease sharply halves the window, resulting in a recurring sawtooth waveform over time.

### Q10: What are modern TCP congestion control algorithms beyond Reno?
**Answer:** Modern algorithms include TCP Cubic (default in Linux, uses a cubic function for faster convergence on high-bandwidth delay product networks) and Google BBR (Bottleneck Bandwidth and RTT, which models pacing rather than loss-based throttling).
