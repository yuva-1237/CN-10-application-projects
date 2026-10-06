"""Master Test Suite Runner for the 10 Computer Networks Academic Projects.

Runs each project's test suite independently in an isolated Python process
to guarantee complete project decoupling and generate an audit summary.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

PROJECTS = [
    ("01_LAN_Chat_and_File_Sharing", "LAN Chat & File Sharing"),
    ("02_Reliable_UDP_File_Transfer", "Reliable UDP File Transfer"),
    ("03_Mini_HTTP_Web_Server", "Mini HTTP Web Server"),
    ("04_DNS_Resolver_and_Domain_Lookup", "DNS Resolver & Domain Lookup"),
    ("05_Network_Routing_Simulator", "Network Routing Simulator"),
    ("06_Packet_Sniffer_and_Network_Analyzer", "Packet Sniffer & Network Analyzer"),
    ("07_TCP_Congestion_Control_Simulator", "TCP Congestion Control Simulator"),
    ("08_Multi_Client_Network_Server", "Multi-Client Network Server"),
    ("09_Network_Monitoring_and_Device_Discovery", "Network Monitoring & Device Discovery"),
    ("10_Network_Intrusion_and_Port_Scan_Detection", "Network Intrusion & Port Scan Detection"),
]

def main():
    print("=" * 75)
    print("      COMPUTER NETWORKS ACADEMIC PROJECTS — MASTER AUDIT RUNNER")
    print("=" * 75)

    results = {}
    total_passed = 0
    t0 = time.time()

    for folder_name, title in PROJECTS:
        proj_dir = ROOT_DIR / folder_name
        test_file = proj_dir / "tests" / "test_basic.py"

        if not test_file.exists():
            print(f"[-] {folder_name:<46}: MISSING TESTS")
            results[folder_name] = ("FAIL (Missing tests)", 0)
            continue

        # Execute pytest in isolated process inside project working directory
        cmd = [sys.executable, "-m", "pytest", "tests/test_basic.py", "-v"]
        res = subprocess.run(cmd, cwd=proj_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if res.returncode == 0:
            print(f"[+] {folder_name:<46}: PASS")
            results[folder_name] = ("PASS", res.stdout.count("PASSED"))
            total_passed += 1
        else:
            print(f"[!] {folder_name:<46}: FAIL")
            results[folder_name] = ("FAIL", 0)
            print(res.stdout)
            print(res.stderr)

    elapsed = time.time() - t0
    print("\n" + "=" * 75)
    print(f"  FINAL AUDIT SCORE: {total_passed}/{len(PROJECTS)} PROJECTS PASSED ({elapsed:.2f}s)")
    print("=" * 75)
    for folder_name, (status, count) in results.items():
        print(f"  {folder_name:<46} : {status} ({count} test cases)")
    print("=" * 75 + "\n")

    return 0 if total_passed == len(PROJECTS) else 1

if __name__ == "__main__":
    sys.exit(main())
