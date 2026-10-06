# TCP Congestion Control Simulator

## 1. Objective
To construct a pedagogical discrete-event simulation of the TCP Congestion Control state machine (RFC 5681), demonstrating Slow Start exponential growth, Congestion Avoidance additive increase (AIMD), Slow Start Threshold (`ssthresh`) transitions, timeout window resets, and TCP Reno Fast Recovery in an interactive terminal environment.

## 2. Problem Statement
Kernel implementations of TCP congestion control operate internally inside the operating system network stack at microsecond intervals. Observing how the congestion window (`cwnd`) responds to individual acknowledgments, timeouts, or triple duplicate ACKs directly on physical networks is challenging for academic viva demonstrations. This simulator provides a transparent, controllable mathematical model where students can configure thresholds and simulate loss events round-by-round.

## 3. Computer Networks Concepts Used
* **Transport Layer (OSI Layer 4):** TCP end-to-end congestion management.
* **Congestion Window (`cwnd`):** Sender-side constraint on maximum outstanding unacknowledged bytes.
* **Slow Start:** Exponential growth phase doubling `cwnd` each transmission round (RTT).
* **Slow Start Threshold (`ssthresh`):** Boundary demarcating exponential vs. linear growth.
* **Congestion Avoidance & AIMD:** Additive Increase (+1 MSS per RTT), Multiplicative Decrease (halving `ssthresh`).
* **Loss Event Handling:** Contrasting Timeout (hard collapse to `cwnd=1`) with Fast Retransmit / Fast Recovery (Reno vs. Tahoe).

## 4. Protocol Used
* Mathematical simulation of TCP Reno and TCP Tahoe state machines (RFC 5681 / RFC 2581).

## 5. Architecture
* **`app/tcp_engine.py` (`TCPCongestionEngine`):** State machine managing `cwnd`, `ssthresh`, operational states (`SLOW_START`, `CONGESTION_AVOIDANCE`, `FAST_RECOVERY`), and transitions based on scheduled loss events.
* **`app/simulator.py`:** CLI entry point executing the simulation, printing round-by-round trace logs, and plotting the ASCII congestion window progression.
* **`app/utils.py` (`render_ascii_graph`):** Scaled ASCII canvas plotter visualizing the AIMD "sawtooth" curve.

```
       +------------------------------------+
       |  Config: cwnd=1, ssthresh=16       |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  Slow Start (Exponential: * 2)     |
       +------------------------------------+
                         | (cwnd >= ssthresh)
                         v
       +------------------------------------+
       |  Congestion Avoidance (Linear: +1) |
       +------------------------------------+
              |                       |
       (Timeout Loss)       (3 Duplicate ACKs)
              |                       |
              v                       v
     [Reset: cwnd = 1]     [Fast Recovery: cwnd = ssthresh]
     [ssthresh = cwnd/2]   [ssthresh = cwnd/2]
```

## 6. System Requirements
* **Operating System:** Windows 10/11, Linux, or macOS.
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only.

## 7. Technologies Used
* `dataclasses`: Round logging and state representation.
* Standard Python math and collections.
* `pytest`: Automated test framework.

## 8. Project Structure
```
07_TCP_Congestion_Control_Simulator/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── tcp_engine.py
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
cd COMPUTER_NETWORKS/07_TCP_Congestion_Control_Simulator
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Default Simulation (TCP Reno, 25 Rounds)
```bash
python app/simulator.py
```

### Compare with TCP Tahoe
```bash
python app/simulator.py --variant TAHOE --loss "8:TIMEOUT,16:TRIPLE_DUP_ACK"
```

### Custom Rounds and Thresholds
```bash
python app/simulator.py --rounds 30 --ssthresh 32 --loss "10:TIMEOUT"
```

## 11. How the Network Communication Works
1. **Initial State:** Sockets start with `cwnd = 1` MSS and `ssthresh = 16` in `SLOW_START`.
2. **Slow Start Exponential Probe:** Senders transmit `cwnd` packets; receiving ACKs doubles `cwnd` every RTT ($1 \rightarrow 2 \rightarrow 4 \rightarrow 8 \rightarrow 16$).
3. **Threshold Reached:** Once `cwnd >= ssthresh`, state becomes `CONGESTION_AVOIDANCE`.
4. **AIMD Probing:** In Congestion Avoidance, each full window of ACKs increases `cwnd` linearly by $+1$ MSS ($16 \rightarrow 17 \rightarrow 18 \rightarrow \dots$).
5. **Loss Detection:**
   - **Timeout:** Sockets reset `cwnd = 1`, halve `ssthresh`, and revert to Slow Start.
   - **Triple Duplicate ACKs (Reno):** Sockets enter Fast Recovery, halving `ssthresh` and resuming linear growth from `cwnd = ssthresh`.

## 12. Example Input
```bash
python app/simulator.py --variant RENO --loss "6:TIMEOUT,14:TRIPLE_DUP_ACK"
```

## 13. Example Output
```
======================================================================
           TCP CONGESTION CONTROL SIMULATOR [SIMULATION MODE]
======================================================================
Algorithm Variant : TCP RENO
Initial cwnd      : 1.0 MSS
Initial ssthresh  : 16.0 MSS
Simulation Window : 25 Rounds (RTTs)

+-------+----------+----------+-----------------------+-----------------+----------------------------------------------------+
| Round | cwnd     | ssthresh | State                 | Event           | Actions Taken & Academic Notes                     |
+-------+----------+----------+-----------------------+-----------------+----------------------------------------------------+
|     1 |      2.0 |     16.0 | SLOW_START            | ACK_RECEIVED    | Slow Start exponential growth: cwnd doubled.       |
|     2 |      4.0 |     16.0 | SLOW_START            | ACK_RECEIVED    | Slow Start exponential growth: cwnd doubled.       |
|     3 |      8.0 |     16.0 | SLOW_START            | ACK_RECEIVED    | Slow Start exponential growth: cwnd doubled.       |
|     4 |     16.0 |     16.0 | CONGESTION_AVOIDANCE  | ACK_RECEIVED    | Reached ssthresh (16). Switched to Congestion Av...|
|     5 |     17.0 |     16.0 | CONGESTION_AVOIDANCE  | ACK_RECEIVED    | Congestion Avoidance linear growth (AIMD): +1.     |
|     6 |      1.0 |      8.0 | SLOW_START            | TIMEOUT         | Timeout! ssthresh halved to 8, cwnd reset to 1.    |
...

CONGESTION WINDOW EVOLUTION GRAPH (cwnd vs Round):
  ^ cwnd (MSS) [Peak: 18.0]
  |
  18 |                 *
  15 |            *
  12 |                         * * *
   9 |       *
   6 |     *
   3 |   *
   0 +---------------------------------> Transmission Round (RTT)
       1   5   10   15   20   25
```

## 14. Testing
Run the 5 automated unit tests:
```bash
pytest tests/test_basic.py -v
```
Validates exponential growth in Slow Start, transition to Congestion Avoidance at ssthresh, linear growth (AIMD), timeout recovery, and Reno vs Tahoe duplicate ACK behavior.

## 15. Real-World Applications
* Linux kernel TCP stack (TCP Reno, Cubic, BBR).
* Streaming video player bitrate pacing (DASH, HLS).
* WAN optimization controllers.

## 16. Limitations
* Discrete-round simulation rather than microsecond continuous network packet queueing.

## 17. Future Enhancements
* Implementation of TCP Cubic (polynomial growth) and TCP BBR (Bottleneck Bandwidth and RTT model).

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is congestion collapse?
2. What is the Congestion Window (`cwnd`)?
3. What is the difference between Flow Control and Congestion Control?
4. How does the Slow Start phase work?
5. What is Congestion Avoidance and AIMD?
6. What is `ssthresh`?
7. What is the difference between a Timeout and Triple Duplicate ACKs?
8. How does TCP Reno differ from TCP Tahoe?
9. Why does TCP congestion control produce a "sawtooth" pattern?
10. What are modern TCP congestion control algorithms beyond Reno?
