"""Automated tests for Project 10: Network Intrusion and Port Scan Detection."""
import json
import sys
import tempfile
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.detector import PortScanDetector
from app.ids_engine import IDSEngine

def test_01_normal_traffic_does_not_trigger_alert():
    """Test 1: Normal repeated connections to a single service port (e.g. 80) does not trigger port scan alert."""
    detector = PortScanDetector(threshold_n_ports=5, window_t_seconds=10.0)

    # 10 attempts to the same web server port 80
    for _ in range(10):
        alert = detector.record_attempt("192.168.1.100", 80)
        assert alert is None, "False positive alert generated for single-port traffic!"

    assert len(detector.alerts) == 0

def test_02_threshold_exceeded_triggers_port_scan_alert():
    """Test 2: Connecting to 5 distinct ports within time window triggers a port scan alert."""
    detector = PortScanDetector(threshold_n_ports=5, window_t_seconds=10.0)

    # Connect to ports 21, 22, 23, 25, 80
    alert1 = detector.record_attempt("192.168.1.200", 21)
    alert2 = detector.record_attempt("192.168.1.200", 22)
    alert3 = detector.record_attempt("192.168.1.200", 23)
    alert4 = detector.record_attempt("192.168.1.200", 25)
    assert alert1 is None and alert2 is None and alert3 is None and alert4 is None

    # 5th distinct port triggers the alert
    alert5 = detector.record_attempt("192.168.1.200", 80)
    assert alert5 is not None
    assert alert5.source_ip == "192.168.1.200"
    assert len(alert5.ports_contacted) == 5
    assert alert5.severity in ("MEDIUM", "HIGH")

def test_03_severity_scaling():
    """Test 3: Severity scales up as port reconnaissance count increases."""
    detector = PortScanDetector(threshold_n_ports=5, window_t_seconds=30.0)

    # Hit 12 distinct ports to evaluate HIGH severity
    alert = None
    for p in range(1000, 1012):
        res = detector.record_attempt("10.0.0.99", p)
        if res:
            alert = res

    assert alert is not None
    assert alert.severity == "HIGH"

def test_04_sliding_window_pruning():
    """Test 4: Old connection attempts outside window T expire and do not accumulate."""
    detector = PortScanDetector(threshold_n_ports=5, window_t_seconds=5.0)

    t0 = 1000.0
    # 4 distinct attempts at t0
    detector.record_attempt("172.16.0.5", 21, timestamp=t0)
    detector.record_attempt("172.16.0.5", 22, timestamp=t0)
    detector.record_attempt("172.16.0.5", 23, timestamp=t0)
    detector.record_attempt("172.16.0.5", 25, timestamp=t0)

    # 5th attempt arrives 10 seconds later (window 5.0s has expired)
    alert_late = detector.record_attempt("172.16.0.5", 80, timestamp=t0 + 10.0)
    assert alert_late is None, "Expired events were not pruned from sliding window!"

def test_05_ids_engine_report_generation():
    """Test 5: IDS engine registers alerts and produces valid JSON report."""
    engine = IDSEngine(threshold_n=3, window_t=10.0)

    # Simulate ingestion of scan
    engine.detector.record_attempt("192.168.1.15", 8080)
    engine.detector.record_attempt("192.168.1.15", 8081)
    alert = engine.detector.record_attempt("192.168.1.15", 8082)
    assert alert is not None

    with tempfile.TemporaryDirectory() as temp_dir:
        out_file = Path(temp_dir) / "test_ids_report.json"
        engine.export_report(out_file)
        assert out_file.exists()

        data = json.loads(out_file.read_text(encoding="utf-8"))
        assert data["incident_count"] == 1
        assert data["incidents"][0]["source_ip"] == "192.168.1.15"
