"""Configuration settings for Mini HTTP Web Server."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

HTTP_HOST = os.getenv("HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
PUBLIC_DIR = BASE_DIR / os.getenv("PUBLIC_DIR", "public")
LOGS_DIR = BASE_DIR / "logs"
SERVER_NAME = os.getenv("SERVER_NAME", "MiniHTTPServer/1.0 (Python/CustomSocket)")

for d in (PUBLIC_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)
