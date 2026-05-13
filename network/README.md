# Network Analysis Tools

Tools for network scanning, subdomain enumeration, and SSL/TLS inspection.

## Tools

| Tool | Description | Requirements |
|---|---|---|
| `port_scanner.py` | TCP connect port scanner with optional banner grabbing | stdlib only |
| `subdomain_enum.py` | Subdomain brute-force via DNS with wildcard detection | `dnspython` |
| `ssl_inspector.py` | TLS certificate details, expiry check, cipher info | stdlib + optional `cryptography` |

Install dependencies:
```bash
pip install dnspython cryptography
```

`cryptography` is optional — `ssl_inspector.py` works without it but shows fewer fields.

## Usage

```bash
# Port scanner
python3 port_scanner.py scanme.nmap.org --ports 1-1024
python3 port_scanner.py 192.168.1.1 --ports 22,80,443,8080 --banner
python3 port_scanner.py target.com --ports 1-65535 --threads 200 --output ports.json

# Subdomain enumeration
python3 subdomain_enum.py example.com
python3 subdomain_enum.py example.com --wordlist /path/to/big-wordlist.txt --threads 50
python3 subdomain_enum.py example.com --wildcard-check --output subdomains.json

# SSL inspector
python3 ssl_inspector.py example.com
python3 ssl_inspector.py mail.example.com --port 993
python3 ssl_inspector.py example.com --expiry-days 60 --output cert.json
```
