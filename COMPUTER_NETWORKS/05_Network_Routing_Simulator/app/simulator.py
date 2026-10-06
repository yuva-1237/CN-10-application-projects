"""Interactive CLI Simulator for Network Routing and Dijkstra / Distance Vector."""
import argparse
import sys
from pathlib import Path

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.dijkstra import compute_routing_table, get_shortest_path
from app.distance_vector import bellman_ford_routing
from app.topology import NetworkTopology
from app.utils import format_ascii_table, setup_logger

logger = setup_logger("Routing_Simulator")

class RoutingSimulator:
    def __init__(self):
        self.topology = NetworkTopology()
        self.topology.build_default_topology()

    def show_topology(self) -> None:
        """Display current router nodes and link states."""
        print("\n" + "=" * 60)
        print("  CURRENT NETWORK TOPOLOGY [SIMULATION MODE]")
        print("=" * 60)
        print(f"Active Routers: {', '.join(sorted(self.topology.routers))}")
        print("\nConfigured Links:")

        headers = ["Link", "Cost", "Status"]
        rows = []
        for (u, v), props in sorted(self.topology.links.items()):
            status = "UP (Active)" if props["active"] else "DOWN (FAILED)"
            rows.append([f"{u} <---> {v}", str(props["cost"]), status])
        print(format_ascii_table(headers, rows))

    def show_path(self, src: str, dst: str) -> None:
        """Calculate and display shortest path from source to destination."""
        src, dst = src.strip().upper(), dst.strip().upper()
        if src not in self.topology.routers or dst not in self.topology.routers:
            print(f"Error: One or both routers ('{src}', '{dst}') not found in topology.")
            return

        path, cost, next_hop = get_shortest_path(self.topology, src, dst)
        print("\n" + "=" * 60)
        print(f"  SHORTEST PATH COMPUTATION: {src} -> {dst}")
        print("=" * 60)
        if cost == float("inf"):
            print(f"DESTINATION UNREACHABLE: No active network path exists between {src} and {dst}.")
        else:
            path_str = " -> ".join(path)
            print(f"SOURCE       : {src}")
            print(f"DESTINATION  : {dst}")
            print(f"TOTAL COST   : {int(cost)}")
            print(f"NEXT HOP     : {next_hop}")
            print(f"OPTIMAL PATH : {path_str}")
        print("=" * 60)

    def show_routing_table(self, router: str) -> None:
        """Display the complete calculated routing table for a given router."""
        r = router.strip().upper()
        if r not in self.topology.routers:
            print(f"Error: Router '{r}' does not exist.")
            return

        table = compute_routing_table(self.topology, r)
        print("\n" + "=" * 60)
        print(f"  ROUTING TABLE FOR NODE [{r}] (Dijkstra Link-State)")
        print("=" * 60)

        headers = ["Destination", "Next Hop", "Cost", "Full Path"]
        rows = []
        for entry in table:
            path_str = " -> ".join(entry["path"]) if entry["path"] else "N/A"
            rows.append([entry["destination"], str(entry["next_hop"]), str(entry["cost"]), path_str])
        print(format_ascii_table(headers, rows))

    def simulate_failure(self, u: str, v: str) -> None:
        """Simulate a physical cable cut / interface failure."""
        u, v = u.strip().upper(), v.strip().upper()
        if self.topology.set_link_status(u, v, False):
            print(f"\n[EVENT] Link {u} <---> {v} marked as DOWN (Simulated Failure).")
        else:
            print(f"Error: Link {u} <---> {v} does not exist.")

    def simulate_recovery(self, u: str, v: str) -> None:
        """Simulate link restoration."""
        u, v = u.strip().upper(), v.strip().upper()
        if self.topology.set_link_status(u, v, True):
            print(f"\n[EVENT] Link {u} <---> {v} marked as UP (Restored).")
        else:
            print(f"Error: Link {u} <---> {v} does not exist.")

    def compare_algorithms(self, src: str) -> None:
        """Compare Link-State (Dijkstra) vs Distance-Vector (Bellman-Ford)."""
        src = src.strip().upper()
        if src not in self.topology.routers:
            print(f"Error: Router '{src}' does not exist.")
            return

        dijkstra_table = compute_routing_table(self.topology, src)
        bf_results = bellman_ford_routing(self.topology, src)

        print("\n" + "=" * 60)
        print(f"  ALGORITHM CONVERGENCE COMPARISON FROM NODE [{src}]")
        print("=" * 60)

        headers = ["Destination", "Dijkstra Next-Hop", "Dijkstra Cost", "Bellman-Ford Next-Hop", "Bellman-Ford Cost"]
        rows = []
        for entry in dijkstra_table:
            dst = entry["destination"]
            bf_cost, bf_nh = bf_results.get(dst, (float("inf"), "NONE"))
            bf_cost_str = str(int(bf_cost)) if bf_cost != float("inf") else "INF"
            rows.append([
                dst,
                str(entry["next_hop"]),
                str(entry["cost"]),
                str(bf_nh),
                bf_cost_str
            ])
        print(format_ascii_table(headers, rows))
        print("[ANALYSIS]: Both algorithms converge to identical shortest path metrics when topology is stable.")

def print_menu():
    print("""
============================================================
              NETWORK ROUTING SIMULATOR MENU
============================================================
  1. Display Topology
  2. Compute Shortest Path (Source -> Destination)
  3. Display Router Routing Table
  4. Add Router
  5. Add / Update Link & Cost
  6. Remove Link
  7. Simulate Link Failure (Cable Cut)
  8. Restore Failed Link
  9. Compare Dijkstra vs Distance-Vector (Bellman-Ford)
  10. Reset to Default 6-Node Campus Topology
  0. Exit
============================================================
""")

def main():
    parser = argparse.ArgumentParser(description="Network Routing Simulator")
    parser.add_argument("--src", help="Source router for one-shot path calculation")
    parser.add_argument("--dst", help="Destination router for one-shot path calculation")
    args = parser.parse_args()

    sim = RoutingSimulator()

    if args.src and args.dst:
        sim.show_path(args.src, args.dst)
        return

    while True:
        print_menu()
        choice = input("Select an option (0-10): ").strip()
        if choice == "0":
            print("Exiting simulator.")
            break
        elif choice == "1":
            sim.show_topology()
        elif choice == "2":
            src = input("Enter Source Router: ").strip()
            dst = input("Enter Destination Router: ").strip()
            sim.show_path(src, dst)
        elif choice == "3":
            r = input("Enter Router Node to view routing table: ").strip()
            sim.show_routing_table(r)
        elif choice == "4":
            r = input("Enter new Router name (e.g. G): ").strip()
            if sim.topology.add_router(r):
                print(f"Router '{r}' successfully added.")
            else:
                print("Failed to add router (name empty or already exists).")
        elif choice == "5":
            u = input("Enter Router 1: ").strip()
            v = input("Enter Router 2: ").strip()
            try:
                cost = int(input("Enter Link Cost (positive integer): ").strip())
                if sim.topology.add_link(u, v, cost):
                    print(f"Link {u} <---> {v} configured with cost {cost}.")
                else:
                    print("Failed to add link. Check router names and positive cost.")
            except ValueError:
                print("Invalid cost integer.")
        elif choice == "6":
            u = input("Enter Router 1: ").strip()
            v = input("Enter Router 2: ").strip()
            if sim.topology.remove_link(u, v):
                print(f"Link {u} <---> {v} removed.")
            else:
                print("Link not found.")
        elif choice == "7":
            u = input("Enter Router 1: ").strip()
            v = input("Enter Router 2: ").strip()
            sim.simulate_failure(u, v)
        elif choice == "8":
            u = input("Enter Router 1: ").strip()
            v = input("Enter Router 2: ").strip()
            sim.simulate_recovery(u, v)
        elif choice == "9":
            r = input("Enter Source Router for comparison: ").strip()
            sim.compare_algorithms(r)
        elif choice == "10":
            sim.topology.build_default_topology()
            print("Reset topology to default 6-node campus topology.")
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
