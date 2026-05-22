# CLAUDE.md

This file provides guidance to AI assistants working in this repository.

## Project Overview

**OSINT & Cybersecurity Tools** is a multi-language collection of self-contained CLI tools for open-source intelligence gathering, network analysis, web security testing, and credential analysis.

## Repository State (as of 2026-05-13)

- **Languages**: Python 3.9+, Bash
- **Dependencies**: `requests`, `dnspython`, `cryptography` (optional)
- **Tests**: None — each tool is runnable standalone
- **CI/CD**: None configured
- **Main branch**: `main`

## Project Structure

```
osint/           # OSINT and recon tools
network/         # Network analysis tools
web/             # Web security tools
credentials/     # Credential and wordlist tools
wordlists/       # Bundled wordlists
```

## Setup

```bash
pip install requests dnspython cryptography
```

`cryptography` is optional; `ssl_inspector.py` degrades gracefully without it.

## Running Tools

Every Python tool supports `--help`:

```bash
python3 osint/dns_enum.py --help
python3 network/port_scanner.py scanme.nmap.org --ports 22,80,443
python3 web/headers_analyzer.py https://example.com
python3 credentials/hash_identifier.py 5f4dcc3b5aa765d61d8327deb882cf99
bash credentials/wordlist_utils.sh -h
```

## Code Style

- **Python**: PEP 8, 4-space indentation, `argparse` for all CLIs, type hints encouraged
- **Bash**: `set -euo pipefail`, `getopts` for flags, `LC_ALL=C` for sort/awk/uniq
- No comments unless the WHY is non-obvious
- No docstrings on simple functions

## Git Workflow

### Branch Naming

```
claude/<short-description>-<session-id>
```

### Commit Style

Imperative mood, present tense:
```
Add DNS enumeration tool
Fix subdomain wildcard detection
Update README with ssl_inspector examples
```

### Push Commands

```bash
git push -u origin <branch-name>
```

Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s) on network failure.

### Pull Requests

Target `main`. Include a summary and test plan in the PR body.

## Development Guidelines

1. **Read before modifying** — always read a file fully before editing.
2. **Minimal changes** — only change what is directly requested.
3. **No speculation** — do not add features for hypothetical future use.
4. **Security-first** — tools operate outbound only; no server mode; no credentials stored on disk.
5. **No backwards-compatibility hacks** — remove dead code fully.

## Reversibility & Blast Radius

- **Local, reversible actions** (editing files, running tools against test targets) — proceed freely.
- **Destructive or hard-to-reverse actions** — confirm with the user first.
- **Actions visible to others** (pushing, opening PRs) — confirm unless pre-authorized.
