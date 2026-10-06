import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.client import ChatClient
from app.protocol import recv_msg, send_msg
from app.server import ChatServer
from app.utils import calculate_sha256

TEST_PORT = 5911

@pytest.fixture(scope="module")
def running_server():
    """Start a test server on a dedicated loopback port."""
    server = ChatServer(host="127.0.0.1", port=TEST_PORT)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)  # Allow server to bind and listen
    yield server
    server.stop()
    time.sleep(0.2)

def test_01_server_bind_and_listen(running_server):
    """Test 1: Server starts and binds to localhost port."""
    assert running_server.is_running is True
    assert running_server.server_sock is not None
    # Verify port is accepting TCP connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", TEST_PORT))
        assert True
    finally:
        sock.close()

def test_02_protocol_framing_integrity():
    """Test 2: Protocol framing packs and unrolls header and payload without corruption."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(("127.0.0.1", port))
    conn, _ = server_sock.accept()

    try:
        header = {"type": "test", "val": 12345, "status": "OK"}
        payload = b"Sample Binary Stream with \x00\x01\x02 Bytes"
        send_msg(client_sock, header, payload)

        recvd_header, recvd_payload = recv_msg(conn)
        assert recvd_header == header
        assert recvd_payload == payload
    finally:
        client_sock.close()
        conn.close()
        server_sock.close()

def test_03_client_registration(running_server):
    """Test 3: Client connects and successfully registers a unique username."""
    client = ChatClient(host="127.0.0.1", port=TEST_PORT, username="Alice_Test")
    assert client.connect() is True
    assert client.is_connected is True
    time.sleep(0.2)
    assert "Alice_Test" in running_server.clients
    client.disconnect()
    time.sleep(0.2)
    assert "Alice_Test" not in running_server.clients

def test_04_multi_client_broadcast_and_private(running_server):
    """Test 4: Two clients connect and exchange broadcast and private messages."""
    received_msgs = []

    def on_bob_msg(header, payload):
        if header.get("type") in ("chat", "private"):
            received_msgs.append((header.get("type"), header.get("sender"), header.get("message")))

    alice = ChatClient(host="127.0.0.1", port=TEST_PORT, username="Alice")
    bob = ChatClient(host="127.0.0.1", port=TEST_PORT, username="Bob")

    assert alice.connect() is True
    assert bob.connect() is True
    bob.on_message_callback = on_bob_msg
    time.sleep(0.3)

    # Broadcast message from Alice
    alice.send_chat("Hello everyone!")
    time.sleep(0.3)
    assert any(m[0] == "chat" and m[1] == "Alice" and m[2] == "Hello everyone!" for m in received_msgs)

    # Private message from Alice to Bob
    alice.send_private("Bob", "Secret 123")
    time.sleep(0.3)
    assert any(m[0] == "private" and m[1] == "Alice" and m[2] == "Secret 123" for m in received_msgs)

    alice.disconnect()
    bob.disconnect()

def test_05_file_transfer_and_checksum_verification(running_server):
    """Test 5: Stream file over TCP and verify recipient computes matching SHA-256."""
    with tempfile.TemporaryDirectory() as temp_dir:
        download_path = Path(temp_dir) / "downloads"
        upload_path = Path(temp_dir) / "uploads"
        download_path.mkdir()
        upload_path.mkdir()

        # Create a sample file with random text
        test_file = upload_path / "test_doc.txt"
        test_content = b"Computer Networks Academic Lab Project - File Sharing Stream Test!" * 100
        test_file.write_bytes(test_content)
        expected_sha = calculate_sha256(test_file)

        sender = ChatClient(host="127.0.0.1", port=TEST_PORT, username="FileSender")
        receiver = ChatClient(host="127.0.0.1", port=TEST_PORT, username="FileReceiver", downloads_dir=download_path)

        assert sender.connect() is True
        assert receiver.connect() is True
        time.sleep(0.2)

        # Transmit file to FileReceiver
        assert sender.send_file(test_file, recipient="FileReceiver") is True
        time.sleep(0.5)

        # Verify downloaded file
        downloaded_files = list(download_path.glob("recvd_*test_doc.txt"))
        assert len(downloaded_files) == 1
        recvd_file = downloaded_files[0]
        assert recvd_file.read_bytes() == test_content
        assert calculate_sha256(recvd_file) == expected_sha

        sender.disconnect()
        receiver.disconnect()
