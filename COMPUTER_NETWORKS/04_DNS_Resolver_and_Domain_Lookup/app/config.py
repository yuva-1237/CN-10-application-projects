"""Configuration settings for DNS Resolver."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PRIMARY_DNS = os.getenv("PRIMARY_DNS", "8.8.8.8")
SECONDARY_DNS = os.getenv("SECONDARY_DNS", "1.1.1.1")
DNS_PORT = int(os.getenv("DNS_PORT", "53"))
DNS_TIMEOUT = float(os.getenv("DNS_TIMEOUT", "3.0"))
DEFAULT_CACHE_TTL = int(os.getenv("DEFAULT_CACHE_TTL", "300"))

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
