#!/usr/bin/env python3
import argparse
import email
import ipaddress
import json
import re
import sys
from email import policy


IP_RE = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
RECEIVED_FROM_RE = re.compile(r"from\s+(\S+)\s+\(([^)]+)\)", re.IGNORECASE)


def classify_ip(ip_str: str) -> str:
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private:
            return "private"
        if ip.is_loopback:
            return "loopback"
        return "public"
    except ValueError:
        return "invalid"


def parse_received(header_value: str) -> dict:
    ips = IP_RE.findall(header_value)
    classified = [{"ip": ip, "type": classify_ip(ip)} for ip in ips]
    match = RECEIVED_FROM_RE.search(header_value)
    hostname = match.group(1) if match else None
    return {"raw": header_value.strip(), "hostname": hostname, "ips": classified}


def analyze(msg: email.message.Message) -> dict:
    result: dict = {}

    for field in ("From", "To", "Subject", "Date", "Message-ID", "Reply-To"):
        result[field] = msg.get(field, "")

    result["relay_chain"] = [
        parse_received(h) for h in reversed(msg.get_all("Received") or [])
    ]

    auth_results = msg.get("Authentication-Results", "")
    result["authentication"] = {
        "spf":   "pass" if "spf=pass"   in auth_results.lower() else
                 "fail" if "spf=fail"   in auth_results.lower() else "none",
        "dkim":  "pass" if "dkim=pass"  in auth_results.lower() else
                 "fail" if "dkim=fail"  in auth_results.lower() else "none",
        "dmarc": "pass" if "dmarc=pass" in auth_results.lower() else
                 "fail" if "dmarc=fail" in auth_results.lower() else "none",
    }

    flags = []
    from_addr = result.get("From", "")
    reply_to  = result.get("Reply-To", "")
    if reply_to and reply_to.strip() and reply_to.strip() != from_addr.strip():
        flags.append(f"Reply-To ({reply_to}) differs from From ({from_addr})")

    auth = result["authentication"]
    if auth["spf"] == "fail":
        flags.append("SPF check failed")
    if auth["dkim"] == "fail":
        flags.append("DKIM check failed")
    if auth["dmarc"] == "fail":
        flags.append("DMARC check failed")

    result["flags"] = flags
    return result


def print_result(r: dict) -> None:
    fields = ["From", "To", "Subject", "Date", "Message-ID", "Reply-To"]
    for f in fields:
        if r.get(f):
            print(f"{f:12s}: {r[f]}")

    print("\n--- Authentication ---")
    for k, v in r["authentication"].items():
        print(f"  {k.upper():6s}: {v}")

    print("\n--- Relay Chain ---")
    for i, hop in enumerate(r["relay_chain"], 1):
        print(f"  Hop {i}: {hop['hostname'] or 'unknown'}")
        for ip_info in hop["ips"]:
            print(f"    IP: {ip_info['ip']}  ({ip_info['type']})")

    if r["flags"]:
        print("\n--- Flags ---")
        for flag in r["flags"]:
            print(f"  [!] {flag}")
    else:
        print("\nNo suspicious flags detected.")


def main():
    parser = argparse.ArgumentParser(description="Analyze email headers for relay chain and authentication.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", metavar="FILE", help="Path to raw .eml file")
    src.add_argument("--stdin", action="store_true", help="Read raw email from stdin")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
    else:
        with open(args.file, "r", errors="replace") as f:
            raw = f.read()

    msg = email.message_from_string(raw, policy=policy.compat32)
    result = analyze(msg)
    print_result(result)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
