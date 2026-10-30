#!/usr/bin/env python3
"""Lint AWS IAM policy documents for risky patterns (Project 14 Python exercise, solution).

    python3 iam_lint.py ../samples/policies/*.json
    python3 iam_lint.py policy.json --json

Checks (Allow statements only, since explicit Deny is fine to be broad):
  - Action "*" or "service:*"                      (over-broad actions)
  - Resource "*" combined with write/admin actions  (no resource scoping)
  - NotAction / NotResource with Allow               (allows everything except...)
  - Principal "*" without a Condition                (public access, resource policies)
  - iam:PassRole on Resource "*"                     (privilege escalation path)
Exit code is 1 if any High finding exists, so it can gate CI.
"""
import argparse
import json
import sys

WRITE_HINTS = ("put", "create", "delete", "update", "attach", "detach", "pass", "set", "add", "remove", "*")


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def lint_statement(stmt, idx):
    out = []
    if stmt.get("Effect") != "Allow":
        return out
    sid = stmt.get("Sid") or f"Statement[{idx}]"
    actions = [a.lower() for a in as_list(stmt.get("Action"))]
    resources = as_list(stmt.get("Resource"))
    if "*" in actions:
        out.append(("High", sid, 'Action "*" allows every API call'))
    for a in actions:
        if a.endswith(":*") and a != "*":
            out.append(("Medium", sid, f'Service wildcard "{a}"'))
    if "*" in resources and any(a == "*" or a.split(":")[-1].startswith(WRITE_HINTS) for a in actions):
        out.append(("High", sid, 'Write/admin actions on Resource "*" (no resource scoping)'))
    if "NotAction" in stmt:
        out.append(("High", sid, "Allow with NotAction grants everything except the listed actions"))
    if "NotResource" in stmt:
        out.append(("Medium", sid, "Allow with NotResource applies to every other resource"))
    principal = stmt.get("Principal")
    is_public = principal == "*" or (isinstance(principal, dict) and "*" in as_list(principal.get("AWS")))
    if is_public and not stmt.get("Condition"):
        out.append(("High", sid, 'Public Principal "*" with no Condition'))
    if "iam:passrole" in actions and "*" in resources:
        out.append(("High", sid, 'iam:PassRole on Resource "*" enables privilege escalation'))
    return out


def lint_file(path):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    findings = []
    for i, stmt in enumerate(as_list(doc.get("Statement"))):
        findings.extend(lint_statement(stmt, i))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("policies", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results, worst_high = {}, False
    for path in args.policies:
        try:
            findings = lint_file(path)
        except (OSError, json.JSONDecodeError) as exc:
            findings = [("Error", "-", str(exc))]
        results[path] = findings
        worst_high |= any(f[0] == "High" for f in findings)

    if args.json:
        print(json.dumps({p: [dict(zip(("severity", "statement", "issue"), f)) for f in fs]
                          for p, fs in results.items()}, indent=2))
    else:
        for path, findings in results.items():
            print(f"{path}: {'OK' if not findings else str(len(findings)) + ' finding(s)'}")
            for sev, sid, issue in findings:
                print(f"  [{sev:<6}] {sid}: {issue}")
    return 1 if worst_high else 0


if __name__ == "__main__":
    sys.exit(main())
