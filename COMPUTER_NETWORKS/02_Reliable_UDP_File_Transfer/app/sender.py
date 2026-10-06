"""Reliable UDP Sender with ARQ Stop-and-Wait, Timeouts, and Simulated Loss.

Chunks files into datagrams, applies CRC32 checksums, sends over UDP,
waits for acknowledgments (ACKs), and performs automatic retransmission upon timeout.
"""
import argparse
import json
import math
import random
import socket
import sys
import time
from pathlib import Path
from typing import Dict, Tuple

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import (
    LOGS_DIR,
    MAX_RETRIES,
    PACKET_PAYLOAD_SIZE,
    RECEIVER_HOST,
    RECEIVER_PORT,
    TIMEOUT_SECONDS,
)
from app.packet import (
    RUDPAckPacket,
    RUDPDataPacket,
    STATUS_OK,
    TYPE_DATA,
    TYPE_END,
    TYPE_START,
)
from app.utils import calculate_sha256, format_bytes, setup_logger

logger = setup_logger("RUDP_Sender", LOGS_DIR / "sender.log")

class RUDPSender:
    def __init__(
        self,
        receiver_host: str = RECEIVER_HOST,
        receiver_port: int = RECEIVER_PORT,
        chunk_size: int = PACKET_PAYLOAD_SIZE,
        timeout: float = TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
        simulated_loss: float = 0.0
    ):
        self.receiver_addr = (receiver_host, receiver_port)
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.max_retries = max_retries
        self.simulated_loss = simulated_loss
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)

        # Statistics
        self.total_packets_sent = 0
        self.retransmissions = 0
        self.simulated_drops = 0

    def _send_with_ack(self, packet: RUDPDataPacket) -> bool:
        """Send a packet and wait for its corresponding ACK. Retransmit on timeout."""
        data_bytes = packet.pack()
        attempt = 0

        while attempt <= self.max_retries:
            attempt += 1
            self.total_packets_sent += 1

            # Simulated packet loss check
            if self.simulated_loss > 0 and random.random() < self.simulated_loss:
                self.simulated_drops += 1
                logger.warning(
                    f"[SIMULATION] Dropped SEQ #{packet.seq_num} on attempt {attempt}/{self.max_retries + 1} (Simulated Loss)"
                )
            else:
                self.sock.sendto(data_bytes, self.receiver_addr)

            # Wait for ACK
            try:
                ack_data, _ = self.sock.recvfrom(1024)
                ack = RUDPAckPacket.unpack(ack_data)
                if ack and ack.transfer_id == packet.transfer_id and ack.ack_seq == packet.seq_num:
                    if ack.status == STATUS_OK:
                        return True
                    else:
                        logger.warning(f"Receiver signaled corrupt SEQ #{packet.seq_num}. Retransmitting...")
                else:
                    logger.debug(f"Received mismatched ACK {ack.ack_seq if ack else None}, expected {packet.seq_num}")
            except socket.timeout:
                self.retransmissions += 1
                logger.warning(
                    f"Timeout waiting for ACK #{packet.seq_num}! Retransmitting (Attempt {attempt}/{self.max_retries + 1})..."
                )

        logger.error(f"Exceeded max retries ({self.max_retries}) for packet SEQ #{packet.seq_num}. Transfer failed.")
        return False

    def send_file(self, filepath: Path) -> Tuple[bool, Dict[str, float]]:
        """Reliably transmit an entire file over UDP."""
        if not filepath.exists() or not filepath.is_file():
            logger.error(f"File not found: {filepath}")
            return False, {}

        filesize = filepath.stat().st_size
        sha256_hash = calculate_sha256(filepath)
        total_packets = max(1, math.ceil(filesize / self.chunk_size)) if filesize > 0 else 1
        transfer_id = random.randint(1000, 65535)

        logger.info("=" * 60)
        logger.info("  RELIABLE UDP FILE SENDER INITIATED")
        logger.info(f"  Target Receiver      : {self.receiver_addr[0]}:{self.receiver_addr[1]}")
        logger.info(f"  File Name            : {filepath.name}")
        logger.info(f"  File Size            : {format_bytes(filesize)} ({filesize} bytes)")
        logger.info(f"  Total Data Packets   : {total_packets}")
        logger.info(f"  Chunk Size           : {self.chunk_size} bytes")
        logger.info(f"  Timeout Window       : {self.timeout}s")
        if self.simulated_loss > 0:
            logger.warning(f"  SIMULATION MODE      : Simulated Drop Rate = {self.simulated_loss * 100:.1f}%")
        logger.info("=" * 60)

        start_time = time.time()

        # Step 1: Send START packet with metadata
        start_meta = json.dumps({
            "filename": filepath.name,
            "filesize": filesize,
            "sha256": sha256_hash
        }).encode("utf-8")

        start_pkt = RUDPDataPacket(TYPE_START, transfer_id, 0, total_packets, start_meta)
        if not self._send_with_ack(start_pkt):
            return False, {}

        # Step 2: Sequentially stream data packets
        seq = 1
        with open(filepath, "rb") as f:
            while chunk := f.read(self.chunk_size):
                pkt = RUDPDataPacket(TYPE_DATA, transfer_id, seq, total_packets, chunk)
                if not self._send_with_ack(pkt):
                    return False, {}
                seq += 1

        # Step 3: Send END packet
        end_pkt = RUDPDataPacket(TYPE_END, transfer_id, seq, total_packets, b"END")
        if not self._send_with_ack(end_pkt):
            return False, {}

        elapsed = max(time.time() - start_time, 0.001)
        speed = (filesize / 1024.0) / elapsed

        stats = {
            "elapsed_seconds": elapsed,
            "speed_kbps": speed,
            "total_packets_sent": self.total_packets_sent,
            "retransmissions": self.retransmissions,
            "simulated_drops": self.simulated_drops,
            "file_size": filesize
        }

        logger.info("=" * 60)
        logger.info("  TRANSFER SUMMARY")
        logger.info(f"  Status               : SUCCESS (100% Delivered)")
        logger.info(f"  Elapsed Time         : {elapsed:.2f} seconds")
        logger.info(f"  Throughput           : {speed:.2f} KB/s")
        logger.info(f"  Total Transmissions  : {self.total_packets_sent}")
        logger.info(f"  Retransmissions      : {self.retransmissions}")
        logger.info(f"  Simulated Drops      : {self.simulated_drops}")
        logger.info("=" * 60)

        return True, stats

    def close(self):
        self.sock.close()

def main():
    parser = argparse.ArgumentParser(description="Reliable UDP File Sender")
    parser.add_argument("file", help="Path to file to transmit")
    parser.add_argument("--host", default=RECEIVER_HOST, help="Receiver IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=RECEIVER_PORT, help="Receiver port (default: 5002)")
    parser.add_argument("--loss", type=float, default=0.0, help="Simulate drop rate (e.g. 0.1 for 10% packet loss)")
    parser.add_argument("--timeout", type=float, default=TIMEOUT_SECONDS, help="ACK timeout in seconds")
    args = parser.parse_args()

    sender = RUDPSender(
        receiver_host=args.host,
        receiver_port=args.port,
        simulated_loss=args.loss,
        timeout=args.timeout
    )
    try:
        success, _ = sender.send_file(Path(args.file))
        if not success:
            sys.exit(1)
    finally:
        sender.close()

if __name__ == "__main__":
    main()
