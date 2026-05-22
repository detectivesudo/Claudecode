#!/usr/bin/env python3
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    sys.exit("Error: requests not installed. Run: pip install requests")

DEFAULT_CODES = {200, 201, 301, 302, 403}


def make_session() -> requests.Session:
    s = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=1, backoff_factor=0.5))
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": "Mozilla/5.0 (web-fuzzer/1.0)"})
    return s


def fuzz_path(session: requests.Session, base: str, path: str,
              timeout: float, delay: float) -> dict | None:
    url = f"{base.rstrip('/')}/{path}"
    if delay:
        time.sleep(delay / 1000)
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=False)
        return {
            "path": path,
            "url": url,
            "status": resp.status_code,
            "size": len(resp.content),
            "redirect": resp.headers.get("Location"),
        }
    except requests.Timeout:
        return None
    except requests.ConnectionError:
        return None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Directory and path enumeration tool.",
        epilog="IMPORTANT: Only use against systems you own or have written permission to test.",
    )
    parser.add_argument("url", help="Target base URL (e.g. https://example.com)")
    parser.add_argument("--wordlist", required=True, metavar="FILE",
                        help="Path to wordlist file")
    parser.add_argument("--threads", type=int, default=10, metavar="N",
                        help="Concurrent threads (default: 10)")
    parser.add_argument("--timeout", type=float, default=5.0, metavar="SECS",
                        help="Request timeout (default: 5)")
    parser.add_argument("--status-codes", default="200,201,301,302,403", metavar="CODES",
                        help="Comma-separated status codes to report (default: 200,201,301,302,403)")
    parser.add_argument("--extensions", metavar="EXT",
                        help="Comma-separated extensions to append (e.g. php,html,txt)")
    parser.add_argument("--delay", type=float, default=0, metavar="MS",
                        help="Delay between requests per thread in milliseconds (default: 0)")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    report_codes = {int(c.strip()) for c in args.status_codes.split(",")}
    extensions = [e.strip().lstrip(".") for e in args.extensions.split(",")] if args.extensions else []

    if not args.wordlist:
        parser.error("--wordlist is required")

    try:
        with open(args.wordlist) as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        sys.exit(f"Wordlist not found: {args.wordlist}")

    paths = list(words)
    for word in words:
        for ext in extensions:
            paths.append(f"{word}.{ext}")

    print(f"[!] Authorized use only. Target: {args.url}")
    print(f"Wordlist: {len(words)} words | Extensions: {extensions or 'none'} | Paths: {len(paths)}\n")

    found = []
    session = make_session()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(fuzz_path, session, args.url, p, args.timeout, args.delay): p
            for p in paths
        }
        for future in as_completed(futures):
            r = future.result()
            if r and r["status"] in report_codes:
                found.append(r)
                redirect = f" -> {r['redirect']}" if r["redirect"] else ""
                print(f"[{r['status']}] {r['url']:<60} ({r['size']} bytes){redirect}")

    found.sort(key=lambda x: (x["status"], x["path"]))
    print(f"\n{len(found)} path(s) found.")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"target": args.url, "results": found}, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
