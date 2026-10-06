"""Utilities and Alert formatting for Network Intrusion Detection System."""
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class SecurityAlert:
    alert_id: str
    timestamp: str
    source_ip: str
    ports_contacted: List[int]
    total_attempts: int
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    alert_type: str
    recommendation: str

def format_alert_box(alert: SecurityAlert) -> str:
    """Render high-visibility security alert box for viva and SOC console."""
    ports_str = ", ".join(str(p) for p in alert.ports_contacted)
    lines = [
        "",
        "!" + "=" * 68 + "!",
        f"!  [SECURITY ALERT] - {alert.alert_type.upper():<43}!",
        "!" + "=" * 68 + "!",
        f"!  Incident ID      : {alert.alert_id:<46}!",
        f"!  Detected At      : {alert.timestamp:<46}!",
        f"!  Source IP        : {alert.source_ip:<46}!",
        f"!  Ports Contacted  : {ports_str:<46}!",
        f"!  Total Attempts   : {alert.total_attempts:<46}!",
        f"!  Severity Level   : {alert.severity:<46}!",
        f"!  Action Taken     : {alert.recommendation:<46}!",
        "!" + "=" * 68 + "!",
        ""
    ]
    return "\n".join(lines)

def setup_logger(name: str, log_file: Path | None = None) -> logging.Logger:
    """Configure standard logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
