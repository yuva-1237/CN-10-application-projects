"""Traffic Aggregator and Statistical Protocol Analyzer."""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DEFAULT_PACKET_LIMIT, LOGS_DIR
from app.dissector import PacketMetadata
from app.sniffer import PacketSniffer

class NetworkTrafficAnalyzer:
    def __init__(self, packets: List[PacketMetadata]):
        self.packets = packets

    def generate_report(self) -> Dict[str, Any]:
        """Compute statistical breakdown of protocols, bandwidth, and endpoints."""
        total_packets = len(self.packets)
        total_bytes = sum(p.raw_length for p in self.packets)

        proto_counts = Counter(p.protocol_name for p in self.packets)
        src_ip_counts = Counter(p.src_ip for p in self.packets if p.src_ip)
        dst_ip_counts = Counter(p.dst_ip for p in self.packets if p.dst_ip)
        dst_port_counts = Counter(p.dst_port for p in self.packets if p.dst_port)

        proto_distribution = {}
        for proto, count in proto_counts.items():
            pct = (count / total_packets * 100.0) if total_packets > 0 else 0.0
            proto_distribution[proto] = {
                "count": count,
                "percentage": round(pct, 2)
            }

        return {
            "summary": {
                "total_packets": total_packets,
                "total_bytes": total_bytes,
                "average_packet_size": round(total_bytes / total_packets, 2) if total_packets > 0 else 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "protocol_distribution": proto_distribution,
            "top_source_ips": dict(src_ip_counts.most_common(5)),
            "top_destination_ips": dict(dst_ip_counts.most_common(5)),
            "top_destination_ports": dict(dst_port_counts.most_common(5))
        }

    def print_cli_summary(self, report: Dict[str, Any]) -> None:
        """Render clean terminal summary."""
        s = report["summary"]
        print("\n" + "=" * 65)
        print("         NETWORK TRAFFIC ANALYSIS REPORT")
        print("=" * 65)
        print(f"Total Packets Analyzed : {s['total_packets']}")
        print(f"Total Volume Captured  : {s['total_bytes']} bytes")
        print(f"Average Packet Size    : {s['average_packet_size']} bytes")
        print(f"Report Generated At    : {s['timestamp']}")

        print("\n[Protocol Distribution]")
        for proto, data in report["protocol_distribution"].items():
            bar = "#" * int(data["percentage"] / 4)
            print(f"  {proto:<10}: {data['count']:>4} pkts ({data['percentage']:>5.1f}%) | {bar}")

        print("\n[Top Source IPs]")
        for ip, cnt in report["top_source_ips"].items():
            print(f"  {ip:<20}: {cnt} packets")

        print("\n[Top Destination Ports]")
        for port, cnt in report["top_destination_ports"].items():
            print(f"  Port {port:<15}: {cnt} connections")
        print("=" * 65 + "\n")

    def export_json(self, filepath: Path) -> None:
        """Save report to JSON file."""
        report = self.generate_report()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[EXPORT] Analysis exported to: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Packet Sniffer & Network Analyzer")
    parser.add_argument("--count", type=int, default=DEFAULT_PACKET_LIMIT, help="Number of packets to capture")
    parser.add_argument("--filter", default="ALL", help="Protocol filter (ALL, TCP, UDP, ICMP, DNS, HTTP)")
    parser.add_argument("--sample", action="store_true", help="Force SAMPLE DATA MODE")
    parser.add_argument("--export", default=None, help="Path to export JSON analysis report")
    args = parser.parse_args()

    print("""
============================================================
           PACKET SNIFFER & NETWORK ANALYZER
============================================================
* EDUCATIONAL USE ONLY: Capture only on authorized interfaces.
============================================================
    """)

    sniffer = PacketSniffer(force_sample=args.sample)

    def print_pkt(p: PacketMetadata):
        src = f"{p.src_ip}:{p.src_port}" if p.src_port else (p.src_ip or "N/A")
        dst = f"{p.dst_ip}:{p.dst_port}" if p.dst_port else (p.dst_ip or "N/A")
        extra = f"[{p.app_hint}]" if p.app_hint else ""
        print(f"[{p.protocol_name:<4}] {src:<22} -> {dst:<22} | Len: {p.raw_length:<4} {extra}")

    packets = sniffer.capture(count=args.count, filter_proto=args.filter, on_packet=print_pkt)

    analyzer = NetworkTrafficAnalyzer(packets)
    report = analyzer.generate_report()
    analyzer.print_cli_summary(report)

    if args.export:
        analyzer.export_json(Path(args.export))
    else:
        out_file = LOGS_DIR / f"analysis_{int(time.time())}.json"
        analyzer.export_json(out_file)

if __name__ == "__main__":
    main()
