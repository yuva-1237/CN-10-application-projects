"""RFC 1035 Low-Level DNS Wire Protocol Encoder and Decoder.

Constructs raw binary DNS queries over UDP port 53 and decodes resource record answers.
"""
import random
import socket
import struct
from typing import Any, Dict, List, Tuple

# Record Types
QTYPE_A = 1       # IPv4
QTYPE_NS = 2      # Name Server
QTYPE_CNAME = 5   # Canonical Name
QTYPE_MX = 15     # Mail Exchange
QTYPE_AAAA = 28   # IPv6
QTYPE_TXT = 16    # Text Record

QCLASS_IN = 1     # Internet

def encode_domain_name(domain: str) -> bytes:
    """Encode string domain name to RFC 1035 wire labels (e.g. 'google.com' -> b'\x06google\x03com\x00')."""
    parts = domain.strip(".").split(".")
    encoded = bytearray()
    for part in parts:
        part_bytes = part.encode("ascii")
        encoded.append(len(part_bytes))
        encoded.extend(part_bytes)
    encoded.append(0)
    return bytes(encoded)

def decode_domain_name(data: bytes, offset: int) -> Tuple[str, int]:
    """Decode RFC 1035 domain name at offset, respecting compression pointers (0xC0)."""
    labels = []
    curr = offset
    jumped = False
    original_offset = offset

    while True:
        length = data[curr]
        if length == 0:
            curr += 1
            break
        # Pointer check (2 most significant bits set: 0b11xxxxxx -> 0xC0)
        elif (length & 0xC0) == 0xC0:
            pointer_offset = struct.unpack("!H", data[curr:curr + 2])[0] & 0x3FFF
            if not jumped:
                original_offset = curr + 2
                jumped = True
            curr = pointer_offset
        else:
            curr += 1
            labels.append(data[curr:curr + length].decode("ascii", errors="replace"))
            curr += length

    final_offset = original_offset if jumped else curr
    return ".".join(labels), final_offset

def build_dns_query(domain: str, qtype: int = QTYPE_A) -> Tuple[bytes, int]:
    """Construct a standard recursive DNS query datagram per RFC 1035."""
    query_id = random.randint(1000, 65535)
    flags = 0x0100  # Standard query, Recursion Desired (RD) bit set
    qdcount = 1     # One question
    ancount = 0
    nscount = 0
    arcount = 0

    header = struct.pack("!HHHHHH", query_id, flags, qdcount, ancount, nscount, arcount)
    qname = encode_domain_name(domain)
    qbody = struct.pack("!HH", qtype, QCLASS_IN)

    return header + qname + qbody, query_id

def parse_dns_response(data: bytes) -> Dict[str, Any]:
    """Unpack raw DNS UDP response datagram into structured record fields."""
    if len(data) < 12:
        return {"error": "Packet too short (<12 bytes)"}

    query_id, flags, qdcount, ancount, nscount, arcount = struct.unpack("!HHHHHH", data[:12])
    offset = 12

    # Skip question section
    for _ in range(qdcount):
        _, offset = decode_domain_name(data, offset)
        offset += 4  # skip QTYPE and QCLASS

    answers = []
    for _ in range(ancount):
        if offset >= len(data):
            break
        name, offset = decode_domain_name(data, offset)
        rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", data[offset:offset + 10])
        offset += 10
        rdata = data[offset:offset + rdlength]
        offset += rdlength

        value: Any = None
        if rtype == QTYPE_A and rdlength == 4:
            value = socket.inet_ntoa(rdata)
        elif rtype == QTYPE_AAAA and rdlength == 16:
            value = socket.inet_ntop(socket.AF_INET6, rdata)
        elif rtype in (QTYPE_CNAME, QTYPE_NS):
            value, _ = decode_domain_name(data, offset - rdlength)
        elif rtype == QTYPE_MX and rdlength >= 3:
            preference = struct.unpack("!H", rdata[:2])[0]
            mx_name, _ = decode_domain_name(data, offset - rdlength + 2)
            value = f"{preference} {mx_name}"
        elif rtype == QTYPE_TXT:
            value = rdata[1:].decode("utf-8", errors="replace")
        else:
            value = rdata.hex()

        answers.append({
            "name": name,
            "type": rtype,
            "ttl": ttl,
            "data": value
        })

    return {
        "id": query_id,
        "flags": flags,
        "rcode": flags & 0x000F,
        "ancount": ancount,
        "answers": answers
    }
