# OSINT & Cybersecurity Tools

A collection of self-contained command-line tools for OSINT, network analysis, web security testing, and credential analysis. Each tool is independently runnable with no shared state.

**For authorized use only** — only run these tools on systems you own or have explicit written permission to test.

## Categories

| Category | Tools | Language |
|---|---|---|
| [OSINT / Recon](osint/) | username_search, dns_enum, email_header_analyzer | Python |
| [Network Analysis](network/) | port_scanner, subdomain_enum, ssl_inspector | Python |
| [Web Security](web/) | headers_analyzer, web_fuzzer, dork_generator | Python |
| [Credential Tools](credentials/) | hash_identifier, password_strength, wordlist_utils | Python, Bash |

## Requirements

- Python 3.9+
- Bash (for `wordlist_utils.sh`)

```bash
pip install requests dnspython cryptography
```

`cryptography` is optional — `ssl_inspector.py` degrades gracefully without it.

## Quick Start

```bash
git clone https://github.com/detectivesudo/Claudecode.git
cd Claudecode
pip install requests dnspython cryptography
```

## Usage Examples

```bash
# OSINT
python3 osint/dns_enum.py example.com --types A MX TXT
python3 osint/username_search.py johndoe
python3 osint/email_header_analyzer.py --file message.eml

# Network
python3 network/port_scanner.py scanme.nmap.org --ports 1-1024
python3 network/subdomain_enum.py example.com
python3 network/ssl_inspector.py example.com

# Web
python3 web/headers_analyzer.py https://example.com
python3 web/web_fuzzer.py https://example.com --wordlist wordlists/subdomains-small.txt
python3 web/dork_generator.py example.com --category login

# Credentials
python3 credentials/hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99
python3 credentials/password_strength.py "MyP@ssw0rd" --verbose
bash credentials/wordlist_utils.sh -i big.txt -d -s -l 8:16 -o filtered.txt
```

## Legal Disclaimer

These tools are provided for educational purposes and authorized security testing only. Unauthorized use against systems you do not own or have permission to test may violate local, state, and federal laws. The authors assume no liability for misuse.

## License

MIT
