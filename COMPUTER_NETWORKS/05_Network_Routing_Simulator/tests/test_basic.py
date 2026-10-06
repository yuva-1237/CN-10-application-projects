"""Automated tests for Project 05: Network Routing Simulator."""
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.dijkstra import compute_routing_table, get_shortest_path
from app.distance_vector import bellman_ford_routing
from app.topology import NetworkTopology

def test_01_topology_creation_and_modification():
    """Test 1: Adding and removing routers and links in the topology graph."""
    topo = NetworkTopology()
    assert topo.add_router("R1") is True
    assert topo.add_router("R2") is True
    assert topo.add_router("R1") is False  # Duplicate should be rejected

    assert topo.add_link("R1", "R2", 10) is True
    assert topo.add_link("R1", "R2", -5) is False  # Negative cost rejected
    assert ("R1", "R2") in topo.links
    assert topo.links[("R1", "R2")]["cost"] == 10

    assert topo.remove_link("R1", "R2") is True
    assert ("R1", "R2") not in topo.links

def test_02_dijkstra_shortest_path_default_topology():
    """Test 2: Compute shortest path A -> F on default 6-node campus network.
    
    Paths:
    A -> B -> C -> F : Cost = 1 + 2 + 1 = 4 (Optimal)
    A -> B -> E -> F : Cost = 1 + 3 + 2 = 6
    A -> D -> E -> F : Cost = 4 + 5 + 2 = 11
    """
    topo = NetworkTopology()
    topo.build_default_topology()

    path, cost, next_hop = get_shortest_path(topo, "A", "F")
    assert path == ["A", "B", "C", "F"]
    assert cost == 4
    assert next_hop == "B"

def test_03_routing_table_generation():
    """Test 3: Router A computes complete routing table covering all destinations."""
    topo = NetworkTopology()
    topo.build_default_topology()

    table = compute_routing_table(topo, "A")
    table_map = {row["destination"]: row for row in table}

    assert "A" in table_map and table_map["A"]["cost"] == 0 and table_map["A"]["next_hop"] == "DIRECT"
    assert "B" in table_map and table_map["B"]["cost"] == 1 and table_map["B"]["next_hop"] == "B"
    assert "C" in table_map and table_map["C"]["cost"] == 3 and table_map["C"]["next_hop"] == "B"
    assert "D" in table_map and table_map["D"]["cost"] == 4 and table_map["D"]["next_hop"] == "D"
    assert "F" in table_map and table_map["F"]["cost"] == 4 and table_map["F"]["next_hop"] == "B"

def test_04_link_failure_and_dynamic_route_recovery():
    """Test 4: Fail link C <-> F; Dijkstra dynamically recalculates detour via E -> F."""
    topo = NetworkTopology()
    topo.build_default_topology()

    # Initial optimal path: A -> B -> C -> F (cost 4)
    path1, cost1, _ = get_shortest_path(topo, "A", "F")
    assert path1 == ["A", "B", "C", "F"]
    assert cost1 == 4

    # Cut link C-F
    assert topo.set_link_status("C", "F", False) is True

    # Recalculate route: Detour must take A -> B -> E -> F (cost = 1 + 3 + 2 = 6)
    path2, cost2, next_hop2 = get_shortest_path(topo, "A", "F")
    assert path2 == ["A", "B", "E", "F"]
    assert cost2 == 6
    assert next_hop2 == "B"

def test_05_disconnected_graph_handling():
    """Test 5: Completely isolated node produces unreachable status and infinite cost."""
    topo = NetworkTopology()
    topo.build_default_topology()
    topo.add_router("ISOLATED")

    path, cost, next_hop = get_shortest_path(topo, "A", "ISOLATED")
    assert path == []
    assert cost == float("inf")
    assert next_hop is None
