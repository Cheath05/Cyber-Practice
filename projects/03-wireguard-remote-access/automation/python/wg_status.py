#!/usr/bin/env python3
"""Report WireGuard peer health from `wg show all dump` (Project 03 Python exercise, solution).

On OPNsense:  wg show all dump > dump.txt   (then copy it over), or pipe it in:
    ssh root@10.10.10.1 'wg show all dump' | python3 wg_status.py --peers peers.csv

Dump format (tab-separated): the first line per interface describes the interface itself
(5 fields after the interface name); each peer line has 8 fields after the interface name:
public-key, preshared-key, endpoint, allowed-ips, latest-handshake (unix ts, 0 = never),
transfer-rx, transfer-tx, persistent-keepalive.
"""
import argparse
import csv
import sys
import time

STALE_SECONDS = 180          # no handshake in 3 min = not currently connected
REVOKE_DAYS = 30             # no handshake in 30 days = revocation candidate


def human_bytes(n):
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TiB"


def human_age(seconds):
    if seconds is None:
        return "never"
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if seconds >= size:
            return f"{seconds // size}{unit} ago"
    return f"{seconds}s ago"


def load_register(path):
    if not path:
        return {}
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["public_key"]: row for row in csv.DictReader(fh)}


def parse_dump(lines):
    peers = []
    for line in lines:
        fields = line.rstrip("\n").split("\t")
        if len(fields) == 9:  # interface name + 8 peer fields
            iface, pub, _psk, endpoint, allowed, hs, rx, tx, _ka = fields
            peers.append({
                "iface": iface, "public_key": pub, "endpoint": endpoint,
                "allowed_ips": allowed, "handshake": int(hs), "rx": int(rx), "tx": int(tx),
            })
    return peers


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dump", nargs="?", help="file with `wg show all dump` output (default: stdin)")
    parser.add_argument("--peers", help="CSV peer register (public_key,name,tunnel_ip,added,expires)")
    args = parser.parse_args()

    lines = open(args.dump, encoding="utf-8") if args.dump else sys.stdin
    peers = parse_dump(lines)
    register = load_register(args.peers)
    now = int(time.time())

    print(f"{'NAME':<16} {'TUNNEL IP':<16} {'LAST HANDSHAKE':<15} {'RX':>10} {'TX':>10}  STATUS")
    for p in sorted(peers, key=lambda p: p["allowed_ips"]):
        info = register.get(p["public_key"], {})
        name = info.get("name", p["public_key"][:10] + "…")
        age = now - p["handshake"] if p["handshake"] else None
        if age is None or age > REVOKE_DAYS * 86400:
            status = "REVOCATION CANDIDATE"
        elif age > STALE_SECONDS:
            status = "idle"
        else:
            status = "connected"
        expires = info.get("expires", "")
        if expires and expires != "never" and expires < time.strftime("%Y-%m-%d"):
            status += " | EXPIRED per register"
        print(f"{name:<16} {p['allowed_ips']:<16} {human_age(age):<15} "
              f"{human_bytes(p['rx']):>10} {human_bytes(p['tx']):>10}  {status}")
    unknown = [p for p in peers if p["public_key"] not in register]
    if register and unknown:
        print(f"\nWARNING: {len(unknown)} peer(s) on the server are missing from the register.")


if __name__ == "__main__":
    main()
