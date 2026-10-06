"""Utility helpers and realistic packet trace synthesizer for Packet Sniffer."""
import logging
import socket
import struct
import time
from pathlib import Path
from typing import List

def format_mac(bytes_addr: bytes) -> str:
    """Format 6-byte raw MAC into standard colon-separated representation (e.g. 00:1A:2B:3C:4D:5E)."""
    return ":".join(f"{b:02X}" for b in bytes_addr)

def create_synthetic_raw_packets() -> List[dict]:
    """Generate realistic binary packet frames across TCP, UDP, ICMP, DNS, HTTP.
    
    Used when running in SAMPLE DATA MODE (e.g. non-root / non-admin environments).
    These contain real valid binary IP and transport layer headers.
    """
    packets = []

    # 1. TCP SYN Packet (HTTP Port 80 connection initiation)
    # IPv4 Header: Ver=4, IHL=5, TOS=0, Len=40, ID=1001, Flags=0, TTL=64, Proto=6 (TCP), Src=192.168.1.50, Dst=93.184.216.34
    ip_header = struct.pack(
        "!BBHHHBBH4s4s",
        (4 << 4) | 5, 0, 40, 1001, 0x4000, 64, 6, 0,
        socket.inet_aton("192.168.1.50"), socket.inet_aton("93.184.216.34")
    )
    # TCP Header: SrcPort=54120, DstPort=80, Seq=100000, Ack=0, Offset=5, Flags=0x02 (SYN), Win=64240, Cksum=0, Urg=0
    tcp_header = struct.pack(
        "!HHIIBBHHH",
        54120, 80, 100000, 0, (5 << 4), 0x02, 64240, 0, 0
    )
    packets.append({
        "timestamp": time.time() - 4.5,
        "raw": ip_header + tcp_header,
        "link_type": "IPv4_RAW"
    })

    # 2. TCP SYN-ACK Packet
    ip_header2 = struct.pack(
        "!BBHHHBBH4s4s",
        (4 << 4) | 5, 0, 40, 2002, 0x4000, 56, 6, 0,
        socket.inet_aton("93.184.216.34"), socket.inet_aton("192.168.1.50")
    )
    tcp_header2 = struct.pack(
        "!HHIIBBHHH",
        80, 54120, 500000, 100001, (5 << 4), 0x12, 65535, 0, 0
    )
    packets.append({
        "timestamp": time.time() - 4.4,
        "raw": ip_header2 + tcp_header2,
        "link_type": "IPv4_RAW"
    })

    # 3. UDP DNS Query Packet (Port 53)
    dns_payload = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
    ip_header3 = struct.pack(
        "!BBHHHBBH4s4s",
        (4 << 4) | 5, 0, 20 + 8 + len(dns_payload), 3003, 0, 64, 17, 0,
        socket.inet_aton("192.168.1.50"), socket.inet_aton("8.8.8.8")
    )
    udp_header = struct.pack("!HHHH", 53123, 53, 8 + len(dns_payload), 0)
    packets.append({
        "timestamp": time.time() - 3.2,
        "raw": ip_header3 + udp_header + dns_payload,
        "link_type": "IPv4_RAW"
    })

    # 4. ICMP Echo Request Packet (Ping)
    icmp_payload = b"abcdefghijklmnopqrstuvwabcdefghi"
    ip_header4 = struct.pack(
        "!BBHHHBBH4s4s",
        (4 << 4) | 5, 0, 20 + 8 + len(icmp_payload), 4004, 0, 128, 1, 0,
        socket.inet_aton("192.168.1.50"), socket.inet_aton("192.168.1.1")
    )
    # Type 8 = Echo Request, Code 0, Checksum, ID=1, Seq=1
    icmp_header = struct.pack("!BBHHH", 8, 0, 0x4d55, 1, 1)
    packets.append({
        "timestamp": time.time() - 2.1,
        "raw": ip_header4 + icmp_header + icmp_payload,
        "link_type": "IPv4_RAW"
    })

    # 5. ICMP Echo Reply Packet (Pong)
    ip_header5 = struct.pack(
        "!BBHHHBBH4s4s",
        (4 << 4) | 5, 0, 20 + 8 + len(icmp_payload), 5005, 0, 64, 1, 0,
        socket.inet_aton("192.168.1.1"), socket.inet_aton("192.168.1.50")
    )
    # Type 0 = Echo Reply, Code 0, Checksum, ID=1, Seq=1
    icmp_reply_header = struct.pack("!BBHHH", 0, 0, 0x554d, 1, 1)
    packets.append({
        "timestamp": time.time() - 2.0,
        "raw": ip_header5 + icmp_reply_header + icmp_payload,
        "link_type": "IPv4_RAW"
    })

    return packets

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
