"""Low-Level Host and Port Probing Mechanisms (ICMP and TCP)."""
import platform
import re
import socket
import subprocess
import time
from typing import Dict, List, Tuple

def ping_host(host: str, timeout_sec: float = 1.0) -> Tuple[bool, float]:
    """Execute cross-platform ICMP ping to measure host liveness and RTT latency in milliseconds.
    
    Falls back to TCP connection probe if ICMP is blocked or restricted.
    """
    sys_name = platform.system().lower()
    timeout_ms = int(timeout_sec * 1000)

    if "win" in sys_name:
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(int(max(1, timeout_sec))), host]

    t_start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec + 1.0
        )
        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        if proc.returncode == 0:
            out = proc.stdout
            # Extract latency from ping output
            # Windows: time<1ms or time=12ms; Linux: time=12.3 ms
            match = re.search(r"time[<=](\d+(?:\.\d+)?)\s*ms", out, re.IGNORECASE)
            if match:
                latency = float(match.group(1))
            else:
                latency = round(elapsed_ms, 2)
            return True, latency
    except Exception:
        pass

    # Fallback TCP probe on port 80/443/53 to determine liveness if ICMP was dropped
    for fallback_port in (80, 443, 53, 22):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_sec)
        try:
            t0 = time.perf_counter()
            err = s.connect_ex((host, fallback_port))
            lat = (time.perf_counter() - t0) * 1000.0
            # 0 = open, 10061/111 = closed/refused (host is actively rejecting, meaning host IS ONLINE!)
            if err in (0, 10061, 111):
                return True, round(lat, 2)
        except Exception:
            pass
        finally:
            s.close()

    return False, -1.0

def probe_tcp_port(host: str, port: int, timeout_sec: float = 1.0) -> str:
    """Probe state of an individual TCP port on an authorized host.
    
    Returns:
    - OPEN: Port accepted connection
    - CLOSED: Host actively reset connection (RST / connection refused)
    - FILTERED: Connection timed out (firewalled)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_sec)
    try:
        s.connect((host, port))
        return "OPEN"
    except ConnectionRefusedError:
        return "CLOSED"
    except (socket.timeout, TimeoutError):
        return "FILTERED"
    except OSError as e:
        if getattr(e, "winerror", None) in (10061, 10035) or e.errno in (10061, 111):
            return "CLOSED"
        elif getattr(e, "winerror", None) == 10060 or e.errno in (10060, 110):
            return "FILTERED"
        return "UNREACHABLE"
    finally:
        try:
            s.close()
        except Exception:
            pass

def probe_host_ports(host: str, ports: List[int], timeout_sec: float = 0.5) -> Dict[int, str]:
    """Probe a list of authorized ports on the target host."""
    results = {}
    for p in ports:
        results[p] = probe_tcp_port(host, p, timeout_sec)
    return results
