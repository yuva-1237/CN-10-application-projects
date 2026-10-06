# Network Routing Simulator

## 1. Objective
To build an interactive, graph-theoretical network routing simulator in Python that models Link-State (Dijkstra) and Distance-Vector (Bellman-Ford) routing algorithms, dynamically computes forwarding tables and next hops, and visualizes route recalculation during simulated network link failures.

## 2. Problem Statement
In physical routing hardware (Cisco, Juniper), routing table calculation occurs inside closed firmware microkernels, making it difficult for students to inspect the mathematical path convergence, link metric weighting, and fault tolerance mechanisms. This project provides a transparent simulation environment where network topologies can be modified, link costs tuned, and cable cuts simulated in real time.

## 3. Computer Networks Concepts Used
* **Network Layer (OSI Layer 3):** IP routing and forwarding paradigm.
* **Graph Topology Model:** Routers as vertices ($V$), bidirectional links as weighted edges ($E$).
* **Link-State Routing:** Dijkstra's Single-Source Shortest Path algorithm with min-heaps (`heapq`).
* **Distance-Vector Routing:** Bellman-Ford edge relaxation ($|V|-1$ iterations).
* **Forwarding / Routing Tables:** Mapping destinations to metrics, next hops, and complete interface paths.
* **Dynamic Network Convergence:** Real-time route failover upon simulated interface/cable cuts.

## 4. Protocol Used
* Simulated IP routing and forwarding logic (modeling OSPF Link-State and RIP Distance-Vector behavior).

## 5. Architecture
* **`app/topology.py` (`NetworkTopology`):** Manages vertices (routers), weighted edges (links), active/down link states, and builds default campus topologies.
* **`app/dijkstra.py`:** Implements Dijkstra's algorithm with priority queues, path traceback, and routing table synthesis.
* **`app/distance_vector.py`:** Implements Bellman-Ford algorithm to compare convergence and next-hop selection.
* **`app/simulator.py`:** Interactive CLI providing topology visualization, route queries, failure simulations, and side-by-side algorithm comparison.

```
      (Cost 1)             (Cost 2)
  [A] ----------- [B] ----------------- [C]
   |               |                     |
(4)|            (3)|                  (1)|
   |               |                     |
  [D] ----------- [E] ----------------- [F]
      (Cost 5)             (Cost 2)
```

## 6. System Requirements
* **Operating System:** Windows 10/11, Linux, or macOS.
* **Python Runtime:** Python 3.11+
* **Dependencies:** Python Standard Library only (`heapq`, `typing`, `argparse`).

## 7. Technologies Used
* `heapq`: Fast binary min-heap for Dijkstra priority queue.
* `dataclasses` / standard collections: Topology adjacency model.
* `pytest`: Automated test framework.

## 8. Project Structure
```
05_Network_Routing_Simulator/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── topology.py
│   ├── dijkstra.py
│   ├── distance_vector.py
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
cd COMPUTER_NETWORKS/05_Network_Routing_Simulator
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## 10. How to Run

### Interactive Menu Mode
```bash
python app/simulator.py
```

### Direct CLI One-Shot Path Calculation
```bash
python app/simulator.py --src A --dst F
```

## 11. How the Network Communication Works
1. **Topology Graph Initialization:** Routers and active links with positive metrics are loaded into memory.
2. **Dijkstra Link-State Execution:** For any queried source node, a min-heap explores adjacent neighbors in order of lowest cumulative metric, maintaining a predecessor map.
3. **Traceback & Next-Hop Extraction:** The shortest path is reconstructed by traversing backwards from destination to source; the immediate second hop along the path is designated as the `NEXT HOP`.
4. **Failure Simulation:** Disabling a link (`set_link_status(u, v, False)`) updates the graph state. Running route calculation identifies the next optimal path.

## 12. Example Input
```
Option 2: Compute Shortest Path
Source: A
Destination: F
```

## 13. Example Output
```
============================================================
  SHORTEST PATH COMPUTATION: A -> F
============================================================
SOURCE       : A
DESTINATION  : F
TOTAL COST   : 4
NEXT HOP     : B
OPTIMAL PATH : A -> B -> C -> F
============================================================

[Simulating Failure of Link C <---> F]
============================================================
  SHORTEST PATH COMPUTATION: A -> F
============================================================
SOURCE       : A
DESTINATION  : F
TOTAL COST   : 6
NEXT HOP     : B
OPTIMAL PATH : A -> B -> E -> F
============================================================
```

## 14. Testing
Run the 5 automated test cases:
```bash
pytest tests/test_basic.py -v
```
Validates topology node and link creation, Dijkstra optimal path computation on a 6-node network, routing table synthesis, dynamic link failure detour recalculation, and isolated network partition handling.

## 15. Real-World Applications
* **OSPF (Open Shortest Path First):** Enterprise IGP protocol based on Dijkstra's algorithm.
* **IS-IS (Intermediate System to Intermediate System):** ISP core backbone routing.
* **Autonomous Vehicle & Drone Mesh Networks:** Dynamic path recalculation in ad-hoc vehicular networks (VANETs).

## 16. Limitations
* Operates as a logical software simulation rather than binding to physical network adapters or emitting real Ethernet frames.

## 17. Future Enhancements
* Multi-area OSPF hierarchical routing simulation.
* Real-time packet forwarding simulation with animated hop-by-hop latency and queue delays.

## 18. Viva Questions
*(See [viva.md](docs/viva.md) for full answers)*
1. What is routing and at which layer does it operate?
2. What is a routing table?
3. How does Dijkstra's algorithm work in Link-State routing?
4. What is the difference between static and dynamic routing?
5. What is "Next Hop"?
6. What happens in this simulator when a link failure occurs?
7. What is the Bellman-Ford algorithm and which protocol uses it?
8. What is the "count-to-infinity" problem?
9. Why is Link-State preferred over Distance-Vector in modern networks?
10. What is the time complexity of Dijkstra's algorithm with a binary min-heap?
