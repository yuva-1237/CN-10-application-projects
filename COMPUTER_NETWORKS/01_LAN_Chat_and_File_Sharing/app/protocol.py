"""Binary and JSON framing protocol for TCP sockets.

Protocol Structure:
+-------------------+--------------------+------------------------+----------------------+
| JSON Header Length| JSON Control Header| Binary Payload Length  | Raw Binary Payload   |
| (4 bytes, !I)     | (UTF-8 JSON string)| (4 bytes, !I)          | (optional raw bytes) |
+-------------------+--------------------+------------------------+----------------------+
"""
import json
import socket
import struct
from typing import Any, Tuple

HEADER_FORMAT = "!I"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def recv_exact(sock: socket.socket, num_bytes: int) -> bytes:
    """Read exactly num_bytes from a TCP socket or raise ConnectionError on EOF."""
    data = bytearray()
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            raise ConnectionError("Socket closed prematurely by remote peer.")
        data.extend(packet)
    return bytes(data)

def send_msg(sock: socket.socket, header: dict[str, Any], binary_payload: bytes = b"") -> None:
    """Pack and transmit a control header and optional binary payload over TCP."""
    header_json = json.dumps(header).encode("utf-8")
    header_len = struct.pack(HEADER_FORMAT, len(header_json))
    bin_len = struct.pack(HEADER_FORMAT, len(binary_payload))

    # Send in a single continuous stream
    sock.sendall(header_len + header_json + bin_len + binary_payload)

def recv_msg(sock: socket.socket) -> Tuple[dict[str, Any], bytes]:
    """Read and unpack a complete framed message from a TCP socket."""
    header_len_raw = recv_exact(sock, HEADER_SIZE)
    (header_len,) = struct.unpack(HEADER_FORMAT, header_len_raw)

    header_raw = recv_exact(sock, header_len)
    header = json.loads(header_raw.decode("utf-8"))

    bin_len_raw = recv_exact(sock, HEADER_SIZE)
    (bin_len,) = struct.unpack(HEADER_FORMAT, bin_len_raw)

    payload = recv_exact(sock, bin_len) if bin_len > 0 else b""
    return header, payload
