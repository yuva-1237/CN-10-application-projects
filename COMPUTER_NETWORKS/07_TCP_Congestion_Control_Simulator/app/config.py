"""Configuration settings for TCP Congestion Control Simulator."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INITIAL_CWND = int(os.getenv("INITIAL_CWND", "1"))
INITIAL_SSTHRESH = int(os.getenv("INITIAL_SSTHRESH", "16"))
SIMULATION_ROUNDS = int(os.getenv("SIMULATION_ROUNDS", "25"))
TCP_VARIANT = os.getenv("TCP_VARIANT", "RENO").upper()

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
