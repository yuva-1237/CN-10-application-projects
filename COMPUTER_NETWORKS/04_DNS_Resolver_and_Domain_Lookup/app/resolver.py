"""DNS Resolver and Domain Information System.

Performs low-level UDP DNS queries and OS-level lookups for IPv4, IPv6, MX,
CNAME, reverse lookups, latency benchmarking, and TTL caching.
"""
import argparse
import socket
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Enable running as script or module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import (
    DEFAULT_CACHE_TTL,
    DNS_PORT,
    DNS_TIMEOUT,
    LOGS_DIR,
    PRIMARY_DNS,
    SECONDARY_DNS,
)
from app.dns_wire import (
    QTYPE_A,
    QTYPE_AAAA,
    QTYPE_MX,
    QTYPE_TXT,
    build_dns_query,
    parse_dns_response,
)
from app.utils import DNSCache, setup_logger

logger = setup_logger("DNS_Resolver", LOGS_DIR / "resolver.log")

class DNSResolver:
    def __init__(
        self,
        primary_dns: str = PRIMARY_DNS,
        port: int = DNS_PORT,
        timeout: float = DNS_TIMEOUT,
        cache_ttl: int = DEFAULT_CACHE_TTL
    ):
        self.primary_dns = primary_dns
        self.port = port
        self.timeout = timeout
        self.cache = DNSCache(default_ttl=cache_ttl)

    def query_raw_udp(self, domain: str, qtype: int = QTYPE_A, server: Optional[str] = None) -> Dict[str, Any]:
        """Perform raw UDP socket query to DNS server on port 53."""
        target_server = server or self.primary_dns
        query_bytes, qid = build_dns_query(domain, qtype)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)

        start_time = time.perf_counter()
        try:
            sock.sendto(query_bytes, (target_server, self.port))
            resp_bytes, _ = sock.recvfrom(4096)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            parsed = parse_dns_response(resp_bytes)
            parsed["latency_ms"] = round(elapsed_ms, 2)
            parsed["server"] = target_server
            return parsed
        except socket.timeout:
            return {"error": "Timeout waiting for DNS response", "latency_ms": -1, "server": target_server}
        except Exception as e:
            return {"error": str(e), "latency_ms": -1, "server": target_server}
        finally:
            sock.close()

    def resolve_domain(self, domain: str, use_cache: bool = True) -> Dict[str, Any]:
        """Full domain lookup resolving IPv4, IPv6, and reverse PTR."""
        clean_domain = domain.strip().lower()

        # Check Cache
        if use_cache:
            cached = self.cache.get(clean_domain)
            if cached:
                cached_copy = dict(cached)
                cached_copy["cached"] = True
                cached_copy["latency_ms"] = 0.05  # Near zero for cache hit
                return cached_copy

        t_start = time.perf_counter()
        ipv4_list: List[str] = []
        ipv6_list: List[str] = []
        reverse_name: Optional[str] = None
        method_used = "RAW_UDP_PORT_53"
        server_used = self.primary_dns

        # 1. Try raw UDP query for IPv4
        raw_res = self.query_raw_udp(clean_domain, QTYPE_A)
        if "answers" in raw_res and raw_res["answers"]:
            for ans in raw_res["answers"]:
                if ans["type"] == QTYPE_A and ans["data"]:
                    ipv4_list.append(ans["data"])

        # 2. Try raw UDP query for IPv6
        raw_v6 = self.query_raw_udp(clean_domain, QTYPE_AAAA)
        if "answers" in raw_v6 and raw_v6["answers"]:
            for ans in raw_v6["answers"]:
                if ans["type"] == QTYPE_AAAA and ans["data"]:
                    ipv6_list.append(ans["data"])

        # 3. Fallback to OS socket resolver if raw UDP was blocked by firewall or empty
        if not ipv4_list and not ipv6_list:
            method_used = "OS_GETADDRINFO_FALLBACK"
            server_used = "System Configured DNS"
            try:
                addr_info = socket.getaddrinfo(clean_domain, None)
                for entry in addr_info:
                    family, _, _, _, sockaddr = entry
                    ip = sockaddr[0]
                    if family == socket.AF_INET and ip not in ipv4_list:
                        ipv4_list.append(ip)
                    elif family == socket.AF_INET6 and ip not in ipv6_list:
                        ipv6_list.append(ip)
            except socket.gaierror as e:
                logger.warning(f"Domain lookup failed for {clean_domain}: {e}")

        # 4. Reverse Lookup on first IPv4
        if ipv4_list:
            try:
                reverse_name = socket.gethostbyaddr(ipv4_list[0])[0]
            except Exception:
                reverse_name = "Not Available (No PTR Record)"

        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        result = {
            "domain": clean_domain,
            "ipv4": ipv4_list,
            "ipv6": ipv6_list,
            "reverse_name": reverse_name,
            "latency_ms": round(elapsed_ms, 2),
            "dns_server": server_used,
            "method": method_used,
            "cached": False,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if ipv4_list or ipv6_list:
            self.cache.set(clean_domain, result)

        return result

    def reverse_lookup(self, ip_address: str) -> Dict[str, Any]:
        """Perform reverse PTR lookup for an IP address."""
        t_start = time.perf_counter()
        try:
            hostname, aliases, _ = socket.gethostbyaddr(ip_address)
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return {
                "ip": ip_address,
                "hostname": hostname,
                "aliases": aliases,
                "latency_ms": round(elapsed_ms, 2),
                "status": "SUCCESS"
            }
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return {
                "ip": ip_address,
                "hostname": None,
                "error": str(e),
                "latency_ms": round(elapsed_ms, 2),
                "status": "NOT_FOUND"
            }

def main():
    parser = argparse.ArgumentParser(description="DNS Resolver & Domain Information Tool")
    parser.add_argument("domain", nargs="?", help="Domain name or IP to lookup (e.g. google.com or 8.8.8.8)")
    parser.add_argument("--server", default=PRIMARY_DNS, help=f"Upstream DNS Server (default: {PRIMARY_DNS})")
    parser.add_argument("--reverse", action="store_true", help="Perform reverse lookup on IP")
    args = parser.parse_args()

    resolver = DNSResolver(primary_dns=args.server)

    target = args.domain or input("Enter domain name or IP address: ").strip()
    if not target:
        print("Input cannot be empty.")
        return

    if args.reverse or target.replace(".", "").isdigit():
        print(f"\nPerforming Reverse Lookup for: {target}")
        res = resolver.reverse_lookup(target)
        print("=" * 60)
        print(f"IP Address      : {res['ip']}")
        print(f"Resolved Host   : {res.get('hostname') or res.get('error')}")
        print(f"Resolution Time : {res['latency_ms']} ms")
        print("=" * 60)
    else:
        print(f"\nResolving Domain: {target} via {args.server}...")
        res = resolver.resolve_domain(target)
        print("=" * 60)
        print("  DNS RESOLUTION REPORT")
        print("=" * 60)
        print(f"Domain Name     : {res['domain']}")
        print(f"IPv4 Addresses  : {', '.join(res['ipv4']) if res['ipv4'] else 'None'}")
        print(f"IPv6 Addresses  : {', '.join(res['ipv6']) if res['ipv6'] else 'None'}")
        print(f"Reverse Hostname: {res['reverse_name']}")
        print(f"Resolution Time : {res['latency_ms']} ms")
        print(f"DNS Server Used : {res['dns_server']}")
        print(f"Resolver Engine : {res['method']}")
        print(f"Cache Status    : {'CACHE HIT' if res['cached'] else 'LIVE NETWORK QUERY'}")
        print("=" * 60)

if __name__ == "__main__":
    main()
