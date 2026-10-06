"""Configuration settings for Network Monitoring & Discovery."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MONITOR_TARGETS = [t.strip() for t in os.getenv("MONITOR_TARGETS", "127.0.0.1,localhost").split(",")]
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "5"))
PROBE_TIMEOUT_SECONDS = float(os.getenv("PROBE_TIMEOUT_SECONDS", "1.0"))
DEFAULT_PORTS_TO_CHECK = [int(p.strip()) for p in os.getenv("DEFAULT_PORTS_TO_CHECK", "80,443,8080,5001,5008").split(",")]

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
