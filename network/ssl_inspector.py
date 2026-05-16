#!/usr/bin/env python3
import argparse
import datetime
import json
import socket
import ssl
import sys

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


def get_cert_info(host: str, port: int, timeout: float) -> dict:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as raw_sock:
        with ctx.wrap_socket(raw_sock, server_hostname=host) as tls_sock:
            der_cert = tls_sock.getpeercert(binary_form=True)
            dict_cert = tls_sock.getpeercert()
            tls_version = tls_sock.version()
            cipher = tls_sock.cipher()

    info: dict = {
        "host": host,
        "port": port,
        "tls_version": tls_version,
        "cipher_suite": cipher[0] if cipher else None,
        "key_bits": None,
        "subject_cn": None,
        "sans": [],
        "issuer": None,
        "not_before": None,
        "not_after": None,
        "serial_number": None,
        "signature_algorithm": None,
        "days_until_expiry": None,
        "expired": False,
    }

    subject = dict(x[0] for x in dict_cert.get("subject", []))
    info["subject_cn"] = subject.get("commonName", "")
    issuer = dict(x[0] for x in dict_cert.get("issuer", []))
    info["issuer"] = issuer.get("organizationName") or issuer.get("commonName", "")

    not_after_str = dict_cert.get("notAfter", "")
    not_before_str = dict_cert.get("notBefore", "")
    info["not_before"] = not_before_str
    info["not_after"] = not_after_str

    sans = []
    for san_type, san_val in dict_cert.get("subjectAltName", []):
        if san_type == "DNS":
            sans.append(san_val)
    info["sans"] = sans

    if not_after_str:
        try:
            not_after = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
            not_after = not_after.replace(tzinfo=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            delta = (not_after - now).days
            info["days_until_expiry"] = delta
            info["expired"] = delta < 0
        except ValueError:
            pass

    if HAS_CRYPTOGRAPHY and der_cert:
        try:
            cert = x509.load_der_x509_certificate(der_cert, default_backend())
            info["serial_number"] = str(cert.serial_number)
            info["signature_algorithm"] = cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else None
            try:
                pk = cert.public_key()
                info["key_bits"] = pk.key_size
            except AttributeError:
                pass
        except Exception:
            pass

    return info


def main():
    parser = argparse.ArgumentParser(description="Inspect TLS/SSL certificate details for a host.")
    parser.add_argument("host", help="Target hostname")
    parser.add_argument("--port", type=int, default=443, help="Target port (default: 443)")
    parser.add_argument("--timeout", type=float, default=5.0, metavar="SECS",
                        help="Connection timeout (default: 5)")
    parser.add_argument("--expiry-days", type=int, default=30, metavar="N",
                        help="Warn if cert expires within N days (default: 30)")
    parser.add_argument("--output", metavar="FILE", help="Write results as JSON to FILE")
    args = parser.parse_args()

    if not HAS_CRYPTOGRAPHY:
        print("[!] cryptography package not installed — key size and signature algorithm unavailable.")
        print("    Run: pip install cryptography\n")

    try:
        info = get_cert_info(args.host, args.port, args.timeout)
    except ssl.SSLError as e:
        sys.exit(f"SSL error: {e}")
    except socket.gaierror as e:
        sys.exit(f"DNS resolution failed: {e}")
    except ConnectionRefusedError:
        sys.exit(f"Connection refused to {args.host}:{args.port}")
    except Exception as e:
        sys.exit(f"Error: {e}")

    print(f"Host:        {info['host']}:{info['port']}")
    print(f"TLS version: {info['tls_version']}")
    print(f"Cipher:      {info['cipher_suite']}")
    print(f"Subject CN:  {info['subject_cn']}")
    print(f"SANs:        {', '.join(info['sans']) or '(none)'}")
    print(f"Issuer:      {info['issuer']}")
    if info.get("key_bits"):
        print(f"Key size:    {info['key_bits']} bits")
    if info.get("signature_algorithm"):
        print(f"Signature:   {info['signature_algorithm']}")
    print(f"Valid from:  {info['not_before']}")
    print(f"Valid until: {info['not_after']}")

    days = info.get("days_until_expiry")
    if days is not None:
        if info["expired"]:
            print(f"\n[!] CERTIFICATE EXPIRED ({abs(days)} days ago)")
        elif days <= args.expiry_days:
            print(f"\n[!] Certificate expires in {days} days (threshold: {args.expiry_days})")
        else:
            print(f"\n[OK] Certificate valid for {days} more days")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(info, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
