#!/usr/bin/env python3
"""Compare two audit JSON files (before/after) and report fixes and regressions.

Project 05 Python exercise (solution). Works with Audit-Windows.ps1 output
(`ConvertTo-Json`) and with `linux_audit.py --json` output from Project 04.

    python3 compare_audits.py before.json after.json
"""
import argparse
import json
import sys


def load(path):
    # PowerShell writes UTF-8 with a BOM by default on Windows PowerShell 5.1: utf-8-sig handles it
    with open(path, encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if isinstance(data, dict):           # a single object if only one control was emitted
        data = [data]
    # Accept both key styles: Id/Result (PowerShell) and id/result (Python)
    return {(r.get("Id") or r.get("id")): r for r in data}


def result(row):
    return (row.get("Result") or row.get("result") or "?").upper()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()

    before, after = load(args.before), load(args.after)
    fixed, regressed, still_failing = [], [], []
    for cid in sorted(set(before) | set(after)):
        b = result(before.get(cid, {})) if cid in before else "MISSING"
        a = result(after.get(cid, {})) if cid in after else "MISSING"
        control = (after.get(cid) or before.get(cid) or {}).get("Control") or \
                  (after.get(cid) or before.get(cid) or {}).get("control", "")
        if b == "FAIL" and a == "PASS":
            fixed.append((cid, control))
        elif b == "PASS" and a == "FAIL":
            regressed.append((cid, control))
        elif a == "FAIL":
            still_failing.append((cid, control))

    def show(title, rows):
        print(f"{title} ({len(rows)}):")
        for cid, control in rows:
            print(f"  {cid:<8} {control}")
        print()

    show("Fixed", fixed)
    show("REGRESSED", regressed)
    show("Still failing", still_failing)
    passed = sum(result(r) == "PASS" for r in after.values())
    print(f"After: {passed}/{len(after)} passing")
    return 1 if regressed else 0


if __name__ == "__main__":
    sys.exit(main())
