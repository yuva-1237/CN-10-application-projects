"""Network Monitoring and Device Availability Engine."""
import argparse
import json
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import (
    CHECK_INTERVAL_SECONDS,
    DEFAULT_PORTS_TO_CHECK,
    LOGS_DIR,
    MONITOR_TARGETS,
    PROBE_TIMEOUT_SECONDS,
)
from app.probe import ping_host, probe_host_ports
from app.utils import format_ascii_table, setup_logger

logger = setup_logger("Network_Monitor", LOGS_DIR / "monitor.log")

@dataclass
class HostRecord:
    target: str
    resolved_ip: str
    status: str = "PENDING"
    last_latency_ms: float = 0.0
    total_checks: int = 0
    successful_checks: int = 0
    open_ports: List[int] = field(default_factory=list)
    last_checked: str = "Never"

    @property
    def uptime_percentage(self) -> float:
        if self.total_checks == 0:
            return 100.0
        return round((self.successful_checks / self.total_checks) * 100.0, 2)

class NetworkMonitor:
    def __init__(
        self,
        targets: Optional[List[str]] = None,
        ports_to_check: Optional[List[int]] = None,
        timeout: float = PROBE_TIMEOUT_SECONDS
    ):
        self.targets = targets or MONITOR_TARGETS
        self.ports = ports_to_check or DEFAULT_PORTS_TO_CHECK
        self.timeout = timeout
        self.inventory: Dict[str, HostRecord] = {}

        # Initialize host inventory
        for t in self.targets:
            resolved = self._resolve_ip(t)
            self.inventory[t] = HostRecord(target=t, resolved_ip=resolved)

    def _resolve_ip(self, host: str) -> str:
        """Resolve target hostname to IP."""
        try:
            return socket.gethostbyname(host)
        except Exception:
            return "UNRESOLVABLE"

    def check_host(self, host: str) -> HostRecord:
        """Execute single liveness and port assessment on target."""
        rec = self.inventory[host]
        rec.total_checks += 1
        rec.last_checked = time.strftime("%H:%M:%S")

        # 1. ICMP / Connect Liveness
        is_online, latency = ping_host(host, timeout_sec=self.timeout)

        prev_status = rec.status
        if is_online:
            rec.status = "ONLINE"
            rec.successful_checks += 1
            rec.last_latency_ms = latency
            # 2. Port check
            port_states = probe_host_ports(host, self.ports, timeout_sec=0.3)
            rec.open_ports = [p for p, st in port_states.items() if st == "OPEN"]
        else:
            rec.status = "OFFLINE"
            rec.last_latency_ms = -1.0
            rec.open_ports = []

        if prev_status != "PENDING" and prev_status != rec.status:
            logger.warning(f"[STATUS TRANSITION] Host '{host}' changed from {prev_status} -> {rec.status}!")

        return rec

    def run_cycle(self) -> None:
        """Run one full monitoring sweep across all registered targets."""
        for t in self.inventory:
            self.check_host(t)

    def print_dashboard(self) -> None:
        """Render active terminal monitoring dashboard."""
        headers = ["Target", "IP Address", "Status", "Latency (ms)", "Uptime %", "Open Ports", "Last Checked"]
        rows = []
        for rec in self.inventory.values():
            lat_str = f"{rec.last_latency_ms:.2f}" if rec.last_latency_ms >= 0 else "N/A"
            ports_str = ", ".join(str(p) for p in rec.open_ports) if rec.open_ports else "None"
            rows.append([
                rec.target,
                rec.resolved_ip,
                rec.status,
                lat_str,
                f"{rec.uptime_percentage}%",
                ports_str,
                rec.last_checked
            ])

        print("\n" + "=" * 80)
        print("          REAL-TIME LOCAL NETWORK MONITORING DASHBOARD")
        print("=" * 80)
        print(format_ascii_table(headers, rows))
        print("=" * 80 + "\n")

    def generate_report(self) -> Dict[str, Any]:
        """Produce structured JSON monitoring report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "monitored_hosts_count": len(self.inventory),
            "hosts": {}
        }
        for t, rec in self.inventory.items():
            report["hosts"][t] = {
                "target": rec.target,
                "ip": rec.resolved_ip,
                "status": rec.status,
                "last_latency_ms": rec.last_latency_ms,
                "uptime_percentage": rec.uptime_percentage,
                "total_checks": rec.total_checks,
                "successful_checks": rec.successful_checks,
                "open_ports": rec.open_ports,
                "last_checked": rec.last_checked
            }
        return report

    def export_report(self, filepath: Path) -> None:
        """Write JSON report to disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        report = self.generate_report()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[EXPORT] Status report saved to: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Network Monitoring & Device Discovery")
    parser.add_argument("--targets", default=None, help="Comma-separated hosts/IPs to monitor")
    parser.add_argument("--ports", default=None, help="Comma-separated ports to check")
    parser.add_argument("--cycles", type=int, default=1, help="Number of check cycles to run")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL_SECONDS, help="Seconds between cycles")
    parser.add_argument("--export", default=None, help="Path to export report")
    args = parser.parse_args()

    print("""
======================================================================
         NETWORK MONITORING & DEVICE DISCOVERY SYSTEM
======================================================================
* AUTHORIZATION NOTICE:
  Use only on systems/networks that you own or have explicit
  permission to test. Default scope is strictly local/loopback.
======================================================================
    """)

    targets = [t.strip() for t in args.targets.split(",")] if args.targets else None
    ports = [int(p.strip()) for p in args.ports.split(",")] if args.ports else None

    monitor = NetworkMonitor(targets=targets, ports_to_check=ports)

    for cycle in range(1, args.cycles + 1):
        print(f"\nRunning Check Cycle {cycle}/{args.cycles}...")
        monitor.run_cycle()
        monitor.print_dashboard()
        if cycle < args.cycles:
            time.sleep(args.interval)

    out_path = Path(args.export) if args.export else (LOGS_DIR / f"monitor_report_{int(time.time())}.json")
    monitor.export_report(out_path)

if __name__ == "__main__":
    main()
