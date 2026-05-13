#!/usr/bin/env python3
import argparse
import json
import re
import sys

HASH_SIGNATURES = [
    ("Argon2",       r"^\$argon2(i|d|id)\$", None),
    ("bcrypt",       r"^\$2[ab]?\$\d{2}\$.{53}$", None),
    ("scrypt",       r"^\$scrypt\$", None),
    ("PBKDF2-SHA256",r"^\$pbkdf2-sha256\$", None),
    ("PBKDF2-SHA512",r"^\$pbkdf2-sha512\$", None),
    ("Kerberos 5 TGT",r"^\$krb5tgs\$", None),
    ("Kerberos 5 AS-REP",r"^\$krb5asrep\$", None),
    ("WordPress (phpass)",r"^\$P\$", None),
    ("Cisco IOS (type 5)",r"^\$1\$", None),
    ("SHA-512 crypt",r"^\$6\$", None),
    ("SHA-256 crypt",r"^\$5\$", None),
    ("MD5 crypt",    r"^\$1\$", None),
    ("MySQL 4.1+",   r"^\*[0-9A-F]{40}$", 41),
    ("LM Hash",      r"^[0-9A-F]{32}$", 32),
    ("NTLM",         r"^[0-9a-fA-F]{32}$", 32),
    ("MD5",          r"^[0-9a-f]{32}$", 32),
    ("MD5 (upper)",  r"^[0-9A-F]{32}$", 32),
    ("MySQL 3.x",    r"^[0-9a-f]{16}$", 16),
    ("SHA-1",        r"^[0-9a-f]{40}$", 40),
    ("SHA-1 (upper)",r"^[0-9A-F]{40}$", 40),
    ("SHA-224",      r"^[0-9a-f]{56}$", 56),
    ("SHA-256",      r"^[0-9a-f]{64}$", 64),
    ("SHA-256 (upper)",r"^[0-9A-F]{64}$", 64),
    ("SHA3-256 / Keccak-256", r"^[0-9a-f]{64}$", 64),
    ("SHA-384",      r"^[0-9a-f]{96}$", 96),
    ("SHA-512",      r"^[0-9a-f]{128}$", 128),
    ("SHA-512 (upper)",r"^[0-9A-F]{128}$", 128),
    ("Base64-SHA1",  r"^[A-Za-z0-9+/]{27}=$", 28),
    ("CRC32",        r"^[0-9a-f]{8}$", 8),
    ("RIPEMD-160",   r"^[0-9a-f]{40}$", 40),
    ("Whirlpool",    r"^[0-9a-f]{128}$", 128),
    ("GOST R 34.11-94", r"^[0-9a-f]{64}$", 64),
]

PREFIX_PRIORITY = {
    "Argon2", "bcrypt", "scrypt", "PBKDF2-SHA256", "PBKDF2-SHA512",
    "Kerberos 5 TGT", "Kerberos 5 AS-REP", "WordPress (phpass)",
    "Cisco IOS (type 5)", "SHA-512 crypt", "SHA-256 crypt", "MySQL 4.1+",
}


def identify(hash_val: str, show_all: bool) -> list[dict]:
    h = hash_val.strip()
    results = []
    for name, pattern, length in HASH_SIGNATURES:
        if length is not None and len(h) != length:
            continue
        if re.match(pattern, h):
            priority = 0 if name in PREFIX_PRIORITY else 1
            results.append({"name": name, "priority": priority})
    results.sort(key=lambda x: x["priority"])
    if not show_all and results:
        top = results[0]["priority"]
        results = [r for r in results if r["priority"] == top]
    return results


def main():
    parser = argparse.ArgumentParser(description="Identify hash type by pattern matching.")
    parser.add_argument("hash", nargs="?", help="Hash string to identify (use '-' to read from stdin)")
    parser.add_argument("--all", action="store_true", help="Show all possible matches, not just most confident")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    if args.hash is None or args.hash == "-":
        hash_val = sys.stdin.read().strip()
    else:
        hash_val = args.hash

    if not hash_val:
        parser.error("Provide a hash string or pipe one via stdin.")

    matches = identify(hash_val, args.all)

    if not matches:
        print(f"[?] No matches found for: {hash_val}")
        sys.exit(1)

    print(f"Hash: {hash_val}\n")
    for m in matches:
        confidence = "High" if m["priority"] == 0 else "Possible"
        print(f"  [{confidence}] {m['name']}")

    if args.output:
        data = {"hash": hash_val, "matches": [m["name"] for m in matches]}
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
