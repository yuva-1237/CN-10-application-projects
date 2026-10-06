"""Automated tests for Project 03: Mini HTTP Web Server & Client."""
import socket
import sys
import threading
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.client import HTTPClient
from app.http_parser import HTTPRequest, HTTPResponse
from app.server import MiniHTTPServer

TEST_HTTP_PORT = 5933

@pytest.fixture(scope="module")
def http_server():
    """Start the Mini HTTP Server on an isolated loopback port."""
    server = MiniHTTPServer(host="127.0.0.1", port=TEST_HTTP_PORT)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)  # Wait for socket to bind
    yield server
    server.stop()
    time.sleep(0.2)

def test_01_server_socket_startup(http_server):
    """Test 1: Server accepts raw TCP connection on port."""
    assert http_server.is_running is True
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", TEST_HTTP_PORT))
        assert True
    finally:
        sock.close()

def test_02_get_index_html(http_server):
    """Test 2: GET /index.html returns 200 OK and text/html."""
    client = HTTPClient(host="127.0.0.1", port=TEST_HTTP_PORT)
    status, headers, body, _ = client.send_request("GET", "/index.html")

    assert status == 200
    assert "text/html" in headers.get("content-type", "")
    assert b"Mini HTTP Web Server" in body

def test_03_head_method_omits_body(http_server):
    """Test 3: HEAD request returns 200 OK and headers, but body must be empty per RFC 2616."""
    client = HTTPClient(host="127.0.0.1", port=TEST_HTTP_PORT)
    status, headers, body, _ = client.send_request("HEAD", "/index.html")

    assert status == 200
    assert "content-length" in headers
    assert int(headers["content-length"]) > 0
    assert len(body) == 0, f"HEAD response must have 0 body bytes, got {len(body)}"

def test_04_404_not_found(http_server):
    """Test 4: Nonexistent resource path returns 404 Not Found."""
    client = HTTPClient(host="127.0.0.1", port=TEST_HTTP_PORT)
    status, headers, body, _ = client.send_request("GET", "/non_existent_file_abc.html")

    assert status == 404
    assert b"404" in body

def test_05_405_method_not_allowed(http_server):
    """Test 5: POST method is rejected with 405 Method Not Allowed."""
    client = HTTPClient(host="127.0.0.1", port=TEST_HTTP_PORT)
    status, headers, body, _ = client.send_request("POST", "/index.html", body=b"sample_data")

    assert status == 405
    assert "allow" in headers
    assert "GET, HEAD" in headers["allow"]
