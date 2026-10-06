"""Intrusion Detection Engine with Multi-Port Listener and Incident Reporting."""
import argparse
import json
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import (
    HONEYPOT_PORTS,
    IDS_LISTEN_HOST,
    LOGS_DIR,
    SCAN_THRESHOLD_N_PORTS,
    SCAN_WINDOW_T_SECONDS,
)
from app.detector import PortScanDetector
from app.utils import SecurityAlert, format_alert_box, setup_logger

logger = setup_logger("IDS_Engine", LOGS_DIR / "ids.log")

class IDSEngine:
    def __init__(
        self,
        listen_host: str = IDS_LISTEN_HOST,
        ports: Optional[List[int]] = None,
        threshold_n: int = SCAN_THRESHOLD_N_PORTS,
        window_t: float = SCAN_WINDOW_T_SECONDS
    ):
        self.host = listen_host
        self.ports = ports or [5010, 5011, 5012, 5013, 5014, 5015, 5016, 5017]
        self.detector = PortScanDetector(threshold_n_ports=threshold_n, window_t_seconds=window_t)
        self.sockets: List[socket.socket] = []
        self.is_running = False

    def start_listener(self) -> None:
        """Bind multi-port honeypot listeners on local interface."""
        self.is_running = True

        logger.info("=" * 68)
        logger.info("  NETWORK INTRUSION & PORT SCAN DETECTION ENGINE (IDS)")
        logger.info(f"  Bind Interface      : {self.host}")
        logger.info(f"  Monitored Ports     : {self.ports}")
        logger.info(f"  Threshold (N)       : {self.detector.threshold} distinct ports")
        logger.info(f"  Time Window (T)     : {self.detector.window} seconds")
        logger.info("=" * 68)

        for port in self.ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, port))
                s.listen(5)
                self.sockets.append(s)
                threading.Thread(target=self._listen_port, args=(s, port), daemon=True).start()
            except OSError as e:
                logger.warning(f"Could not bind monitoring port {port}: {e}")

        logger.info(f"Successfully bound {len(self.sockets)} honeypot listener ports on {self.host}.")

    def _listen_port(self, sock: socket.socket, port: int) -> None:
        """Listen on an individual port and capture connection telemetry."""
        while self.is_running:
            try:
                conn, addr = sock.accept()
                client_ip = addr[0]
                conn.close()

                # Ingest into detector
                alert = self.detector.record_attempt(client_ip, port)
                if alert:
                    print(format_alert_box(alert))
                    logger.warning(f"[INTRUSION DETECTED] {alert.alert_type} from {alert.source_ip} (Ports: {alert.ports_contacted})")
            except OSError:
                break

    def export_report(self, filepath: Path) -> None:
        """Export all recorded security alerts to a structured JSON incident report."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": self.detector.get_summary(),
            "incident_count": len(self.detector.alerts),
            "incidents": [
                {
                    "alert_id": a.alert_id,
                    "timestamp": a.timestamp,
                    "source_ip": a.source_ip,
                    "ports_contacted": a.ports_contacted,
                    "total_attempts": a.total_attempts,
                    "severity": a.severity,
                    "alert_type": a.alert_type,
                    "recommendation": a.recommendation
                }
                for a in self.detector.alerts
            ]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"[EXPORT] Security incident report saved to: {filepath}")

    def stop(self) -> None:
        """Stop all honeypot listeners."""
        self.is_running = False
        for s in self.sockets:
            try:
                s.close()
            except Exception:
                pass
        self.sockets.clear()
        logger.info("IDS Engine stopped.")

def main():
    parser = argparse.ArgumentParser(description="Network Intrusion & Port Scan Detection System")
    parser.add_argument("--host", default=IDS_LISTEN_HOST, help="Listen host interface (default: 127.0.0.1)")
    parser.add_argument("--threshold", type=int, default=SCAN_THRESHOLD_N_PORTS, help="Distinct port threshold N")
    parser.add_argument("--window", type=float, default=SCAN_WINDOW_T_SECONDS, help="Time window T in seconds")
    parser.add_argument("--export", default=None, help="Export JSON path upon exit")
    args = parser.parse_args()

    print("""
======================================================================
     NETWORK INTRUSION & PORT SCAN DETECTION SYSTEM (DEFENSIVE IDS)
======================================================================
* WARNING & ETHICAL COMPLIANCE:
  - This is an educational intrusion detection system.
  - All listeners and simulation tests bind strictly to localhost (127.0.0.1).
  - Only test on networks you own or have explicit written authorization to monitor.
======================================================================
    """)

    engine = IDSEngine(
        listen_host=args.host,
        threshold_n=args.threshold,
        window_t=args.window
    )
    engine.start_listener()
    print("IDS listening... Run 'python app/simulator.py' in another terminal to trigger a simulated scan.")
    print("Press Ctrl+C to terminate and generate final report.\n")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping IDS Engine...")
    finally:
        engine.stop()
        out_file = Path(args.export) if args.export else (LOGS_DIR / f"ids_report_{int(time.time())}.json")
        engine.export_report(out_file)

if __name__ == "__main__":
    main()
