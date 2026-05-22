#!/usr/bin/env python3
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    sys.exit("Error: requests not installed. Run: pip install requests")

PLATFORMS = {
    "GitHub":       "https://github.com/{u}",
    "GitLab":       "https://gitlab.com/{u}",
    "Reddit":       "https://www.reddit.com/user/{u}",
    "HackerNews":   "https://news.ycombinator.com/user?id={u}",
    "Dev.to":       "https://dev.to/{u}",
    "Mastodon":     "https://mastodon.social/@{u}",
    "Keybase":      "https://keybase.io/{u}",
    "Replit":       "https://replit.com/@{u}",
    "Pastebin":     "https://pastebin.com/u/{u}",
    "CodePen":      "https://codepen.io/{u}",
    "Gravatar":     "https://gravatar.com/{u}",
    "Twitch":       "https://www.twitch.tv/{u}",
    "Steam":        "https://steamcommunity.com/id/{u}",
    "Spotify":      "https://open.spotify.com/user/{u}",
    "Lichess":      "https://lichess.org/@/{u}",
    "Chess.com":    "https://www.chess.com/member/{u}",
    "Kaggle":       "https://www.kaggle.com/{u}",
    "Npmjs":        "https://www.npmjs.com/~{u}",
    "PyPI":         "https://pypi.org/user/{u}/",
    "Sourcehut":    "https://sr.ht/~{u}",
}

FOUND_CODES = {200, 201}
NOT_FOUND_CODES = {404, 410}


def check_platform(platform: str, url: str, username: str, timeout: float) -> dict:
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code in FOUND_CODES:
            status = "found"
        elif resp.status_code in NOT_FOUND_CODES:
            status = "not_found"
        else:
            status = f"unknown ({resp.status_code})"
    except requests.Timeout:
        status = "timeout"
    except requests.ConnectionError:
        status = "error"
    except Exception as e:
        status = f"error ({e})"

    return {"platform": platform, "url": url, "status": status}


def main():
    parser = argparse.ArgumentParser(description="Search for a username across multiple platforms.")
    parser.add_argument("username", help="Username to search for")
    parser.add_argument("--timeout", type=float, default=5.0, metavar="SECS", help="Per-request timeout (default: 5)")
    parser.add_argument("--threads", type=int, default=10, metavar="N", help="Concurrent threads (default: 10)")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    u = args.username
    print(f"Searching for username: {u}\n")

    tasks = {
        platform: url.format(u=u) for platform, url in PLATFORMS.items()
    }

    results = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(check_platform, platform, url, u, args.timeout): platform
            for platform, url in tasks.items()
        }
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            mark = "[+]" if r["status"] == "found" else "[-]" if r["status"] == "not_found" else "[?]"
            print(f"{mark} {r['platform']:15s} {r['status']:20s} {r['url']}")

    found = [r for r in results if r["status"] == "found"]
    print(f"\n{len(found)}/{len(results)} platforms matched.")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"username": u, "results": results}, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
