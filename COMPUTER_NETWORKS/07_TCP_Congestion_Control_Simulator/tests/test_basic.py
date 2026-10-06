"""Automated tests for Project 07: TCP Congestion Control Simulator."""
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.tcp_engine import (
    EVENT_NORMAL_ACK,
    EVENT_TIMEOUT,
    EVENT_TRIPLE_DUP_ACK,
    STATE_CONGESTION_AVOIDANCE,
    STATE_SLOW_START,
    TCPCongestionEngine,
)

def test_01_slow_start_exponential_growth():
    """Test 1: cwnd doubles in Slow Start phase with initial ssthresh=16."""
    engine = TCPCongestionEngine(initial_cwnd=1, initial_ssthresh=16, variant="RENO")
    l1 = engine.step(EVENT_NORMAL_ACK)
    assert l1.cwnd == 2.0
    assert l1.state == STATE_SLOW_START

    l2 = engine.step(EVENT_NORMAL_ACK)
    assert l2.cwnd == 4.0

    l3 = engine.step(EVENT_NORMAL_ACK)
    assert l3.cwnd == 8.0

def test_02_transition_to_congestion_avoidance():
    """Test 2: When cwnd reaches ssthresh, state transitions to Congestion Avoidance."""
    engine = TCPCongestionEngine(initial_cwnd=8, initial_ssthresh=16, variant="RENO")
    l1 = engine.step(EVENT_NORMAL_ACK)
    assert l1.cwnd == 16.0
    assert l1.state == STATE_CONGESTION_AVOIDANCE

def test_03_congestion_avoidance_linear_growth():
    """Test 3: In Congestion Avoidance, cwnd increments by strictly +1 MSS per round (AIMD)."""
    engine = TCPCongestionEngine(initial_cwnd=16, initial_ssthresh=16, variant="RENO")
    engine.state = STATE_CONGESTION_AVOIDANCE

    l1 = engine.step(EVENT_NORMAL_ACK)
    assert l1.cwnd == 17.0

    l2 = engine.step(EVENT_NORMAL_ACK)
    assert l2.cwnd == 18.0

    l3 = engine.step(EVENT_NORMAL_ACK)
    assert l3.cwnd == 19.0

def test_04_timeout_event_resets_cwnd():
    """Test 4: Timeout causes ssthresh to halve and cwnd to drop back to 1 MSS."""
    engine = TCPCongestionEngine(initial_cwnd=20, initial_ssthresh=16, variant="RENO")
    engine.state = STATE_CONGESTION_AVOIDANCE

    l = engine.step(EVENT_TIMEOUT)
    assert l.cwnd == 1.0
    assert l.ssthresh == 10.0  # 20 / 2
    assert l.state == STATE_SLOW_START

def test_05_triple_dup_ack_fast_recovery_reno_vs_tahoe():
    """Test 5: Reno enters Fast Recovery (cwnd=ssthresh) whereas Tahoe drops to cwnd=1."""
    # Reno
    reno = TCPCongestionEngine(initial_cwnd=24, initial_ssthresh=16, variant="RENO")
    l_reno = reno.step(EVENT_TRIPLE_DUP_ACK)
    assert l_reno.ssthresh == 12.0  # 24 / 2
    assert l_reno.cwnd == 12.0      # Set to ssthresh
    assert l_reno.state == STATE_CONGESTION_AVOIDANCE

    # Tahoe
    tahoe = TCPCongestionEngine(initial_cwnd=24, initial_ssthresh=16, variant="TAHOE")
    l_tahoe = tahoe.step(EVENT_TRIPLE_DUP_ACK)
    assert l_tahoe.ssthresh == 12.0
    assert l_tahoe.cwnd == 1.0       # Tahoe drops back to 1
    assert l_tahoe.state == STATE_SLOW_START
