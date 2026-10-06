"""Utilities, framing, and statistics tracker for Multi-Client Server."""
import json
import logging
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple

HEADER_FORMAT = "!I"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def pack_frame(data: dict[str, Any]) -> bytes:
    """Encode dictionary into length-prefixed bytes."""
    encoded = json.dumps(data).encode("utf-8")
    length = struct.pack(HEADER_FORMAT, len(encoded))
    return length + encoded

def unpack_frames(buffer: bytearray) -> Tuple[list[dict], bytearray]:
    """Extract all complete framed messages from buffer, returning (messages, remaining_buffer)."""
    messages = []
    while len(buffer) >= HEADER_SIZE:
        (msg_len,) = struct.unpack(HEADER_FORMAT, buffer[:HEADER_SIZE])
        if len(buffer) < HEADER_SIZE + msg_len:
            # Incomplete frame; wait for more data
            break
        frame_bytes = buffer[HEADER_SIZE:HEADER_SIZE + msg_len]
        buffer = buffer[HEADER_SIZE + msg_len:]
        try:
            msg = json.loads(frame_bytes.decode("utf-8"))
            messages.append(msg)
        except Exception:
            pass
    return messages, buffer

@dataclass
class ServerStats:
    total_connections: int = 0
    active_clients: int = 0
    peak_clients: int = 0
    messages_received: int = 0
    messages_sent: int = 0

def setup_logger(name: str, log_file: Path | None = None) -> logging.Logger:
    """Configure standard logger."""
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
