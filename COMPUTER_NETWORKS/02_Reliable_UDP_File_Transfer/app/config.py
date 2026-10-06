"""Configuration settings for Reliable UDP File Transfer."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RECEIVER_HOST = os.getenv("RECEIVER_HOST", "127.0.0.1")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT", "5002"))
PACKET_PAYLOAD_SIZE = int(os.getenv("PACKET_PAYLOAD_SIZE", "1024"))
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "0.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
SIMULATED_LOSS_RATE = float(os.getenv("SIMULATED_LOSS_RATE", "0.0"))

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SENDER_DIR = DATA_DIR / "sender_files"
RECEIVER_DIR = DATA_DIR / "received_files"

for d in (DATA_DIR, LOGS_DIR, SENDER_DIR, RECEIVER_DIR):
    d.mkdir(parents=True, exist_ok=True)
