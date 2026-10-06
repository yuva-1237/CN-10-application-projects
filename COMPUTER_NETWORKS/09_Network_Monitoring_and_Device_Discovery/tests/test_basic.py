"""Automated tests for Project 09: Network Monitoring & Device Discovery."""
import json
import socket
import sys
import tempfile
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.monitor import HostRecord, NetworkMonitor
from app.probe import ping_host, probe_tcp_port

def test_01_localhost_ping_and_latency():
    """Test 1: Ping localhost returns ONLINE and valid latency."""
    is_online, latency = ping_host("127.0.0.1", timeout_sec=1.5)
    assert is_online is True
    assert latency >= 0.0

def test_02_probe_open_tcp_port():
    """Test 2: Probe dynamically opened TCP port detects OPEN state."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    try:
        status = probe_tcp_port("127.0.0.1", port, timeout_sec=0.5)
        assert status == "OPEN"
    finally:
        server_sock.close()

def test_03_probe_closed_tcp_port():
    """Test 3: Probe an unbound port detects CLOSED (RST) state."""
    # Find unused port
    temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp.bind(("127.0.0.1", 0))
    port = temp.getsockname()[1]
    temp.close()

    status = probe_tcp_port("127.0.0.1", port, timeout_sec=0.5)
    assert status in ("CLOSED", "FILTERED")

def test_04_host_record_uptime_calculation():
    """Test 4: Verify HostRecord uptime arithmetic."""
    rec = HostRecord(target="test", resolved_ip="1.1.1.1", total_checks=10, successful_checks=8)
    assert rec.uptime_percentage == 80.0

    rec2 = HostRecord(target="test2", resolved_ip="1.1.1.1", total_checks=0)
    assert rec2.uptime_percentage == 100.0

def test_05_monitor_cycle_and_json_report():
    """Test 5: Run monitor cycle on localhost, produce dashboard data and JSON report."""
    monitor = NetworkMonitor(targets=["127.0.0.1"], ports_to_check=[80, 443])
    monitor.run_cycle()

    assert "127.0.0.1" in monitor.inventory
    rec = monitor.inventory["127.0.0.1"]
    assert rec.status == "ONLINE"
    assert rec.total_checks == 1

    report = monitor.generate_report()
    assert report["monitored_hosts_count"] == 1
    assert report["hosts"]["127.0.0.1"]["status"] == "ONLINE"

    with tempfile.TemporaryDirectory() as temp_dir:
        out_file = Path(temp_dir) / "monitor_report.json"
        monitor.export_report(out_file)
        assert out_file.exists()
        loaded = json.loads(out_file.read_text(encoding="utf-8"))
        assert loaded["hosts"]["127.0.0.1"]["status"] == "ONLINE"
