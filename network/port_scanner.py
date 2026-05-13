#!/usr/bin/env python3
import argparse
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

COMMON_SERVICES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 143: "imap", 443: "https", 445: "smb",
    465: "smtps", 587: "smtp-submission", 993: "imaps", 995: "pop3s",
    1433: "mssql", 1521: "oracle", 3306: "mysql", 3389: "rdp",
    5432: "postgresql", 5900: "vnc", 6379: "redis", 8080: "http-alt",
    8443: "https-alt", 8888: "http-alt", 9200: "elasticsearch",
    27017: "mongodb",
}


def service_name(port: int) -> str:
    try:
        return socket.getservbyport(port)
    except OSError:
        return COMMON_SERVICES.get(port, "unknown")


def parse_ports(spec: str) -> list[int]:
    ports = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            ports.extend(range(int(lo), int(hi) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def scan_port(host: str, port: int, timeout: float, banner: bool) -> dict:
    result = {"port": port, "state": "closed", "service": service_name(port), "banner": None}
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            result["state"] = "open"
            if banner:
                try:
                    sock.settimeout(2)
                    data = sock.recv(1024)
                    result["banner"] = data.decode("utf-8", errors="replace").strip()
                except Exception:
                    pass
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    return result


def main():
    parser = argparse.ArgumentParser(description="TCP connect port scanner.")
    parser.add_argument("target", help="Hostname or IP address to scan")
    parser.add_argument("--ports", default="1-1024", metavar="RANGE",
                        help="Port range or list (e.g. '1-1024' or '22,80,443'). Default: 1-1024")
    parser.add_argument("--timeout", type=float, default=1.0, metavar="SECS",
                        help="Per-connection timeout in seconds (default: 1)")
    parser.add_argument("--threads", type=int, default=100, metavar="N",
                        help="Concurrent threads (default: 100)")
    parser.add_argument("--banner", action="store_true",
                        help="Attempt to grab service banner on open ports")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    try:
        host = socket.gethostbyname(args.target)
    except socket.gaierror as e:
        sys.exit(f"Error resolving {args.target}: {e}")

    ports = parse_ports(args.ports)
    print(f"Scanning {args.target} ({host}) — {len(ports)} port(s)\n")

    open_ports = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(scan_port, host, p, args.timeout, args.banner): p for p in ports}
        for future in as_completed(futures):
            r = future.result()
            if r["state"] == "open":
                open_ports.append(r)

    open_ports.sort(key=lambda x: x["port"])

    if not open_ports:
        print("No open ports found.")
    else:
        print(f"{'PORT':<8} {'STATE':<8} {'SERVICE':<18} {'BANNER'}")
        print("-" * 60)
        for r in open_ports:
            banner = (r["banner"] or "")[:40]
            print(f"{r['port']:<8} {r['state']:<8} {r['service']:<18} {banner}")

    print(f"\n{len(open_ports)} open port(s) found.")

    if args.output:
        data = {"target": args.target, "host": host, "open_ports": open_ports}
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
