# OSINT / Recon Tools

Tools for open-source intelligence gathering and passive reconnaissance.

## Tools

| Tool | Description | Requirements |
|---|---|---|
| `username_search.py` | Search for a username across 20+ platforms | `requests` |
| `dns_enum.py` | Enumerate DNS records (A, AAAA, MX, NS, TXT, SOA, CNAME) | `dnspython` |
| `email_header_analyzer.py` | Parse email relay chain and authentication headers | stdlib only |

Install dependencies:
```bash
pip install requests dnspython
```

## Usage

```bash
# Username search across platforms
python3 username_search.py johndoe
python3 username_search.py johndoe --threads 20 --output results.json

# DNS enumeration
python3 dns_enum.py example.com
python3 dns_enum.py example.com --types A MX TXT
python3 dns_enum.py example.com --resolver 8.8.8.8 --output dns.json

# Email header analysis
python3 email_header_analyzer.py --file suspicious.eml
cat email.eml | python3 email_header_analyzer.py --stdin
python3 email_header_analyzer.py --file email.eml --output analysis.json
```
