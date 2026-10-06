"""Configuration settings for IDS and Port Scan Detection."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IDS_LISTEN_HOST = os.getenv("IDS_LISTEN_HOST", "127.0.0.1")
SCAN_THRESHOLD_N_PORTS = int(os.getenv("SCAN_THRESHOLD_N_PORTS", "5"))
SCAN_WINDOW_T_SECONDS = float(os.getenv("SCAN_WINDOW_T_SECONDS", "10.0"))
HONEYPOT_PORTS = [int(p.strip()) for p in os.getenv("HONEYPOT_PORTS", "21,22,23,25,80,443,3306,8080").split(",")]

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
