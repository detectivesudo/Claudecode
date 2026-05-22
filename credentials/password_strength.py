#!/usr/bin/env python3
import argparse
import json
import math
import re
import sys

COMMON_PASSWORDS = frozenset([
    "password", "123456", "password1", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon", "baseball",
    "iloveyou", "master", "sunshine", "ashley", "bailey", "passw0rd",
    "shadow", "123123", "654321", "superman", "qazwsx", "michael",
    "football", "password123", "ninja", "mustang", "access", "welcome",
    "login", "admin", "princess", "solo", "starwars", "hello", "charlie",
    "donald", "password2", "qwerty123", "000000", "111111", "1234567890",
    "pass", "temp", "test", "guest", "root", "toor", "changeme",
])

KEYBOARD_WALKS = [
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "qwerty", "asdfgh", "zxcvbn", "qazwsx", "edcrfv",
    "1234567890", "0987654321", "12345", "09876",
]

TIERS = [
    (0,  20,  "Very Weak"),
    (20, 40,  "Weak"),
    (40, 60,  "Fair"),
    (60, 80,  "Strong"),
    (80, 101, "Very Strong"),
]

GUESSES_PER_SEC = 1e10  # offline fast hash (e.g. MD5)


def crack_time_str(entropy: float) -> str:
    seconds = (2 ** entropy) / GUESSES_PER_SEC
    if seconds < 1:
        return "instant"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    if seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    if seconds < 31536000:
        return f"{seconds/86400:.1f} days"
    if seconds < 3.156e9:
        return f"{seconds/31536000:.1f} years"
    return "centuries"


def analyze(password: str, verbose: bool) -> dict:
    details = []
    score = 0

    # Charset size
    charset = 0
    if re.search(r"[a-z]", password):
        charset += 26
    if re.search(r"[A-Z]", password):
        charset += 26
    if re.search(r"[0-9]", password):
        charset += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        charset += 32
    # crude unicode bump
    if any(ord(c) > 127 for c in password):
        charset += 64

    length = len(password)
    entropy = math.log2(max(charset, 1) ** max(length, 1))

    # Base score from entropy (0–70 points)
    base = min(70, entropy * 1.4)
    score += base
    details.append(f"Entropy {entropy:.1f} bits → +{base:.0f} pts")

    # Length bonus
    if length >= 20:
        score += 10
        details.append("Length ≥ 20 → +10 pts")
    elif length >= 16:
        score += 7
        details.append("Length ≥ 16 → +7 pts")

    lower = password.lower()

    # Penalties
    if lower in COMMON_PASSWORDS:
        score -= 60
        details.append("Common password → -60 pts")

    if re.search(r"(.)\1{2,}", password):
        score -= 10
        details.append("Repeating characters → -10 pts")
    for walk in KEYBOARD_WALKS:
        for window in range(4, len(walk) + 1):
            chunk = walk[:window]
            if chunk in lower or chunk[::-1] in lower:
                score -= 15
                details.append(f"Keyboard walk '{chunk}' → -15 pts")
                break

    if password.isdigit():
        score -= 10
        details.append("Digits only → -10 pts")
    elif password.isalpha() and length <= 12:
        score -= 5
        details.append("Letters only, short → -5 pts")

    score = max(0, min(100, score))

    tier = "Very Weak"
    for lo, hi, label in TIERS:
        if lo <= score < hi:
            tier = label
            break

    return {
        "score": round(score),
        "tier": tier,
        "entropy_bits": round(entropy, 1),
        "charset_size": charset,
        "length": length,
        "crack_time": crack_time_str(entropy),
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze password strength and estimate crack time.")
    parser.add_argument("password", nargs="?", help="Password to analyze")
    parser.add_argument("--stdin", action="store_true", help="Read password from stdin (avoids shell history)")
    parser.add_argument("--verbose", action="store_true", help="Show scoring breakdown")
    parser.add_argument("--min-score", type=int, metavar="N", help="Exit with code 1 if score < N")
    parser.add_argument("--output", metavar="FILE", help="Write result as JSON to FILE")
    args = parser.parse_args()

    if args.stdin:
        password = sys.stdin.readline().rstrip("\n")
    elif args.password:
        password = args.password
    else:
        parser.error("Provide a password argument or use --stdin.")

    result = analyze(password, args.verbose)

    print(f"Score:      {result['score']}/100  ({result['tier']})")
    print(f"Length:     {result['length']}")
    print(f"Charset:    {result['charset_size']} symbols")
    print(f"Entropy:    {result['entropy_bits']} bits")
    print(f"Crack time: {result['crack_time']} (offline fast hash, 10B guesses/sec)")

    if args.verbose:
        print("\nScoring breakdown:")
        for line in result["details"]:
            print(f"  {line}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")

    if args.min_score is not None and result["score"] < args.min_score:
        sys.exit(1)


if __name__ == "__main__":
    main()
