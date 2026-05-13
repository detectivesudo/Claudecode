#!/usr/bin/env python3
import argparse
import json
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import dns.resolver
    import dns.exception
except ImportError:
    sys.exit("Error: dnspython not installed. Run: pip install dnspython")

DEFAULT_WORDLIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "wordlists", "subdomains-small.txt"
)


def resolve_a(subdomain: str, resolver: dns.resolver.Resolver, timeout: float) -> list[str]:
    try:
        answers = resolver.resolve(subdomain, "A", lifetime=timeout)
        return [str(r) for r in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout,
            dns.resolver.NoNameservers):
        return []
    except Exception:
        return []


def check_wildcard(domain: str, resolver: dns.resolver.Resolver, timeout: float) -> set[str]:
    probe = f"{uuid.uuid4().hex}.{domain}"
    ips = resolve_a(probe, resolver, timeout)
    return set(ips)


def main():
    parser = argparse.ArgumentParser(description="Enumerate subdomains via DNS brute-force.")
    parser.add_argument("domain", help="Target domain (e.g. example.com)")
    parser.add_argument("--wordlist", default=DEFAULT_WORDLIST, metavar="FILE",
                        help="Wordlist of subdomain prefixes (default: bundled subdomains-small.txt)")
    parser.add_argument("--threads", type=int, default=20, metavar="N",
                        help="Concurrent threads (default: 20)")
    parser.add_argument("--timeout", type=float, default=3.0, metavar="SECS",
                        help="DNS query timeout (default: 3)")
    parser.add_argument("--wildcard-check", action="store_true",
                        help="Detect and suppress wildcard DNS responses")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    resolver = dns.resolver.Resolver()

    wildcard_ips: set[str] = set()
    if args.wildcard_check:
        wildcard_ips = check_wildcard(args.domain, resolver, args.timeout)
        if wildcard_ips:
            print(f"[!] Wildcard DNS detected (resolves to {wildcard_ips}). Results may be noisy.\n")

    if not os.path.isfile(args.wordlist):
        sys.exit(f"Error: wordlist not found: {args.wordlist}")

    with open(args.wordlist) as f:
        prefixes = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"Domain: {args.domain} | Wordlist: {len(prefixes)} entries\n")

    found: list[dict] = []

    def check(prefix: str) -> dict | None:
        sub = f"{prefix}.{args.domain}"
        ips = resolve_a(sub, resolver, args.timeout)
        if not ips:
            return None
        if wildcard_ips and set(ips) == wildcard_ips:
            return None
        return {"subdomain": sub, "ips": ips}

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(check, p): p for p in prefixes}
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
                ips_str = ", ".join(result["ips"])
                print(f"[+] {result['subdomain']:<40} {ips_str}")

    found.sort(key=lambda x: x["subdomain"])
    print(f"\n{len(found)} subdomain(s) found.")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"domain": args.domain, "subdomains": found}, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
