#!/usr/bin/env python3
import argparse
import json
import sys

try:
    import dns.resolver
    import dns.exception
except ImportError:
    sys.exit("Error: dnspython not installed. Run: pip install dnspython")

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]


def query(domain: str, rtype: str, resolver: dns.resolver.Resolver, timeout: float) -> list[str]:
    try:
        answers = resolver.resolve(domain, rtype, lifetime=timeout)
        results = []
        for rdata in answers:
            if rtype == "MX":
                results.append(f"{rdata.preference} {rdata.exchange}")
            elif rtype == "TXT":
                results.append(" ".join(p.decode() for p in rdata.strings))
            else:
                results.append(str(rdata))
        return results
    except dns.resolver.NXDOMAIN:
        return ["[NXDOMAIN — domain does not exist]"]
    except dns.resolver.NoAnswer:
        return []
    except dns.exception.Timeout:
        return ["[TIMEOUT]"]
    except Exception as e:
        return [f"[ERROR: {e}]"]


def main():
    parser = argparse.ArgumentParser(description="Enumerate DNS records for a domain.")
    parser.add_argument("domain", help="Target domain (e.g. example.com)")
    parser.add_argument(
        "--types", nargs="+", metavar="TYPE",
        choices=RECORD_TYPES, default=RECORD_TYPES,
        help=f"Record types to query (default: all). Choices: {', '.join(RECORD_TYPES)}",
    )
    parser.add_argument("--resolver", metavar="IP", help="Custom DNS resolver IP")
    parser.add_argument("--timeout", type=float, default=5.0, metavar="SECS", help="Query timeout (default: 5)")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    resolver = dns.resolver.Resolver()
    if args.resolver:
        resolver.nameservers = [args.resolver]

    all_results: dict[str, list[str]] = {}
    print(f"Domain: {args.domain}\n")

    for rtype in args.types:
        records = query(args.domain, rtype, resolver, args.timeout)
        all_results[rtype] = records
        if records:
            print(f"[{rtype}]")
            for r in records:
                print(f"  {r}")
        else:
            print(f"[{rtype}] (no records)")

    if args.output:
        data = {"domain": args.domain, "records": all_results}
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
