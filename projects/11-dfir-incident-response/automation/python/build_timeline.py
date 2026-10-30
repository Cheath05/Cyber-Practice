#!/usr/bin/env python3
"""Build a mini super-timeline from a mounted Linux image (Project 11 Python exercise, solution).

    sudo mount -o ro,loop,noexec victim.raw /mnt/victim     (or a partition offset)
    python3 build_timeline.py /mnt/victim --year 2026 --csv timeline.csv

Sources:
  - file mtime/ctime for files under --dirs (default: etc, root, home, tmp, var/tmp)
  - var/log/auth.log lines (syslog timestamps have no year: pass --year)
  - home/*/.bash_history and root/.bash_history '#<epoch>' entries
Output: one CSV sorted by time with columns time_utc, source, artifact, detail.
Read-only: never writes to the image.
"""
import argparse
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path

SYSLOG_RE = re.compile(r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s\d\d:\d\d:\d\d)\s+(?P<host>\S+)\s+(?P<msg>.*)$")
ISO_RE = re.compile(r"^(?P<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:[+-]\d\d:?\d\d|Z)?)\s+(?P<host>\S+)\s+(?P<msg>.*)$")


def utc(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")


def file_events(root, dirs):
    for d in dirs:
        base = root / d
        if not base.exists():
            continue
        for dirpath, _dirnames, filenames in os.walk(base, onerror=lambda e: None):
            for name in filenames:
                p = Path(dirpath) / name
                try:
                    st = p.lstat()
                except OSError:
                    continue
                rel = "/" + str(p.relative_to(root))
                yield utc(st.st_mtime), "file-mtime", rel, f"size={st.st_size}"
                # ctime can't be set from user space; ctime >> mtime hints at timestomping
                if st.st_ctime - st.st_mtime > 86400:
                    yield utc(st.st_ctime), "file-ctime", rel, "ctime much newer than mtime (possible timestomp)"


def auth_events(root, year):
    for name in ("var/log/auth.log", "var/log/secure"):
        path = root / name
        if not path.exists():
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                m = ISO_RE.match(line)
                if m:
                    ts = datetime.fromisoformat(m["ts"].replace("Z", "+00:00"))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    yield ts.astimezone(timezone.utc).isoformat(timespec="seconds"), "auth.log", "/" + name, m["msg"]
                    continue
                m = SYSLOG_RE.match(line)
                if m:
                    ts = datetime.strptime(f"{year} {m['ts']}", "%Y %b %d %H:%M:%S").replace(tzinfo=timezone.utc)
                    yield ts.isoformat(timespec="seconds"), "auth.log", "/" + name, m["msg"]


def history_events(root):
    homes = list((root / "home").glob("*/.bash_history")) + [root / "root/.bash_history"]
    for hist in homes:
        if not hist.exists():
            continue
        stamp = None
        with open(hist, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if re.fullmatch(r"#\d{9,11}", line):
                    stamp = int(line[1:])
                elif line and stamp is not None:
                    yield utc(stamp), "bash_history", "/" + str(hist.relative_to(root)), line
                    stamp = None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", help="mount point of the evidence image (read-only)")
    parser.add_argument("--dirs", nargs="*", default=["etc", "root", "home", "tmp", "var/tmp"])
    parser.add_argument("--year", type=int, default=datetime.now(timezone.utc).year,
                        help="year for classic syslog timestamps (they omit it)")
    parser.add_argument("--since", help="only events at/after this ISO time (UTC)")
    parser.add_argument("--csv", default="timeline.csv")
    args = parser.parse_args()

    root = Path(args.root)
    events = [*file_events(root, args.dirs), *auth_events(root, args.year), *history_events(root)]
    if args.since:
        events = [e for e in events if e[0] >= args.since]
    events.sort(key=lambda e: e[0])

    with open(args.csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time_utc", "source", "artifact", "detail"])
        writer.writerows(events)
    print(f"{len(events)} events written to {args.csv}")
    for e in events[-15:]:
        print("  " + " | ".join(e))


if __name__ == "__main__":
    main()
