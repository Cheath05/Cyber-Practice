#!/usr/bin/env python3
"""Concurrent service-uptime checker / mini scoring engine (Project 10 Python exercise, solution).

    python3 service_check.py targets.txt --csv scores.csv
targets.txt lines:   <team> <host> <kind> [port] [expect]
  kind: tcp | http | ssh       expect (http only): substring the page must contain
  e.g.  Blue1 10.10.30.51 ssh
        Blue1 10.10.30.51 http 80 Homelab Widgets
Run it from cron every minute during a game to build an uptime history. Only check hosts that
are in your exercise scope.
"""
import argparse
import csv
import os
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

DEFAULT_PORTS = {"tcp": 80, "http": 80, "ssh": 22}


def check(target, timeout):
    team, host, kind, port, expect = target
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            if kind == "ssh":
                banner = s.recv(64).decode(errors="replace")
                return banner.startswith("SSH-"), banner.strip()[:40]
            if kind == "http":
                s.sendall(f"GET / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
                data = b""
                while len(data) < 65536:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                text = data.decode(errors="replace")
                ok = " 200 " in text.split("\r\n", 1)[0] and (not expect or expect in text)
                return ok, text.split("\r\n", 1)[0][:40]
            return True, "open"
    except OSError as exc:
        return False, type(exc).__name__


def parse_targets(path):
    targets = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=4)
            team, host, kind = parts[0], parts[1], parts[2].lower()
            port = int(parts[3]) if len(parts) > 3 else DEFAULT_PORTS[kind]
            expect = parts[4] if len(parts) > 4 else ""
            targets.append((team, host, kind, port, expect))
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets")
    parser.add_argument("--csv", help="append results to this CSV")
    parser.add_argument("--timeout", type=float, default=3)
    args = parser.parse_args()

    targets = parse_targets(args.targets)
    with ThreadPoolExecutor(max_workers=min(32, len(targets) or 1)) as pool:
        results = list(pool.map(lambda t: check(t, args.timeout), targets))

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    score = {}
    print(f"Round at {now}")
    for (team, host, kind, port, _), (ok, detail) in zip(targets, results):
        score.setdefault(team, [0, 0])
        score[team][1] += 1
        score[team][0] += ok
        print(f"  {'UP  ' if ok else 'DOWN'}  {team:<8} {host}:{port:<5} {kind:<4} {detail}")
    print("Scoreboard (services up this round):")
    for team, (up, total) in sorted(score.items()):
        print(f"  {team:<8} {up}/{total}")

    if args.csv:
        new = not os.path.exists(args.csv)
        with open(args.csv, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["time", "team", "host", "port", "kind", "up", "detail"])
            for (team, host, kind, port, _), (ok, detail) in zip(targets, results):
                w.writerow([now, team, host, port, kind, int(ok), detail])


if __name__ == "__main__":
    main()
