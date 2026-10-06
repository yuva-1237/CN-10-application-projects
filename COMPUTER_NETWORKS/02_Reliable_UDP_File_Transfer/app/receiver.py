"""Reliable UDP Receiver with ARQ, ACK generation, and Integrity Verification.

Listens on a UDP port, processes incoming data packets, validates CRC32 checksums,
sends ACK datagrams, filters duplicate packets, and reconstructs files.
"""
import argparse
import json
import random
import socket
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import LOGS_DIR, RECEIVER_DIR, RECEIVER_HOST, RECEIVER_PORT
from app.packet import (
    RUDPAckPacket,
    RUDPDataPacket,
    STATUS_OK,
    TYPE_DATA,
    TYPE_END,
    TYPE_START,
)
from app.utils import calculate_sha256, format_bytes, setup_logger

logger = setup_logger("RUDP_Receiver", LOGS_DIR / "receiver.log")

class RUDPReceiver:
    def __init__(
        self,
        host: str = RECEIVER_HOST,
        port: int = RECEIVER_PORT,
        output_dir: Path = RECEIVER_DIR,
        simulated_loss: float = 0.0
    ):
        self.host = host
        self.port = port
        self.output_dir = output_dir
        self.simulated_loss = simulated_loss
        self.sock: Optional[socket.socket] = None
        self.is_running = False

        # Metrics
        self.packets_received = 0
        self.packets_dropped_simulated = 0
        self.corrupted_packets_detected = 0
        self.duplicate_packets = 0

    def start(self, single_transfer: bool = False) -> Optional[Path]:
        """Bind and process incoming UDP packets."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.is_running = True

        logger.info("=" * 60)
        logger.info("  RELIABLE UDP FILE RECEIVER STARTED")
        logger.info(f"  Listening on UDP : {self.host}:{self.port}")
        logger.info(f"  Storage Directory: {self.output_dir}")
        if self.simulated_loss > 0:
            logger.warning(f"  SIMULATION MODE: Simulated ACK/Packet Drop Rate = {self.simulated_loss * 100:.1f}%")
        logger.info("=" * 60)

        active_transfer: Optional[dict] = None
        final_file_path: Optional[Path] = None

        try:
            while self.is_running:
                try:
                    data, client_addr = self.sock.recvfrom(65535)
                except OSError:
                    break

                self.packets_received += 1

                # Simulate inbound packet loss if configured
                if self.simulated_loss > 0 and random.random() < self.simulated_loss:
                    self.packets_dropped_simulated += 1
                    logger.warning(f"[SIMULATION] Dropped incoming packet from {client_addr} (Simulated Loss)")
                    continue

                packet = RUDPDataPacket.unpack(data)
                if packet is None:
                    self.corrupted_packets_detected += 1
                    logger.warning(f"Corrupted packet received from {client_addr}! Discarding.")
                    continue

                # Handle START
                if packet.pkt_type == TYPE_START:
                    meta = json.loads(packet.payload.decode("utf-8"))
                    active_transfer = {
                        "transfer_id": packet.transfer_id,
                        "filename": meta["filename"],
                        "filesize": meta["filesize"],
                        "total_packets": packet.total_packets,
                        "expected_sha": meta["sha256"],
                        "chunks": {},
                        "client_addr": client_addr,
                        "start_time": time.time()
                    }
                    logger.info(f"Initiated Transfer #{packet.transfer_id}: '{meta['filename']}' ({format_bytes(meta['filesize'])} across {packet.total_packets} packets)")
                    ack = RUDPAckPacket(packet.transfer_id, packet.seq_num, STATUS_OK)
                    self.sock.sendto(ack.pack(), client_addr)

                # Handle DATA
                elif packet.pkt_type == TYPE_DATA:
                    if active_transfer and active_transfer["transfer_id"] == packet.transfer_id:
                        if packet.seq_num in active_transfer["chunks"]:
                            self.duplicate_packets += 1
                        else:
                            active_transfer["chunks"][packet.seq_num] = packet.payload

                        # Send ACK
                        ack = RUDPAckPacket(packet.transfer_id, packet.seq_num, STATUS_OK)
                        self.sock.sendto(ack.pack(), client_addr)
                    else:
                        logger.warning(f"Orphan data packet SEQ {packet.seq_num} received without active transfer.")

                # Handle END
                elif packet.pkt_type == TYPE_END:
                    if active_transfer and active_transfer["transfer_id"] == packet.transfer_id:
                        # Send final ACK
                        ack = RUDPAckPacket(packet.transfer_id, packet.seq_num, STATUS_OK)
                        self.sock.sendto(ack.pack(), client_addr)

                        # Reassemble file
                        final_file_path = self._reassemble_file(active_transfer)
                        active_transfer = None
                        if single_transfer:
                            break

        finally:
            self.stop()

        return final_file_path

    def _reassemble_file(self, transfer: dict) -> Path:
        """Stitch chunks sequentially and verify final checksum."""
        filename = transfer["filename"]
        out_path = self.output_dir / f"rudp_{int(time.time())}_{filename}"
        total = transfer["total_packets"]
        chunks: Dict[int, bytes] = transfer["chunks"]

        logger.info(f"Reassembling {len(chunks)}/{total} packets into {out_path.name}...")
        with open(out_path, "wb") as f:
            for seq in range(1, total + 1):
                chunk = chunks.get(seq, b"")
                f.write(chunk)

        actual_sha = calculate_sha256(out_path)
        duration = max(time.time() - transfer["start_time"], 0.001)
        speed = (transfer["filesize"] / 1024.0) / duration

        logger.info("=" * 60)
        logger.info("  TRANSFER COMPLETE")
        logger.info(f"  Target File          : {out_path.name}")
        logger.info(f"  Total Packets        : {total}")
        logger.info(f"  Duplicate Packets    : {self.duplicate_packets}")
        logger.info(f"  Simulated Drops      : {self.packets_dropped_simulated}")
        logger.info(f"  Corrupt Drops        : {self.corrupted_packets_detected}")
        logger.info(f"  Duration             : {duration:.2f}s ({speed:.2f} KB/s)")
        logger.info(f"  Expected SHA-256     : {transfer['expected_sha']}")
        logger.info(f"  Calculated SHA-256   : {actual_sha}")
        if actual_sha == transfer["expected_sha"]:
            logger.info("  >> INTEGRITY STATUS  : [VERIFIED MATCH - 100% RELIABLE] <<")
        else:
            logger.error("  >> INTEGRITY STATUS  : [CORRUPTED CHECKSUM MISMATCH] <<")
        logger.info("=" * 60)
        return out_path

    def stop(self) -> None:
        """Stop listening and close socket."""
        self.is_running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        logger.info("Receiver stopped.")

def main():
    parser = argparse.ArgumentParser(description="Reliable UDP File Receiver")
    parser.add_argument("--host", default=RECEIVER_HOST, help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=RECEIVER_PORT, help="Port to listen (default: 5002)")
    parser.add_argument("--loss", type=float, default=0.0, help="Simulate packet loss fraction (0.0 to 0.5)")
    args = parser.parse_args()

    receiver = RUDPReceiver(host=args.host, port=args.port, simulated_loss=args.loss)
    try:
        receiver.start()
    except KeyboardInterrupt:
        logger.info("\nReceiver stopped by user.")
        receiver.stop()

if __name__ == "__main__":
    main()
