"""Low-Level Protocol Header Dissector using binary struct unpacking.

Supports decoding:
- Ethernet II (Layer 2)
- IPv4 (Layer 3)
- TCP, UDP, ICMP (Layer 4)
- High-level application protocol hints (DNS Port 53, HTTP Port 80/8080)
"""
import socket
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

@dataclass
class PacketMetadata:
    timestamp: float
    raw_length: int
    ether_type: Optional[str] = None
    src_mac: Optional[str] = None
    dst_mac: Optional[str] = None
    ip_version: Optional[int] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    ttl: Optional[int] = None
    protocol_num: Optional[int] = None
    protocol_name: str = "UNKNOWN"
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    tcp_flags: Dict[str, bool] = field(default_factory=dict)
    tcp_seq: Optional[int] = None
    tcp_ack: Optional[int] = None
    icmp_type: Optional[int] = None
    icmp_code: Optional[int] = None
    app_hint: Optional[str] = None
    payload_length: int = 0

def dissect_ethernet(raw_frame: bytes) -> Tuple[Optional[str], Optional[str], int, bytes]:
    """Unpack 14-byte Ethernet II header."""
    if len(raw_frame) < 14:
        return None, None, 0, raw_frame
    dst_mac_raw, src_mac_raw, eth_type = struct.unpack("!6s6sH", raw_frame[:14])
    dst_mac = ":".join(f"{b:02X}" for b in dst_mac_raw)
    src_mac = ":".join(f"{b:02X}" for b in src_mac_raw)
    return src_mac, dst_mac, eth_type, raw_frame[14:]

def dissect_ipv4(raw_ip: bytes) -> Tuple[Dict[str, Any], bytes]:
    """Unpack standard 20-byte IPv4 header."""
    if len(raw_ip) < 20:
        return {}, raw_ip

    v_ihl, tos, total_len, pkt_id, flags_frag, ttl, proto, checksum, src_raw, dst_raw = struct.unpack(
        "!BBHHHBBH4s4s", raw_ip[:20]
    )

    version = (v_ihl >> 4) & 0x0F
    ihl = (v_ihl & 0x0F) * 4  # Header length in bytes

    src_ip = socket.inet_ntoa(src_raw)
    dst_ip = socket.inet_ntoa(dst_raw)

    payload = raw_ip[ihl:]
    return {
        "version": version,
        "ihl": ihl,
        "tos": tos,
        "total_length": total_len,
        "id": pkt_id,
        "ttl": ttl,
        "protocol": proto,
        "src_ip": src_ip,
        "dst_ip": dst_ip
    }, payload

def dissect_tcp(raw_tcp: bytes) -> Tuple[Dict[str, Any], bytes]:
    """Unpack 20-byte TCP header and flag bitfield."""
    if len(raw_tcp) < 20:
        return {}, raw_tcp

    src_port, dst_port, seq, ack, offset_reserved, flags_byte, window, checksum, urgent = struct.unpack(
        "!HHIIBBHHH", raw_tcp[:20]
    )

    data_offset = ((offset_reserved >> 4) & 0x0F) * 4

    flags = {
        "FIN": bool(flags_byte & 0x01),
        "SYN": bool(flags_byte & 0x02),
        "RST": bool(flags_byte & 0x04),
        "PSH": bool(flags_byte & 0x08),
        "ACK": bool(flags_byte & 0x10),
        "URG": bool(flags_byte & 0x20)
    }

    payload = raw_tcp[data_offset:]
    return {
        "src_port": src_port,
        "dst_port": dst_port,
        "seq": seq,
        "ack": ack,
        "data_offset": data_offset,
        "flags": flags,
        "window": window,
        "checksum": checksum
    }, payload

def dissect_udp(raw_udp: bytes) -> Tuple[Dict[str, Any], bytes]:
    """Unpack 8-byte UDP header."""
    if len(raw_udp) < 8:
        return {}, raw_udp
    src_port, dst_port, length, checksum = struct.unpack("!HHHH", raw_udp[:8])
    payload = raw_udp[8:]
    return {
        "src_port": src_port,
        "dst_port": dst_port,
        "length": length,
        "checksum": checksum
    }, payload

def dissect_icmp(raw_icmp: bytes) -> Tuple[Dict[str, Any], bytes]:
    """Unpack 8-byte ICMP header."""
    if len(raw_icmp) < 8:
        return {}, raw_icmp
    icmp_type, icmp_code, checksum, rest_of_hdr = struct.unpack("!BBHI", raw_icmp[:8])
    payload = raw_icmp[8:]
    return {
        "type": icmp_type,
        "code": icmp_code,
        "checksum": checksum,
        "rest": rest_of_hdr
    }, payload

def dissect_packet(raw_data: bytes, has_ethernet: bool = False, timestamp: float = 0.0) -> PacketMetadata:
    """Full hierarchical decapsulation of a raw packet frame."""
    meta = PacketMetadata(timestamp=timestamp, raw_length=len(raw_data))

    curr_bytes = raw_data
    if has_ethernet:
        src_mac, dst_mac, eth_type, curr_bytes = dissect_ethernet(raw_data)
        meta.src_mac = src_mac
        meta.dst_mac = dst_mac
        meta.ether_type = f"0x{eth_type:04X}"
        if eth_type != 0x0800:
            meta.protocol_name = f"NON_IPV4 (0x{eth_type:04X})"
            return meta

    # Decapsulate IPv4
    ip_info, transport_bytes = dissect_ipv4(curr_bytes)
    if not ip_info:
        return meta

    meta.ip_version = ip_info["version"]
    meta.src_ip = ip_info["src_ip"]
    meta.dst_ip = ip_info["dst_ip"]
    meta.ttl = ip_info["ttl"]
    meta.protocol_num = ip_info["protocol"]

    # Decapsulate Transport Layer
    if meta.protocol_num == 6:  # TCP
        meta.protocol_name = "TCP"
        tcp_info, app_bytes = dissect_tcp(transport_bytes)
        if tcp_info:
            meta.src_port = tcp_info["src_port"]
            meta.dst_port = tcp_info["dst_port"]
            meta.tcp_flags = tcp_info["flags"]
            meta.tcp_seq = tcp_info["seq"]
            meta.tcp_ack = tcp_info["ack"]
            meta.payload_length = len(app_bytes)
            # Application hint
            if meta.src_port in (80, 8080) or meta.dst_port in (80, 8080):
                meta.app_hint = "HTTP"

    elif meta.protocol_num == 17:  # UDP
        meta.protocol_name = "UDP"
        udp_info, app_bytes = dissect_udp(transport_bytes)
        if udp_info:
            meta.src_port = udp_info["src_port"]
            meta.dst_port = udp_info["dst_port"]
            meta.payload_length = len(app_bytes)
            # Application hint
            if meta.src_port == 53 or meta.dst_port == 53:
                meta.app_hint = "DNS"

    elif meta.protocol_num == 1:  # ICMP
        meta.protocol_name = "ICMP"
        icmp_info, app_bytes = dissect_icmp(transport_bytes)
        if icmp_info:
            meta.icmp_type = icmp_info["type"]
            meta.icmp_code = icmp_info["code"]
            meta.payload_length = len(app_bytes)
            if meta.icmp_type == 8:
                meta.app_hint = "ECHO_REQUEST (Ping)"
            elif meta.icmp_type == 0:
                meta.app_hint = "ECHO_REPLY (Pong)"

    return meta
