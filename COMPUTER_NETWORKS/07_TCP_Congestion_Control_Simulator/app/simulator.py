"""Interactive CLI runner for TCP Congestion Control Simulation."""
import argparse
import sys
from pathlib import Path
from typing import Dict

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import INITIAL_CWND, INITIAL_SSTHRESH, SIMULATION_ROUNDS, TCP_VARIANT
from app.tcp_engine import (
    EVENT_NORMAL_ACK,
    EVENT_TIMEOUT,
    EVENT_TRIPLE_DUP_ACK,
    TCPCongestionEngine,
)
from app.utils import render_ascii_graph, setup_logger

logger = setup_logger("TCP_Simulator")

def parse_loss_events(event_str: str) -> Dict[int, str]:
    """Parse string format '8:TIMEOUT,16:TRIPLE_DUP_ACK' into a dictionary."""
    schedule = {}
    if not event_str:
        return schedule
    for item in event_str.split(","):
        if ":" in item:
            r_str, evt = item.split(":", 1)
            try:
                schedule[int(r_str.strip())] = evt.strip().upper()
            except ValueError:
                pass
    return schedule

def main():
    parser = argparse.ArgumentParser(description="TCP Congestion Control Simulator")
    parser.add_argument("--rounds", type=int, default=SIMULATION_ROUNDS, help=f"Total rounds (default: {SIMULATION_ROUNDS})")
    parser.add_argument("--ssthresh", type=float, default=INITIAL_SSTHRESH, help=f"Initial ssthresh (default: {INITIAL_SSTHRESH})")
    parser.add_argument("--variant", default=TCP_VARIANT, choices=["RENO", "TAHOE"], help="TCP Variant (RENO or TAHOE)")
    parser.add_argument("--loss", default="8:TIMEOUT,16:TRIPLE_DUP_ACK", help="Loss schedule (e.g. '8:TIMEOUT,16:TRIPLE_DUP_ACK')")
    args = parser.parse_args()

    print("""
======================================================================
           TCP CONGESTION CONTROL SIMULATOR [SIMULATION MODE]
======================================================================
  Notice: This is a discrete mathematical simulation of transport-layer
          congestion management (RFC 5681 / Reno & Tahoe models).
======================================================================
    """)

    engine = TCPCongestionEngine(
        initial_cwnd=INITIAL_CWND,
        initial_ssthresh=args.ssthresh,
        variant=args.variant
    )
    loss_schedule = parse_loss_events(args.loss)

    print(f"Algorithm Variant : TCP {args.variant}")
    print(f"Initial cwnd      : {INITIAL_CWND} MSS")
    print(f"Initial ssthresh  : {args.ssthresh} MSS")
    print(f"Loss Events       : {loss_schedule or 'None (Clean Channel)'}")
    print(f"Simulation Window : {args.rounds} Rounds (RTTs)\n")

    logs = engine.run_simulation(args.rounds, loss_schedule)

    # Print Trace Table
    print("+-------+----------+----------+-----------------------+-----------------+----------------------------------------------------+")
    print("| Round | cwnd     | ssthresh | State                 | Event           | Actions Taken & Academic Notes                     |")
    print("+-------+----------+----------+-----------------------+-----------------+----------------------------------------------------+")
    for l in logs:
        print(f"| {l.round_num:>5} | {l.cwnd:>8.1f} | {l.ssthresh:>8.1f} | {l.state:<21} | {l.event:<15} | {l.description:<50} |")
    print("+-------+----------+----------+-----------------------+-----------------+----------------------------------------------------+\n")

    # Render ASCII Plot
    rounds = [l.round_num for l in logs]
    cwnds = [l.cwnd for l in logs]
    graph = render_ascii_graph(rounds, cwnds)
    print("CONGESTION WINDOW EVOLUTION GRAPH (cwnd vs Round):")
    print(graph)

    print("\n" + "=" * 70)
    print("  ACADEMIC OBSERVATIONS:")
    print("  1. Slow Start: cwnd doubles every round until reaching ssthresh.")
    print("  2. Congestion Avoidance: cwnd increases linearly by +1 MSS per round (AIMD).")
    print("  3. Timeout: Triggers severe penalization (ssthresh = cwnd/2, cwnd = 1).")
    if args.variant == "RENO":
        print("  4. Triple Dup ACK: Reno enters Fast Recovery (ssthresh = cwnd/2, cwnd = ssthresh),")
        print("     avoiding the costly drop back to cwnd=1.")
    print("=" * 70)

if __name__ == "__main__":
    main()
