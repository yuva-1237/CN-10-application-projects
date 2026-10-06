# Project 05: Network Routing Simulator — Viva Questions & Answers

### Q1: What is routing and at which layer of the OSI model does it operate?
**Answer:** Routing is the process of selecting paths across a network to deliver IP packets from a source host to a destination host. It operates at Layer 3 (Network Layer).

### Q2: What is a routing table?
**Answer:** A data table stored in a router's memory that lists available network destinations, associated metrics (costs), and the designated "next hop" IP address or interface to forward packets toward that destination.

### Q3: How does Dijkstra's algorithm work in Link-State routing (e.g., OSPF)?
**Answer:** Every router acquires the complete global topology via Link-State Advertisements (LSAs). It then treats itself as the root and greedily explores the lowest-cost unvisited neighbors using a priority queue, computing the shortest path tree to all other nodes.

### Q4: What is the difference between static and dynamic routing?
**Answer:** In static routing, paths are manually configured by a network administrator and do not adapt automatically if a link fails. In dynamic routing, routers run routing protocols to automatically discover neighbors, calculate best paths, and re-route traffic around failures.

### Q5: What is "Next Hop"?
**Answer:** The next hop is the immediate adjacent router along the computed optimal path to which a packet must be forwarded next.

### Q6: What happens in this simulator when a link failure occurs?
**Answer:** The link's `active` flag is set to `False`. The Link-State routing engine re-runs Dijkstra's algorithm excluding the inactive link, automatically finding the next lowest-cost alternate detour (e.g. routing $A \rightarrow F$ via $E$ instead of $C$).

### Q7: What is the Bellman-Ford algorithm and which protocol uses it?
**Answer:** Bellman-Ford is a dynamic programming algorithm that iteratively relaxes all edges $|V|-1$ times. It forms the mathematical foundation for Distance-Vector routing protocols like RIP (Routing Information Protocol).

### Q8: What is the "count-to-infinity" problem in Distance-Vector routing?
**Answer:** When a link fails, neighboring routers may continuously exchange outdated, slowly incrementing distance estimates, creating temporary routing loops before realizing the destination is unreachable.

### Q9: Why is Link-State generally preferred over Distance-Vector in large modern enterprise networks?
**Answer:** Link-State protocols (like OSPF and IS-IS) converge significantly faster, support complex multi-metric cost functions, prevent routing loops, and do not suffer from the 15-hop limit imposed by RIP.

### Q10: What is the time complexity of Dijkstra's algorithm using a binary min-heap?
**Answer:** $O((V + E) \log V)$, where $V$ is the number of routers (vertices) and $E$ is the number of links (edges).
