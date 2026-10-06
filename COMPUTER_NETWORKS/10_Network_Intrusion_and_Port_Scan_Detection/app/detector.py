"""Sliding-Window Heuristic Anomaly Detector for Network Intrusion Detection."""
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from app.config import SCAN_THRESHOLD_N_PORTS, SCAN_WINDOW_T_SECONDS
from app.utils import SecurityAlert

@dataclass
class ConnectionAttempt:
    src_ip: str
    dst_port: int
    timestamp: float

class PortScanDetector:
    def __init__(
        self,
        threshold_n_ports: int = SCAN_THRESHOLD_N_PORTS,
        window_t_seconds: float = SCAN_WINDOW_T_SECONDS
    ):
        self.threshold = threshold_n_ports
        self.window = window_t_seconds
        # src_ip -> list of ConnectionAttempt
        self.history: Dict[str, List[ConnectionAttempt]] = defaultdict(list)
        # src_ip -> last alert timestamp (cooldown)
        self.alert_cooldown: Dict[str, float] = {}
        self.alerts: List[SecurityAlert] = []

    def record_attempt(self, src_ip: str, dst_port: int, timestamp: Optional[float] = None) -> Optional[SecurityAlert]:
        """Ingest connection attempt, prune expired sliding window entries, and evaluate heuristic rules."""
        now = timestamp if timestamp is not None else time.time()
        clean_ip = src_ip.strip()

        # 1. Prune events outside the sliding window (now - T)
        cutoff = now - self.window
        self.history[clean_ip] = [ev for ev in self.history[clean_ip] if ev.timestamp >= cutoff]

        # 2. Add current event
        self.history[clean_ip].append(ConnectionAttempt(src_ip=clean_ip, dst_port=dst_port, timestamp=now))

        attempts = self.history[clean_ip]
        distinct_ports = sorted(list({ev.dst_port for ev in attempts}))

        # 3. Check threshold trigger
        if len(distinct_ports) >= self.threshold:
            is_sequential = self._check_sequential(distinct_ports)
            pattern_type = "Sequential Port Reconnaissance" if is_sequential else "Horizontal Port Sweep"
            severity = self._compute_severity(len(distinct_ports), is_sequential)

            # Check cooldown unless severity has escalated
            last_alert_time, last_severity = self.alert_cooldown.get(clean_ip, (0.0, "NONE"))
            severity_ranks = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            is_escalation = severity_ranks.get(severity, 0) > severity_ranks.get(last_severity, 0)

            if not is_escalation and (now - last_alert_time < (self.window / 2.0)):
                return None  # Cooldown active for same or lower severity

            alert = SecurityAlert(
                alert_id=f"IDS-{uuid.uuid4().hex[:8].upper()}",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
                source_ip=clean_ip,
                ports_contacted=distinct_ports,
                total_attempts=len(attempts),
                severity=severity,
                alert_type=pattern_type,
                recommendation=f"Rate-limit or block {clean_ip} at edge firewall / ACL"
            )

            self.alert_cooldown[clean_ip] = (now, severity)
            self.alerts.append(alert)
            return alert

        return None

    def _check_sequential(self, ports: List[int]) -> bool:
        """Identify if at least 3 ports in the list form a continuous sequential sequence."""
        if len(ports) < 3:
            return False
        consecutive = 1
        for i in range(1, len(ports)):
            if ports[i] == ports[i - 1] + 1:
                consecutive += 1
                if consecutive >= 3:
                    return True
            else:
                consecutive = 1
        return False

    def _compute_severity(self, num_ports: int, is_sequential: bool) -> str:
        """Assign CVSS-aligned risk classification."""
        if num_ports >= 20:
            return "CRITICAL"
        elif num_ports >= 10:
            return "HIGH"
        elif num_ports >= 5 or is_sequential:
            return "MEDIUM"
        return "LOW"

    def get_summary(self) -> Dict[str, any]:
        """Return operational security metrics."""
        return {
            "tracked_sources": len(self.history),
            "total_alerts_generated": len(self.alerts),
            "threshold_n": self.threshold,
            "window_seconds_t": self.window
        }
