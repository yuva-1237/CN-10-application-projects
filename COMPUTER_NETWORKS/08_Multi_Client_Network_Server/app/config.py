"""Configuration settings for Multi-Client Network Server."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5008"))
MAX_SIMULTANEOUS_CLIENTS = int(os.getenv("MAX_SIMULTANEOUS_CLIENTS", "100"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "4096"))

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
