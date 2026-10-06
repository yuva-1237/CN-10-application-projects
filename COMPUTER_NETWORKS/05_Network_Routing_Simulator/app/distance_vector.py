"""Distance-Vector (Bellman-Ford / RIP) Routing Algorithm Comparison Engine."""
from typing import Dict, List, Optional, Tuple
from app.topology import NetworkTopology

def bellman_ford_routing(topology: NetworkTopology, source: str) -> Dict[str, Tuple[float, Optional[str]]]:
    """Calculate shortest distance and next hop using the Bellman-Ford Distance Vector algorithm.
    
    Iteratively relaxes all edges |V| - 1 times.
    Returns: dest -> (distance, next_hop)
    """
    src = source.strip().upper()
    routers = sorted(topology.routers)
    dist: Dict[str, float] = {r: float("inf") for r in routers}
    next_hop: Dict[str, Optional[str]] = {r: None for r in routers}

    if src not in topology.routers:
        return {}

    dist[src] = 0
    next_hop[src] = "DIRECT"

    # Initialize directly connected neighbors
    for neighbor, cost in topology.get_neighbors(src, only_active=True):
        dist[neighbor] = cost
        next_hop[neighbor] = neighbor

    # Active undirected edges
    edges = []
    for (u, v), props in topology.links.items():
        if props["active"]:
            edges.append((u, v, props["cost"]))
            edges.append((v, u, props["cost"]))

    # Relax edges |V| - 1 times
    for _ in range(max(1, len(routers) - 1)):
        updated = False
        for u, v, cost in edges:
            if dist[u] != float("inf") and dist[u] + cost < dist[v]:
                dist[v] = dist[u] + cost
                # Next hop is inherited from u's next hop
                next_hop[v] = next_hop[u]
                updated = True
        if not updated:
            break

    return {r: (dist[r], next_hop[r]) for r in routers}
