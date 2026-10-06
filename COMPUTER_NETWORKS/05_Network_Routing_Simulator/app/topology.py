"""Network Topology Graph Model."""
from typing import Dict, List, Optional, Set, Tuple

class NetworkTopology:
    def __init__(self):
        self.routers: Set[str] = set()
        # (u, v) in canonical sorted order -> {"cost": int, "active": bool}
        self.links: Dict[Tuple[str, str], Dict[str, any]] = {}

    def add_router(self, name: str) -> bool:
        """Add a new router node to the topology."""
        clean = name.strip().upper()
        if not clean or clean in self.routers:
            return False
        self.routers.add(clean)
        return True

    def remove_router(self, name: str) -> bool:
        """Remove a router node and all its incident links."""
        clean = name.strip().upper()
        if clean not in self.routers:
            return False
        self.routers.remove(clean)
        # Remove incident links
        to_del = [edge for edge in self.links if clean in edge]
        for edge in to_del:
            del self.links[edge]
        return True

    def add_link(self, u: str, v: str, cost: int) -> bool:
        """Add or update an undirected weighted link between two routers."""
        u_clean, v_clean = u.strip().upper(), v.strip().upper()
        if u_clean == v_clean or u_clean not in self.routers or v_clean not in self.routers:
            return False
        if cost <= 0:
            return False

        edge = tuple(sorted((u_clean, v_clean)))
        self.links[edge] = {"cost": cost, "active": True}
        return True

    def remove_link(self, u: str, v: str) -> bool:
        """Remove a link between two routers."""
        edge = tuple(sorted((u.strip().upper(), v.strip().upper())))
        if edge in self.links:
            del self.links[edge]
            return True
        return False

    def set_link_status(self, u: str, v: str, active: bool) -> bool:
        """Simulate link failure (active=False) or link recovery (active=True)."""
        edge = tuple(sorted((u.strip().upper(), v.strip().upper())))
        if edge in self.links:
            self.links[edge]["active"] = active
            return True
        return False

    def get_neighbors(self, router: str, only_active: bool = True) -> List[Tuple[str, int]]:
        """Return list of (neighbor_router, cost) for a given router."""
        clean = router.strip().upper()
        neighbors = []
        for (u, v), props in self.links.items():
            if only_active and not props["active"]:
                continue
            if clean == u:
                neighbors.append((v, props["cost"]))
            elif clean == v:
                neighbors.append((u, props["cost"]))
        return neighbors

    def build_default_topology(self) -> None:
        """Create a standard 6-node academic campus network topology.
        
           (1)       (2)
        A ----- B -------- C
        |       |          |
     (4)|       |(3)       |(1)
        |       |          |
        D ----- E -------- F
           (5)       (2)
        """
        self.routers.clear()
        self.links.clear()

        for r in ["A", "B", "C", "D", "E", "F"]:
            self.add_router(r)

        self.add_link("A", "B", 1)
        self.add_link("B", "C", 2)
        self.add_link("A", "D", 4)
        self.add_link("B", "E", 3)
        self.add_link("C", "F", 1)
        self.add_link("D", "E", 5)
        self.add_link("E", "F", 2)
