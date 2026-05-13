#!/usr/bin/env python3
import argparse
import json
import sys

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:
    sys.exit("Error: requests not installed. Run: pip install requests")

SECURITY_HEADERS = [
    {
        "name": "Strict-Transport-Security",
        "check": lambda v: ("PASS" if "max-age" in v.lower() else "WARN",
                            "OK" if "max-age" in v.lower() else "max-age directive missing"),
    },
    {
        "name": "Content-Security-Policy",
        "check": lambda v: ("PASS", "Present") if v else ("FAIL", "Missing"),
    },
    {
        "name": "X-Content-Type-Options",
        "check": lambda v: ("PASS", "OK") if v.lower() == "nosniff" else ("WARN", f"Unexpected value: {v}"),
    },
    {
        "name": "X-Frame-Options",
        "check": lambda v: ("PASS", "OK") if v.upper() in ("DENY", "SAMEORIGIN") else ("WARN", f"Value: {v}"),
    },
    {
        "name": "Referrer-Policy",
        "check": lambda v: ("PASS", v) if v else ("WARN", "Missing"),
    },
    {
        "name": "Permissions-Policy",
        "check": lambda v: ("PASS", "Present") if v else ("WARN", "Missing"),
    },
    {
        "name": "Cross-Origin-Opener-Policy",
        "check": lambda v: ("PASS", v) if v else ("WARN", "Missing"),
    },
    {
        "name": "Cross-Origin-Resource-Policy",
        "check": lambda v: ("PASS", v) if v else ("WARN", "Missing"),
    },
]

LEAKY_HEADERS = ["Server", "X-Powered-By", "X-AspNet-Version", "X-Generator", "X-Drupal-Cache"]


def analyze_headers(url: str, method: str, follow: bool, timeout: float) -> dict:
    try:
        resp = requests.request(
            method, url,
            timeout=timeout,
            allow_redirects=follow,
            headers={"User-Agent": "Mozilla/5.0 (security-header-check)"},
        )
    except RequestException as e:
        sys.exit(f"Request failed: {e}")

    headers = resp.headers
    results = []

    for spec in SECURITY_HEADERS:
        hname = spec["name"]
        val = headers.get(hname, "")
        if val:
            grade, note = spec["check"](val)
        else:
            grade, note = "FAIL", "Missing"
        results.append({"header": hname, "grade": grade, "note": note, "value": val})

    leaks = {}
    for h in LEAKY_HEADERS:
        val = headers.get(h)
        if val:
            leaks[h] = val

    return {
        "url": resp.url,
        "status_code": resp.status_code,
        "security_headers": results,
        "leaky_headers": leaks,
    }


def main():
    parser = argparse.ArgumentParser(description="Check HTTP security headers for a URL.")
    parser.add_argument("url", help="Target URL (e.g. https://example.com)")
    parser.add_argument("--method", choices=["GET", "HEAD"], default="HEAD",
                        help="HTTP method (default: HEAD)")
    parser.add_argument("--follow-redirects", action="store_true",
                        help="Follow redirects (up to 5)")
    parser.add_argument("--timeout", type=float, default=10.0, metavar="SECS",
                        help="Request timeout (default: 10)")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    data = analyze_headers(args.url, args.method, args.follow_redirects, args.timeout)

    print(f"URL:    {data['url']}")
    print(f"Status: {data['status_code']}\n")

    grade_counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    print(f"{'HEADER':<40} {'GRADE':<6} NOTE")
    print("-" * 80)
    for r in data["security_headers"]:
        grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1
        note = r["note"] or r["value"] or ""
        print(f"{r['header']:<40} {r['grade']:<6} {note}")

    if data["leaky_headers"]:
        print("\n[!] Information-leaking headers:")
        for h, v in data["leaky_headers"].items():
            print(f"  {h}: {v}")

    total = len(data["security_headers"])
    print(f"\nSummary: {grade_counts['PASS']} PASS / {grade_counts['WARN']} WARN / {grade_counts['FAIL']} FAIL  (of {total} headers checked)")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
