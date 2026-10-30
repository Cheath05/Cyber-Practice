#!/usr/bin/env python3
"""Check that relative Markdown links in this repo point at files that exist.

Usage: python3 scripts/check_links.py   (exit code = number of broken links)
External http(s) links are not fetched; they're listed with --external.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def main():
    show_external = "--external" in sys.argv
    broken = 0
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        in_code = False
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            for target in LINK.findall(line):
                if target.startswith(("http://", "https://")):
                    if show_external:
                        print(f"EXT  {md.relative_to(ROOT)}:{lineno}  {target}")
                    continue
                if target.startswith(("mailto:", "#")):
                    continue
                path = target.split("#", 1)[0]
                if not path:
                    continue
                if not (md.parent / path).exists():
                    print(f"BROKEN  {md.relative_to(ROOT)}:{lineno}  {target}")
                    broken += 1
    print(f"{broken} broken relative link(s)")
    return broken


if __name__ == "__main__":
    sys.exit(min(main(), 255))
