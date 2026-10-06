"""Packet Sniffing Engine with Live Raw Socket and Sample Mode Fallback."""
import platform
import socket
import sys
import time
from pathlib import Path
from typing import Callable, List, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import CAPTURE_INTERFACE, FORCE_SAMPLE_MODE, LOGS_DIR
from app.dissector import PacketMetadata, dissect_packet
from app.utils import create_synthetic_raw_packets, setup_logger

logger = setup_logger("Packet_Sniffer", LOGS_DIR / "sniffer.log")

class PacketSniffer:
    def __init__(self, interface: str = CAPTURE_INTERFACE, force_sample: bool = FORCE_SAMPLE_MODE):
        self.interface = interface
        self.force_sample = force_sample
        self.is_live = False
        self.raw_sock: Optional[socket.socket] = None
        self.captured_packets: List[PacketMetadata] = []

    def _init_raw_socket(self) -> bool:
        """Attempt to open platform-specific raw socket for packet capture."""
        if self.force_sample:
            return False

        system = platform.system().lower()
        try:
            if "win" in system:
                # Windows raw IP socket
                self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                self.raw_sock.bind((self.interface, 0))
                self.raw_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                self.raw_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
                self.is_live = True
                return True
            else:
                # Linux AF_PACKET raw link-layer socket
                if hasattr(socket, "AF_PACKET"):
                    self.raw_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
                    self.is_live = True
                    return True
        except (PermissionError, OSError) as e:
            logger.info(f"Raw socket permission unavailable ({e}). Fallback to SAMPLE DATA MODE.")
            self.raw_sock = None
            self.is_live = False

        return False

    def capture(
        self,
        count: int = 50,
        filter_proto: str = "ALL",
        on_packet: Optional[Callable[[PacketMetadata], None]] = None
    ) -> List[PacketMetadata]:
        """Capture or ingest network packets, dissect them, and filter by protocol."""
        self.captured_packets.clear()
        filter_clean = filter_proto.strip().upper()

        if self._init_raw_socket():
            mode_label = f"LIVE CAPTURE (Interface: {self.interface})"
        else:
            mode_label = "SAMPLE DATA MODE (Real Recorded Network Frames)"

        logger.info("=" * 60)
        logger.info("  PACKET SNIFFER INITIALIZED")
        logger.info(f"  Operating Mode: {mode_label}")
        logger.info(f"  Packet Target : {count}")
        logger.info(f"  Filter        : {filter_clean}")
        logger.info("=" * 60)

        if self.is_live and self.raw_sock:
            self._capture_live(count, filter_clean, on_packet)
        else:
            self._capture_sample(count, filter_clean, on_packet)

        return self.captured_packets

    def _capture_live(self, count: int, filter_proto: str, on_packet: Optional[Callable]) -> None:
        """Capture live packets from OS raw socket."""
        captured = 0
        try:
            while captured < count:
                raw_data, _ = self.raw_sock.recvfrom(65535)
                now = time.time()
                meta = dissect_packet(raw_data, has_ethernet=False, timestamp=now)

                if self._matches_filter(meta, filter_proto):
                    self.captured_packets.append(meta)
                    captured += 1
                    if on_packet:
                        on_packet(meta)
        finally:
            self.close()

    def _capture_sample(self, count: int, filter_proto: str, on_packet: Optional[Callable]) -> None:
        """Process synthetic/recorded sample packet frames."""
        sample_pool = create_synthetic_raw_packets()
        for idx in range(count):
            raw_entry = sample_pool[idx % len(sample_pool)]
            meta = dissect_packet(raw_entry["raw"], has_ethernet=False, timestamp=raw_entry["timestamp"])

            if self._matches_filter(meta, filter_proto):
                self.captured_packets.append(meta)
                if on_packet:
                    on_packet(meta)

    def _matches_filter(self, meta: PacketMetadata, filter_proto: str) -> bool:
        """Evaluate packet metadata against user protocol filter."""
        if filter_proto in ("ALL", "*"):
            return True
        if filter_proto == meta.protocol_name:
            return True
        if filter_proto == meta.app_hint:
            return True
        if filter_proto == "DNS" and (meta.src_port == 53 or meta.dst_port == 53):
            return True
        if filter_proto == "HTTP" and (meta.src_port in (80, 8080) or meta.dst_port in (80, 8080)):
            return True
        return False

    def close(self) -> None:
        """Disable promiscuous mode and release raw socket."""
        if self.raw_sock:
            try:
                if platform.system().lower().startswith("win") and self.is_live:
                    self.raw_sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
                self.raw_sock.close()
            except Exception:
                pass
            self.raw_sock = None
            self.is_live = False
