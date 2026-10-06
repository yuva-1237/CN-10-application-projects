"""Configuration settings for Packet Sniffer & Analyzer."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CAPTURE_INTERFACE = os.getenv("CAPTURE_INTERFACE", "127.0.0.1")
DEFAULT_PACKET_LIMIT = int(os.getenv("DEFAULT_PACKET_LIMIT", "50"))
FORCE_SAMPLE_MODE = os.getenv("FORCE_SAMPLE_MODE", "false").lower() == "true"

LOGS_DIR = BASE_DIR / "logs"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"

for d in (LOGS_DIR, SAMPLE_DATA_DIR):
    d.mkdir(parents=True, exist_ok=True)
