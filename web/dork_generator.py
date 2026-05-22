#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.parse

DORK_TEMPLATES: dict[str, list[str]] = {
    "login": [
        "site:{t} inurl:login",
        "site:{t} inurl:signin",
        "site:{t} intitle:\"Login\"",
        "site:{t} intitle:\"Sign in\"",
        "site:{t} inurl:admin",
        "site:{t} inurl:wp-login.php",
        "site:{t} inurl:wp-admin",
        "site:{t} inurl:/user/login",
        "site:{t} inurl:account/login",
        "site:{t} inurl:auth/login",
    ],
    "files": [
        "site:{t} filetype:pdf",
        "site:{t} filetype:xls",
        "site:{t} filetype:xlsx",
        "site:{t} filetype:csv",
        "site:{t} filetype:doc",
        "site:{t} filetype:docx",
        "site:{t} filetype:ppt",
        "site:{t} filetype:txt",
        "site:{t} filetype:log",
        "site:{t} filetype:xml",
    ],
    "config": [
        "site:{t} filetype:env",
        "site:{t} filetype:cfg",
        "site:{t} filetype:conf",
        "site:{t} filetype:ini",
        "site:{t} inurl:.git",
        "site:{t} inurl:.svn",
        "site:{t} \"DB_PASSWORD\"",
        "site:{t} \"api_key\"",
        "site:{t} \"secret_key\"",
        "site:{t} inurl:config filetype:php",
    ],
    "cams": [
        "inurl:/view/view.shtml site:{t}",
        "intitle:\"webcamXP\" site:{t}",
        "inurl:axis-cgi/mjpg site:{t}",
        "intitle:\"Live View\" site:{t}",
        "inurl:/cgi-bin/viewer/video.jpg site:{t}",
    ],
    "admin": [
        "site:{t} inurl:admin",
        "site:{t} inurl:dashboard",
        "site:{t} inurl:panel",
        "site:{t} inurl:controlpanel",
        "site:{t} intitle:\"Admin Panel\"",
        "site:{t} inurl:phpmyadmin",
        "site:{t} inurl:cpanel",
        "site:{t} inurl:webmin",
    ],
    "vuln": [
        "site:{t} inurl:php?id=",
        "site:{t} inurl:index.php?page=",
        "site:{t} inurl:product.php?id=",
        "site:{t} \"index of\" inurl:backup",
        "site:{t} \"index of\" inurl:upload",
        "site:{t} inurl:download.php?file=",
        "site:{t} inurl:open?url=",
        "site:{t} inurl:redirect?url=",
        "site:{t} ext:sql inurl:backup",
        "site:{t} intitle:\"Index of\" \".htpasswd\"",
    ],
}

SEARCH_URLS = {
    "google":     "https://www.google.com/search?q={q}",
    "bing":       "https://www.bing.com/search?q={q}",
    "duckduckgo": "https://duckduckgo.com/?q={q}",
}


def build_url(engine: str, dork: str) -> str:
    base = SEARCH_URLS[engine]
    return base.format(q=urllib.parse.quote_plus(dork))


def main():
    parser = argparse.ArgumentParser(
        description="Generate Google dork queries for a target domain. No HTTP requests made.",
        epilog="Use generated queries manually in a browser. Authorized use only.",
    )
    parser.add_argument("target", help="Target domain or keyword (e.g. example.com)")
    parser.add_argument(
        "--category", default="all",
        choices=list(DORK_TEMPLATES.keys()) + ["all"],
        help="Dork category (default: all)",
    )
    parser.add_argument(
        "--engine", default="google",
        choices=list(SEARCH_URLS.keys()),
        help="Search engine for URL generation (default: google)",
    )
    parser.add_argument("--count", type=int, metavar="N",
                        help="Limit output to N dorks")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    if args.category == "all":
        categories = list(DORK_TEMPLATES.keys())
    else:
        categories = [args.category]

    results = []
    for cat in categories:
        for template in DORK_TEMPLATES[cat]:
            dork = template.format(t=args.target)
            url = build_url(args.engine, dork)
            results.append({"category": cat, "dork": dork, "url": url})

    if args.count:
        results = results[: args.count]

    print(f"Target: {args.target} | Engine: {args.engine} | Dorks: {len(results)}\n")
    current_cat = None
    for r in results:
        if r["category"] != current_cat:
            current_cat = r["category"]
            print(f"--- {current_cat.upper()} ---")
        print(f"  {r['dork']}")
        print(f"  {r['url']}\n")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({"target": args.target, "dorks": results}, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
