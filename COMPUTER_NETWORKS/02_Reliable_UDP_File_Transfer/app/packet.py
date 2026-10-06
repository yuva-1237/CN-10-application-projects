"""Binary Packet encoding and decoding for Reliable UDP Transport.

Data Packet Header Format (17 bytes):
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |  Type (1B)    |  Transfer ID (2B)             |  Seq Num (4B) |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |  Seq Num (cont.)              | Total Packets (4B)            |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Total Packets | Payload Len(2)| Checksum CRC-32 (4 bytes)     |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Checksum(cnt) | [Variable Payload up to MTU] ...              |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

ACK Packet Format (11 bytes):
  Type (1B=2) | Transfer ID (2B) | ACK Seq Num (4B) | Status (4B: 0=OK)
"""
import struct
from typing import Optional, Tuple
from app.utils import calculate_crc32

TYPE_DATA = 1
TYPE_ACK = 2
TYPE_START = 3
TYPE_END = 4

# Header: type (B), transfer_id (H), seq_num (I), total_packets (I), payload_len (H), checksum (I)
DATA_HEADER_FMT = "!B H I I H I"
DATA_HEADER_SIZE = struct.calcsize(DATA_HEADER_FMT)

# ACK Header: type (B), transfer_id (H), ack_seq (I), status (I)
ACK_HEADER_FMT = "!B H I I"
ACK_HEADER_SIZE = struct.calcsize(ACK_HEADER_FMT)

STATUS_OK = 0
STATUS_CORRUPT = 1

class RUDPDataPacket:
    def __init__(self, pkt_type: int, transfer_id: int, seq_num: int, total_packets: int, payload: bytes):
        self.pkt_type = pkt_type
        self.transfer_id = transfer_id
        self.seq_num = seq_num
        self.total_packets = total_packets
        self.payload = payload

    def pack(self) -> bytes:
        """Serialize packet into binary datagram with calculated CRC32 checksum."""
        # Pack with checksum = 0 to calculate checksum over header + payload
        temp_header = struct.pack(
            DATA_HEADER_FMT,
            self.pkt_type,
            self.transfer_id,
            self.seq_num,
            self.total_packets,
            len(self.payload),
            0
        )
        checksum = calculate_crc32(temp_header + self.payload)
        # Pack finalized header with real checksum
        header = struct.pack(
            DATA_HEADER_FMT,
            self.pkt_type,
            self.transfer_id,
            self.seq_num,
            self.total_packets,
            len(self.payload),
            checksum
        )
        return header + self.payload

    @classmethod
    def unpack(cls, raw_bytes: bytes) -> Optional["RUDPDataPacket"]:
        """Parse raw datagram and verify CRC32 integrity."""
        if len(raw_bytes) < DATA_HEADER_SIZE:
            return None

        header_bytes = raw_bytes[:DATA_HEADER_SIZE]
        payload = raw_bytes[DATA_HEADER_SIZE:]

        pkt_type, transfer_id, seq_num, total_packets, payload_len, recvd_checksum = struct.unpack(
            DATA_HEADER_FMT, header_bytes
        )

        if len(payload) != payload_len:
            return None

        # Verify CRC32
        check_header = struct.pack(
            DATA_HEADER_FMT,
            pkt_type,
            transfer_id,
            seq_num,
            total_packets,
            payload_len,
            0
        )
        expected_checksum = calculate_crc32(check_header + payload)
        if expected_checksum != recvd_checksum:
            return None  # Checksum mismatch / packet corrupted!

        return cls(pkt_type, transfer_id, seq_num, total_packets, payload)

class RUDPAckPacket:
    def __init__(self, transfer_id: int, ack_seq: int, status: int = STATUS_OK):
        self.pkt_type = TYPE_ACK
        self.transfer_id = transfer_id
        self.ack_seq = ack_seq
        self.status = status

    def pack(self) -> bytes:
        """Serialize ACK packet."""
        return struct.pack(
            ACK_HEADER_FMT,
            self.pkt_type,
            self.transfer_id,
            self.ack_seq,
            self.status
        )

    @classmethod
    def unpack(cls, raw_bytes: bytes) -> Optional["RUDPAckPacket"]:
        """Parse raw ACK datagram."""
        if len(raw_bytes) != ACK_HEADER_SIZE:
            return None
        pkt_type, transfer_id, ack_seq, status = struct.unpack(ACK_HEADER_FMT, raw_bytes)
        if pkt_type != TYPE_ACK:
            return None
        return cls(transfer_id, ack_seq, status)
