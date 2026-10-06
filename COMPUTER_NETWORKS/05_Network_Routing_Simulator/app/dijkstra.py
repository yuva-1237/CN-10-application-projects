"""Dijkstra's Link-State Routing Algorithm and Routing Table Generator."""
import heapq
from typing import Dict, List, Optional, Tuple
from app.topology import NetworkTopology

def dijkstra_compute(topology: NetworkTopology, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """Compute single-source shortest paths to all reachable routers using Dijkstra's algorithm."""
    src = source.strip().upper()
    dist: Dict[str, float] = {r: float("inf") for r in topology.routers}
    previous: Dict[str, Optional[str]] = {r: None for r in topology.routers}

    if src not in topology.routers:
        return dist, previous

    dist[src] = 0
    pq = [(0, src)]

    while pq:
        curr_dist, u = heapq.heappop(pq)
        if curr_dist > dist[u]:
            continue

        for neighbor, cost in topology.get_neighbors(u, only_active=True):
            alt = curr_dist + cost
            if alt < dist[neighbor]:
                dist[neighbor] = alt
                previous[neighbor] = u
                heapq.heappush(pq, (alt, neighbor))

    return dist, previous

def get_shortest_path(
    topology: NetworkTopology,
    source: str,
    destination: str
) -> Tuple[List[str], float, Optional[str]]:
    """Traceback shortest path from source to destination. Returns (path, cost, next_hop)."""
    src = source.strip().upper()
    dst = destination.strip().upper()

    dist, previous = dijkstra_compute(topology, src)
    if dist.get(dst, float("inf")) == float("inf"):
        return [], float("inf"), None

    # Reconstruct path by walking backwards
    path = []
    curr: Optional[str] = dst
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    if len(path) < 2:
        return path, 0, "LOCAL"

    next_hop = path[1]
    return path, dist[dst], next_hop

def compute_routing_table(topology: NetworkTopology, router: str) -> List[Dict[str, any]]:
    """Generate the complete forwarding / routing table for a given router."""
    r = router.strip().upper()
    table = []

    for dest in sorted(topology.routers):
        if dest == r:
            table.append({
                "destination": dest,
                "cost": 0,
                "next_hop": "DIRECT",
                "path": [r]
            })
        else:
            path, cost, next_hop = get_shortest_path(topology, r, dest)
            if cost != float("inf"):
                table.append({
                    "destination": dest,
                    "cost": int(cost),
                    "next_hop": next_hop,
                    "path": path
                })
            else:
                table.append({
                    "destination": dest,
                    "cost": "UNREACHABLE",
                    "next_hop": "NONE",
                    "path": []
                })
    return table
