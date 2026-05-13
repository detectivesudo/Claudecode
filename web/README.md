# Web Security Tools

Tools for HTTP security analysis, directory enumeration, and dork generation.

**Authorized use only** — only target systems you own or have written permission to test.

## Tools

| Tool | Description | Requirements |
|---|---|---|
| `headers_analyzer.py` | Check HTTP security headers (HSTS, CSP, X-Frame-Options, etc.) | `requests` |
| `web_fuzzer.py` | Directory and path enumeration | `requests` |
| `dork_generator.py` | Generate Google dork queries (no HTTP calls made) | stdlib only |

Install dependencies:
```bash
pip install requests
```

## Usage

```bash
# Security headers check
python3 headers_analyzer.py https://example.com
python3 headers_analyzer.py https://example.com --method GET --follow-redirects
python3 headers_analyzer.py https://example.com --output headers.json

# Directory fuzzing
python3 web_fuzzer.py https://example.com --wordlist ../wordlists/subdomains-small.txt
python3 web_fuzzer.py https://example.com --wordlist wordlist.txt --extensions php,html,txt
python3 web_fuzzer.py https://example.com --wordlist wordlist.txt --threads 20 --delay 100

# Dork generator (no network activity)
python3 dork_generator.py example.com
python3 dork_generator.py example.com --category login
python3 dork_generator.py example.com --category config --engine duckduckgo
python3 dork_generator.py example.com --category all --output dorks.json
```
