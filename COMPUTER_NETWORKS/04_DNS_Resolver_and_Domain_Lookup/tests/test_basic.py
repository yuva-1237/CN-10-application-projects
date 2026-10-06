"""Automated tests for Project 04: DNS Resolver and Domain Lookup."""
import socket
import struct
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.dns_wire import (
    QTYPE_A,
    build_dns_query,
    decode_domain_name,
    encode_domain_name,
    parse_dns_response,
)
from app.resolver import DNSResolver
from app.utils import DNSCache

def test_01_encode_domain_name_labels():
    """Test 1: RFC 1035 label encoding (e.g. 'example.com' -> \\x07example\\x03com\\x00)."""
    encoded = encode_domain_name("example.com")
    expected = b"\x07example\x03com\x00"
    assert encoded == expected

    encoded_sub = encode_domain_name("mail.google.com")
    assert encoded_sub == b"\x04mail\x06google\x03com\x00"

def test_02_build_dns_query_packet():
    """Test 2: Raw UDP DNS query contains standard 12-byte header with RD bit set."""
    query_bytes, qid = build_dns_query("example.com", qtype=QTYPE_A)
    assert len(query_bytes) > 12

    # Unpack 12-byte header
    hdr_id, flags, qdcount, ancount, nscount, arcount = struct.unpack("!HHHHHH", query_bytes[:12])
    assert hdr_id == qid
    assert flags == 0x0100  # Recursion Desired
    assert qdcount == 1
    assert ancount == 0

def test_03_dns_response_parser_mock():
    """Test 3: Parser correctly unpacks DNS A-record response bytes."""
    # Synthesize an RFC-compliant DNS response datagram
    # Header: ID=0x1234, Flags=0x8180 (Standard response, No error), QD=1, AN=1, NS=0, AR=0
    header = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0)
    # Question: \x07example\x03com\x00, QTYPE=1 (A), QCLASS=1 (IN)
    question = b"\x07example\x03com\x00" + struct.pack("!HH", 1, 1)
    # Answer: Name pointer to offset 12 (0xC00C), Type=1 (A), Class=1, TTL=300, RDLen=4, IP=93.184.216.34
    answer = struct.pack("!HHHIH4s", 0xC00C, 1, 1, 300, 4, socket.inet_aton("93.184.216.34"))

    mock_resp = header + question + answer
    parsed = parse_dns_response(mock_resp)

    assert parsed["id"] == 0x1234
    assert parsed["ancount"] == 1
    assert len(parsed["answers"]) == 1
    assert parsed["answers"][0]["data"] == "93.184.216.34"
    assert parsed["answers"][0]["ttl"] == 300

def test_04_cache_hit_and_miss_mechanisms():
    """Test 4: Cache returns miss on first lookup, hit on second lookup with near-zero latency."""
    cache = DNSCache(default_ttl=60)
    assert cache.get("test.com") is None
    assert cache.misses == 1

    cache.set("test.com", {"ip": "1.2.3.4"})
    hit_val = cache.get("test.com")
    assert hit_val == {"ip": "1.2.3.4"}
    assert cache.hits == 1

    cache.clear()
    assert cache.get("test.com") is None
    assert cache.stats()["active_entries"] == 0

def test_05_resolve_domain_localhost_and_system():
    """Test 5: Resolve localhost or well-known domain returns valid IP and latency."""
    resolver = DNSResolver()
    res = resolver.resolve_domain("localhost")

    assert res["domain"] == "localhost"
    assert len(res["ipv4"]) > 0
    assert "127.0.0.1" in res["ipv4"]
    assert res["latency_ms"] >= 0
    assert res["cached"] is False

    # Second lookup must be a cache hit
    res_cached = resolver.resolve_domain("localhost")
    assert res_cached["cached"] is True
