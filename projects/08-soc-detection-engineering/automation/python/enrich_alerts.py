#!/usr/bin/env python3
"""Summarize Wazuh alerts.json (Project 08 Python exercise, solution).

Wazuh writes one JSON alert per line to /var/ossec/logs/alerts/alerts.json. Copy it (or a
rotated .json.gz day file) off the manager and run:

    python3 enrich_alerts.py alerts.json
    python3 enrich_alerts.py alerts.json --min-level 10 --since 2026-11-20T00:00 --csv high.csv

Prints alerts per level, top rules, top agents, alerts per MITRE technique, and the alerts at or
above --min-level (optionally to CSV for your SOC tickets). Standard library only.
"""
import argparse
import csv
import gzip
import json
from collections import Counter
from datetime import datetime, timezone


def parse_ts(value):
    # Wazuh timestamps look like 2026-11-20T14:02:11.123+0000
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(value, fmt)
        except (TypeError, ValueError):
            continue
    return None


def read_alerts(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"skipping malformed line {lineno}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("alerts", help="alerts.json (JSON lines), optionally .gz")
    parser.add_argument("--min-level", type=int, default=10)
    parser.add_argument("--since", help="ISO time, e.g. 2026-11-20T00:00 (UTC if no offset)")
    parser.add_argument("--csv", help="write alerts >= min-level to this CSV")
    args = parser.parse_args()

    since = None
    if args.since:
        since = datetime.fromisoformat(args.since)
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)

    levels, rules, agents, techniques = Counter(), Counter(), Counter(), Counter()
    high = []
    total = 0
    for alert in read_alerts(args.alerts):
        ts = parse_ts(alert.get("timestamp"))
        if since and ts and ts < since:
            continue
        total += 1
        rule = alert.get("rule", {})
        level = int(rule.get("level", 0))
        levels[level] += 1
        rules[(rule.get("id", "?"), rule.get("description", ""))] += 1
        agents[alert.get("agent", {}).get("name", "?")] += 1
        mitre = rule.get("mitre", {})
        for tid, name in zip(mitre.get("id", []), mitre.get("technique", []) or [""] * len(mitre.get("id", []))):
            techniques[f"{tid} {name}".strip()] += 1
        if level >= args.min_level:
            high.append({
                "timestamp": alert.get("timestamp", ""),
                "level": level,
                "rule_id": rule.get("id", ""),
                "description": rule.get("description", ""),
                "agent": alert.get("agent", {}).get("name", ""),
                "srcip": alert.get("data", {}).get("srcip", ""),
                "mitre": ",".join(mitre.get("id", [])),
            })

    print(f"Alerts analysed: {total}\n")
    print("By level:")
    for level in sorted(levels, reverse=True):
        print(f"  {level:>2}  {levels[level]}")
    print("\nTop rules:")
    for (rid, desc), n in rules.most_common(10):
        print(f"  {n:>5}  {rid:>6}  {desc}")
    print("\nTop agents:")
    for name, n in agents.most_common(10):
        print(f"  {n:>5}  {name}")
    print("\nMITRE ATT&CK techniques:")
    for tech, n in techniques.most_common(15):
        print(f"  {n:>5}  {tech}")
    print(f"\nAlerts with level >= {args.min_level}: {len(high)}")
    for a in high[:20]:
        print(f"  {a['timestamp']}  L{a['level']}  {a['rule_id']}  {a['agent']}  {a['description']}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(high[0].keys()) if high else ["timestamp"])
            writer.writeheader()
            writer.writerows(high)
        print(f"\nWrote {len(high)} rows to {args.csv}")


if __name__ == "__main__":
    main()
