"""Configuration settings for LAN Chat and File Sharing."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5001"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "4096"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "32768"))

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = DATA_DIR / "uploads"
DOWNLOADS_DIR = DATA_DIR / "downloads"

for d in (DATA_DIR, LOGS_DIR, UPLOADS_DIR, DOWNLOADS_DIR):
    d.mkdir(parents=True, exist_ok=True)
