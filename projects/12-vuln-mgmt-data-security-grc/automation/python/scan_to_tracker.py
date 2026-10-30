#!/usr/bin/env python3
"""Turn scanner output into a remediation tracker (Project 12 Python exercise, solution).

    python3 scan_to_tracker.py --nuclei nuclei.jsonl --greenbone report.csv \
        --kev known_exploited_vulnerabilities.json --csv tracker.csv --db vulns.db

Inputs (any combination):
  --nuclei     Nuclei JSON Lines output (nuclei ... -jsonl -o nuclei.jsonl)
  --greenbone  Greenbone/OpenVAS CSV report export
  --kev        CISA KEV catalog JSON (download it from cisa.gov) to flag known-exploited CVEs
Outputs: a tracker CSV (one row per unique asset+finding) and an optional SQLite DB for SQL.
SLA days by severity: Critical 7, High 14, Medium 30, Low 90 (edit SLA_DAYS to match your policy).
"""
import argparse
import csv
import json
import sqlite3
from datetime import date, timedelta

SLA_DAYS = {"critical": 7, "high": 14, "medium": 30, "low": 90, "info": 0}


def severity_from_cvss(score):
    if score is None:
        return "info"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low" if score > 0 else "info"


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_nuclei(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            info = r.get("info", {})
            cls = info.get("classification") or {}
            cves = cls.get("cve-id") or []
            yield {
                "asset": r.get("host") or r.get("ip") or "?",
                "title": info.get("name") or r.get("template-id", "?"),
                "cve": ",".join(c.upper() for c in cves),
                "cvss": to_float(cls.get("cvss-score")),
                "severity": (info.get("severity") or "").lower(),
                "evidence": r.get("matched-at", ""),
                "source": "nuclei",
            }


def read_greenbone(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            port = r.get("Port", "")
            yield {
                "asset": r.get("IP", "?") + (f":{port}" if port and port != "general" else ""),
                "title": r.get("NVT Name", "?"),
                "cve": (r.get("CVEs") or "").replace(" ", ""),
                "cvss": to_float(r.get("CVSS")),
                "severity": (r.get("Severity") or "").lower(),
                "evidence": r.get("Specific Result", "")[:200],
                "source": "greenbone",
            }


def load_kev(path):
    if not path:
        return set()
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {v["cveID"].upper() for v in data.get("vulnerabilities", [])}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nuclei")
    parser.add_argument("--greenbone")
    parser.add_argument("--kev")
    parser.add_argument("--csv", default="tracker.csv")
    parser.add_argument("--db", help="also write a SQLite database for the SQL exercise")
    parser.add_argument("--found", default=date.today().isoformat(), help="scan date (YYYY-MM-DD)")
    args = parser.parse_args()
    if not (args.nuclei or args.greenbone):
        parser.error("give --nuclei and/or --greenbone")

    kev = load_kev(args.kev)
    found = date.fromisoformat(args.found)
    findings = {}
    sources = []
    if args.nuclei:
        sources.append(read_nuclei(args.nuclei))
    if args.greenbone:
        sources.append(read_greenbone(args.greenbone))
    for source in sources:
        for f in source:
            if f["severity"] not in SLA_DAYS:
                f["severity"] = severity_from_cvss(f["cvss"])
            key = (f["asset"], f["title"])            # de-duplicate across scanners/re-scans
            if key in findings:
                continue
            in_kev = any(c in kev for c in f["cve"].split(",") if c)
            sev = "critical" if in_kev and f["severity"] in ("high", "medium") else f["severity"]
            f.update({
                "kev": "yes" if in_kev else "",
                "priority_severity": sev,
                "found": found.isoformat(),
                "due": (found + timedelta(days=SLA_DAYS[sev])).isoformat() if SLA_DAYS[sev] else "",
                "status": "Open",
            })
            findings[key] = f

    rows = sorted(findings.values(), key=lambda f: (list(SLA_DAYS).index(f["priority_severity"]), f["asset"]))
    for i, r in enumerate(rows, 1):
        r["id"] = f"V-{i:03d}"
    fields = ["id", "asset", "title", "cve", "cvss", "severity", "kev", "priority_severity",
              "found", "due", "status", "source", "evidence"]
    with open(args.csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: r.get(k, "") for k in fields} for r in rows)

    if args.db:
        con = sqlite3.connect(args.db)
        con.execute("DROP TABLE IF EXISTS vulns")
        con.execute("""CREATE TABLE vulns (id TEXT PRIMARY KEY, asset TEXT, title TEXT, cve TEXT,
                       cvss REAL, severity TEXT, kev TEXT, priority_severity TEXT, found TEXT,
                       due TEXT, status TEXT, fixed TEXT, source TEXT, evidence TEXT)""")
        con.executemany(
            "INSERT INTO vulns VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",   # parameterized, never f-strings
            [(r["id"], r["asset"], r["title"], r["cve"], r["cvss"], r["severity"], r["kev"],
              r["priority_severity"], r["found"], r["due"], r["status"], None, r["source"], r["evidence"])
             for r in rows])
        con.commit()
        con.close()

    counts = {}
    for r in rows:
        counts[r["priority_severity"]] = counts.get(r["priority_severity"], 0) + 1
    print(f"{len(rows)} unique findings -> {args.csv}" + (f" and {args.db}" if args.db else ""))
    for sev in SLA_DAYS:
        if sev in counts:
            print(f"  {sev:<9} {counts[sev]}")
    if kev:
        print(f"  in CISA KEV: {sum(1 for r in rows if r['kev'])}")


if __name__ == "__main__":
    main()
