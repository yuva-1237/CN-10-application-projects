"""Utilities for HTTP MIME types, dates, and logging."""
import email.utils
import logging
import mimetypes
from pathlib import Path

MIME_TABLE = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
}

def get_mime_type(filepath: Path) -> str:
    """Return appropriate MIME Content-Type based on file extension."""
    ext = filepath.suffix.lower()
    return MIME_TABLE.get(ext, mimetypes.guess_type(str(filepath))[0] or "application/octet-stream")

def get_http_date() -> str:
    """Format current time as standard RFC 7231 IMF-fixdate."""
    return email.utils.formatdate(timeval=None, localtime=False, usegmt=True)

def setup_logger(name: str, log_file: Path | None = None) -> logging.Logger:
    """Configure a standard logger."""
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
