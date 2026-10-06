"""Automated tests for Project 06: Packet Sniffer and Network Analyzer."""
import json
import socket
import struct
import sys
import tempfile
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.analyzer import NetworkTrafficAnalyzer
from app.dissector import (
    dissect_icmp,
    dissect_ipv4,
    dissect_packet,
    dissect_tcp,
    dissect_udp,
)
from app.sniffer import PacketSniffer

def test_01_dissect_ipv4_header():
    """Test 1: Dissect standard IPv4 binary header."""
    raw_ip = struct.pack(
        "!BBHHHBBH4s4s",
        0x45, 0, 40, 54321, 0x4000, 64, 6, 0,
        socket.inet_aton("192.168.1.100"), socket.inet_aton("10.0.0.1")
    )
    ip_info, payload = dissect_ipv4(raw_ip)

    assert ip_info["version"] == 4
    assert ip_info["ihl"] == 20
    assert ip_info["total_length"] == 40
    assert ip_info["protocol"] == 6
    assert ip_info["src_ip"] == "192.168.1.100"
    assert ip_info["dst_ip"] == "10.0.0.1"

def test_02_dissect_tcp_header_and_flags():
    """Test 2: Dissect TCP binary header and verify SYN-ACK flags."""
    # Offset=5 (20 bytes), Flags = 0x12 (SYN | ACK)
    raw_tcp = struct.pack(
        "!HHIIBBHHH",
        443, 51234, 1000, 2000, (5 << 4), 0x12, 65535, 0, 0
    )
    tcp_info, _ = dissect_tcp(raw_tcp)

    assert tcp_info["src_port"] == 443
    assert tcp_info["dst_port"] == 51234
    assert tcp_info["seq"] == 1000
    assert tcp_info["ack"] == 2000
    assert tcp_info["flags"]["SYN"] is True
    assert tcp_info["flags"]["ACK"] is True
    assert tcp_info["flags"]["FIN"] is False

def test_03_dissect_udp_header():
    """Test 3: Dissect UDP header."""
    raw_udp = struct.pack("!HHHH", 5353, 53, 32, 0)
    udp_info, _ = dissect_udp(raw_udp)

    assert udp_info["src_port"] == 5353
    assert udp_info["dst_port"] == 53
    assert udp_info["length"] == 32

def test_04_dissect_icmp_echo_request():
    """Test 4: Dissect ICMP Ping (Echo Request type 8)."""
    raw_icmp = struct.pack("!BBHI", 8, 0, 0x1234, 0xABCD)
    icmp_info, _ = dissect_icmp(raw_icmp)

    assert icmp_info["type"] == 8
    assert icmp_info["code"] == 0

def test_05_traffic_analyzer_distribution_and_export():
    """Test 5: Capture sample frames, calculate protocol statistics, and export JSON report."""
    sniffer = PacketSniffer(force_sample=True)
    packets = sniffer.capture(count=20, filter_proto="ALL")
    assert len(packets) == 20

    analyzer = NetworkTrafficAnalyzer(packets)
    report = analyzer.generate_report()

    assert report["summary"]["total_packets"] == 20
    assert "TCP" in report["protocol_distribution"]
    assert "UDP" in report["protocol_distribution"]
    assert "ICMP" in report["protocol_distribution"]

    # Verify JSON export
    with tempfile.TemporaryDirectory() as temp_dir:
        out_file = Path(temp_dir) / "test_report.json"
        analyzer.export_json(out_file)
        assert out_file.exists()
        loaded = json.loads(out_file.read_text(encoding="utf-8"))
        assert loaded["summary"]["total_packets"] == 20
