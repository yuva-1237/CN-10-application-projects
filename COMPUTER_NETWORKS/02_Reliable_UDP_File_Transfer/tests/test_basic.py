"""Automated tests for Project 02: Reliable UDP File Transfer."""
import sys
import tempfile
import threading
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app.packet import (
    RUDPAckPacket,
    RUDPDataPacket,
    STATUS_OK,
    TYPE_DATA,
)
from app.receiver import RUDPReceiver
from app.sender import RUDPSender
from app.utils import calculate_sha256

TEST_UDP_PORT = 5922

def test_01_packet_packing_and_crc32_integrity():
    """Test 1: Verify data packet correctly calculates CRC-32 and deserializes payload."""
    payload = b"Reliable UDP Data Chunk 0123456789"
    pkt = RUDPDataPacket(TYPE_DATA, transfer_id=101, seq_num=1, total_packets=5, payload=payload)
    packed_bytes = pkt.pack()

    unpacked = RUDPDataPacket.unpack(packed_bytes)
    assert unpacked is not None
    assert unpacked.pkt_type == TYPE_DATA
    assert unpacked.transfer_id == 101
    assert unpacked.seq_num == 1
    assert unpacked.total_packets == 5
    assert unpacked.payload == payload

def test_02_corrupted_packet_detection():
    """Test 2: Modifying even one bit in the payload causes CRC-32 rejection."""
    payload = b"Original uncorrupted message"
    pkt = RUDPDataPacket(TYPE_DATA, transfer_id=202, seq_num=2, total_packets=10, payload=payload)
    packed = bytearray(pkt.pack())

    # Tamper with the last byte
    packed[-1] ^= 0xFF

    corrupted_unpack = RUDPDataPacket.unpack(bytes(packed))
    assert corrupted_unpack is None, "Corrupted packet was unexpectedly accepted!"

def test_03_ack_packet_packing():
    """Test 3: ACK packet serialization and deserialization."""
    ack = RUDPAckPacket(transfer_id=303, ack_seq=7, status=STATUS_OK)
    packed = ack.pack()
    unpacked = RUDPAckPacket.unpack(packed)
    assert unpacked is not None
    assert unpacked.transfer_id == 303
    assert unpacked.ack_seq == 7
    assert unpacked.status == STATUS_OK

def test_04_clean_udp_file_transfer():
    """Test 4: Clean file transfer over UDP with zero packet loss."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        sender_dir = temp_path / "sender"
        receiver_dir = temp_path / "receiver"
        sender_dir.mkdir()
        receiver_dir.mkdir()

        test_file = sender_dir / "clean_transfer.bin"
        test_data = b"Computer Networks Reliable UDP Test Buffer\n" * 200  # ~8.6 KB
        test_file.write_bytes(test_data)
        original_sha = calculate_sha256(test_file)

        receiver = RUDPReceiver(host="127.0.0.1", port=TEST_UDP_PORT, output_dir=receiver_dir)
        recv_thread = threading.Thread(target=receiver.start, kwargs={"single_transfer": True}, daemon=True)
        recv_thread.start()
        time.sleep(0.2)

        sender = RUDPSender(
            receiver_host="127.0.0.1",
            receiver_port=TEST_UDP_PORT,
            chunk_size=1024,
            timeout=0.3,
            simulated_loss=0.0
        )
        success, stats = sender.send_file(test_file)
        sender.close()
        recv_thread.join(timeout=3.0)

        assert success is True
        assert stats["retransmissions"] == 0
        assert stats["simulated_drops"] == 0

        received_files = list(receiver_dir.glob("rudp_*clean_transfer.bin"))
        assert len(received_files) == 1
        assert calculate_sha256(received_files[0]) == original_sha

def test_05_packet_loss_retransmission_and_recovery():
    """Test 5: Simulate 25% packet drop rate; sender retransmits and receiver reconstructs valid file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        sender_dir = temp_path / "sender"
        receiver_dir = temp_path / "receiver"
        sender_dir.mkdir()
        receiver_dir.mkdir()

        test_file = sender_dir / "lossy_transfer.txt"
        test_data = b"Line: Simulated Packet Loss and Retransmission Test Data!\n" * 50
        test_file.write_bytes(test_data)
        original_sha = calculate_sha256(test_file)

        test_port = TEST_UDP_PORT + 1
        receiver = RUDPReceiver(host="127.0.0.1", port=test_port, output_dir=receiver_dir)
        recv_thread = threading.Thread(target=receiver.start, kwargs={"single_transfer": True}, daemon=True)
        recv_thread.start()
        time.sleep(0.2)

        sender = RUDPSender(
            receiver_host="127.0.0.1",
            receiver_port=test_port,
            chunk_size=512,
            timeout=0.15,
            max_retries=10,
            simulated_loss=0.30  # 30% drop probability
        )
        success, stats = sender.send_file(test_file)
        sender.close()
        recv_thread.join(timeout=5.0)

        assert success is True
        # Verify that drops occurred and were recovered via retransmissions
        if stats["simulated_drops"] > 0:
            assert stats["retransmissions"] >= stats["simulated_drops"]

        received_files = list(receiver_dir.glob("rudp_*lossy_transfer.txt"))
        assert len(received_files) == 1
        assert calculate_sha256(received_files[0]) == original_sha
