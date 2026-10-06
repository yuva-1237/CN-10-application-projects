"""Automated tests for Project 08: Multi-Client Network Server."""
import socket
import sys
import threading
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.client import MultiClient
from app.server import MultiClientServer

TEST_SERVER_PORT = 5988

@pytest.fixture(scope="module")
def multi_server():
    """Start the non-blocking Multi-Client Server on loopback."""
    server = MultiClientServer(host="127.0.0.1", port=TEST_SERVER_PORT)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)
    yield server
    server.stop()
    time.sleep(0.2)

def test_01_server_startup_and_listening(multi_server):
    """Test 1: Server starts and binds non-blocking socket."""
    assert multi_server.is_running is True
    assert multi_server.server_sock is not None
    # Validate raw connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", TEST_SERVER_PORT))
    s.close()

def test_02_single_client_registration(multi_server):
    """Test 2: Single client connects, registers, and appears in server users."""
    client = MultiClient("127.0.0.1", TEST_SERVER_PORT, "User_Alpha")
    assert client.connect() is True
    time.sleep(0.2)
    assert "User_Alpha" in multi_server.users
    client.disconnect()
    time.sleep(0.2)
    assert "User_Alpha" not in multi_server.users

def test_03_five_simultaneous_concurrent_clients(multi_server):
    """Test 3: Exactly 5 simultaneous clients connect concurrently."""
    clients = []
    try:
        for i in range(5):
            c = MultiClient("127.0.0.1", TEST_SERVER_PORT, f"Client_{i + 1}")
            assert c.connect() is True
            clients.append(c)
            time.sleep(0.05)

        time.sleep(0.3)
        assert len(multi_server.users) == 5
        assert multi_server.stats.active_clients >= 5
    finally:
        for c in clients:
            c.disconnect()
        time.sleep(0.2)

def test_04_broadcast_delivery_across_clients(multi_server):
    """Test 4: Broadcast message from one client is received by all peer clients."""
    c1 = MultiClient("127.0.0.1", TEST_SERVER_PORT, "Broadcaster")
    c2 = MultiClient("127.0.0.1", TEST_SERVER_PORT, "Listener_1")
    c3 = MultiClient("127.0.0.1", TEST_SERVER_PORT, "Listener_2")

    recvd_msgs_2 = []
    recvd_msgs_3 = []
    c2.on_message = lambda m: recvd_msgs_2.append(m) if m.get("type") == "chat" else None
    c3.on_message = lambda m: recvd_msgs_3.append(m) if m.get("type") == "chat" else None

    assert c1.connect() is True
    assert c2.connect() is True
    assert c3.connect() is True
    time.sleep(0.3)

    c1.broadcast("Hello World to all clients!")
    time.sleep(0.4)

    assert any(m.get("message") == "Hello World to all clients!" for m in recvd_msgs_2)
    assert any(m.get("message") == "Hello World to all clients!" for m in recvd_msgs_3)

    c1.disconnect()
    c2.disconnect()
    c3.disconnect()

def test_05_disconnect_and_metrics_integrity(multi_server):
    """Test 5: Client disconnection cleanly decrements active count and maintains stats."""
    prev_total = multi_server.stats.total_connections
    c = MultiClient("127.0.0.1", TEST_SERVER_PORT, "Ephemeral_User")
    c.connect()
    time.sleep(0.2)
    assert multi_server.stats.total_connections > prev_total
    active_now = multi_server.stats.active_clients

    c.disconnect()
    time.sleep(0.3)
    assert multi_server.stats.active_clients == active_now - 1
