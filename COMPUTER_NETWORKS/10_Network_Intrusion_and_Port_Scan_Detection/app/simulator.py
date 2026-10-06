"""Controlled Local Test Scanner for IDS Demonstration."""
import argparse
import socket
import sys
import time

def simulate_port_scan(target_host: str = "127.0.0.1", ports: list[int] | None = None, delay: float = 0.1) -> None:
    """Connect to a series of ports on the local machine to trigger the IDS detection heuristic."""
    ports_to_test = ports or [5010, 5011, 5012, 5013, 5014, 5015, 5016]

    print("\n" + "=" * 68)
    print("  SIMULATED LOCAL PORT SCAN (BENIGN TEST PROBE)")
    print("=" * 68)
    print("  * NOTICE: Strictly targeting localhost (127.0.0.1) for educational verification.")
    print(f"  Target Host : {target_host}")
    print(f"  Ports to Hit: {ports_to_test}")
    print(f"  Delay       : {delay}s between connection attempts")
    print("=" * 68 + "\n")

    for p in ports_to_test:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            print(f"Connecting to {target_host}:{p} ...", end=" ", flush=True)
            s.connect((target_host, p))
            print("[SYN-ACK: Connected]")
        except ConnectionRefusedError:
            print("[RST: Connection Refused]")
        except Exception as e:
            print(f"[Error: {e}]")
        finally:
            s.close()
        time.sleep(delay)

    print("\nSimulated scan completed. Inspect the IDS Engine terminal to see the generated alert.")

def main():
    parser = argparse.ArgumentParser(description="Simulated Local Port Scanner for IDS Testing")
    parser.add_argument("--host", default="127.0.0.1", help="Target host (strictly localhost / private)")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between connection attempts in seconds")
    args = parser.parse_args()

    if args.host not in ("127.0.0.1", "localhost"):
        print("Error: For educational safety, simulation only targets 127.0.0.1 (localhost).")
        sys.exit(1)

    simulate_port_scan(target_host=args.host, delay=args.delay)

if __name__ == "__main__":
    main()
