# Python Primer for Security Scripting

Every project has a Python exercise. This primer explains **each technique the solutions use**,
with a tiny example and a link to learn more. Read the sections a project's *Coding
exercises* section points to *before* you start that exercise.

New to Python entirely? Do [CS50P](https://cs50.harvard.edu/python/) weeks 0–6 first (or
[MIT 6.100L](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/)).

## 0. Setup: virtual environments

Keep each project's packages separate so nothing breaks system Python (Proxmox and Ubuntu use
it!).

```bash
python3 -m venv .venv          # create
source .venv/bin/activate      # enter (Windows: .venv\Scripts\activate)
pip install scapy requests     # install into the venv only
deactivate                     # leave
```
📖 [venv tutorial](https://docs.python.org/3/tutorial/venv.html)

## 1. Script skeleton and `argparse` (command-line arguments)

Every tool here has the same shape, so you can read any of them once you know it:

```python
#!/usr/bin/env python3
"""One-line description (shows in --help)."""
import argparse

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcap")                                   # required positional
    parser.add_argument("--threshold", type=int, default=20)      # optional with default
    parser.add_argument("--verbose", action="store_true")         # on/off flag
    args = parser.parse_args()
    print(args.pcap, args.threshold, args.verbose)

if __name__ == "__main__":   # only runs when executed, not when imported
    main()
```
📖 [argparse tutorial](https://docs.python.org/3/howto/argparse.html) · Used in: all projects

## 2. Running other programs: `subprocess`

Security scripting is often "glue": run a tool, parse its output.

```python
import subprocess
out = subprocess.run(["pvesh", "get", "/nodes", "--output-format", "json"],
                     check=True, capture_output=True, text=True).stdout
```
- Pass a **list**, not a string. That avoids shell injection (`shell=True` with user input is a
  classic vulnerability; see P06).
- `check=True` raises an exception if the command fails.

📖 [subprocess docs](https://docs.python.org/3/library/subprocess.html) · Used in: P01, P12

## 3. Data formats: JSON and CSV

```python
import json, csv
data = json.loads(out)                     # str -> Python lists/dicts
for vm in data:
    print(vm["vmid"], vm.get("name", "?")) # .get() avoids KeyError when a field is missing

with open("tracker.csv", "w", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=["id", "host", "severity"])
    writer.writeheader()
    writer.writerow({"id": "V-001", "host": "10.10.30.10", "severity": "High"})

with open("peers.csv", newline="") as fh:
    rows = list(csv.DictReader(fh))        # each row is a dict keyed by header
```
Many tools output **JSON Lines** (one JSON object per line: Wazuh `alerts.json`, Nuclei
`-jsonl`). Read them with `for line in fh: event = json.loads(line)`.

📖 [json](https://docs.python.org/3/library/json.html) · [csv](https://docs.python.org/3/library/csv.html) · Used in: P01, P03, P08, P12

## 4. Counting and grouping: `collections`

The core of most log/packet analysis is "count things" and "group things".

```python
from collections import Counter, defaultdict
talkers = Counter()
talkers["10.10.20.99"] += 1
talkers.most_common(5)                      # [('10.10.20.99', 1)]

ports_by_pair = defaultdict(set)            # missing keys start as an empty set
ports_by_pair[("10.10.20.99", "10.10.30.10")].add(80)
```
📖 [collections](https://docs.python.org/3/library/collections.html) · Used in: P02, P08, P11

## 5. Regular expressions: `re`

Pull structured data out of unstructured logs.

```python
import re
line = "Failed password for invalid user admin from 10.10.20.99 port 51122 ssh2"
m = re.search(r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)", line)
if m:
    user, ip = m.groups()                   # ('admin', '10.10.20.99')
```
Practice at [regex101.com](https://regex101.com/) (pick the *Python* flavor).
📖 [Regex HOWTO](https://docs.python.org/3/howto/regex.html) · Used in: P04, P08, P10, P11

## 6. IP addresses and subnets: `ipaddress`

Never parse IPs with string splitting.

```python
import ipaddress
net = ipaddress.ip_network("10.10.30.0/24")
ipaddress.ip_address("10.10.30.10") in net  # True
net.num_addresses, net.broadcast_address    # (256, IPv4Address('10.10.30.255'))
ipaddress.ip_address("192.168.1.5").is_private  # True
```
📖 [ipaddress HOWTO](https://docs.python.org/3/howto/ipaddress.html) · Used in: P02, P08, P12

## 7. Files and paths: `pathlib`, binary I/O, hashing

```python
from pathlib import Path
import hashlib

for p in Path("/var/log").rglob("*.log"):   # recursive glob
    print(p.name, p.stat().st_size)

h = hashlib.sha256()
with open("memory.lime", "rb") as fh:       # "rb" = read bytes
    for chunk in iter(lambda: fh.read(1024 * 1024), b""):
        h.update(chunk)                      # stream: works on files bigger than RAM
print(h.hexdigest())
```
📖 [pathlib](https://docs.python.org/3/library/pathlib.html) · [hashlib](https://docs.python.org/3/library/hashlib.html) · Used in: P11 (evidence hashing), P04

## 8. Time: `datetime`

```python
from datetime import datetime, timezone, timedelta
ts = datetime.fromisoformat("2026-11-20T14:02:11+00:00")
age = datetime.now(timezone.utc) - ts
if age > timedelta(days=30): print("stale")
```
Always keep timestamps in **UTC** in security work (incident timelines mix time zones otherwise).
📖 [datetime](https://docs.python.org/3/library/datetime.html) · Used in: P03, P08, P11, P12

## 9. Talking to web APIs: `requests`

```python
import requests
r = requests.get("https://10.10.40.10:55000/", timeout=10, verify=False)  # lab self-signed cert
r.raise_for_status()
print(r.json())
```
- `verify=False` is acceptable **only** in your lab with self-signed certs. P12 replaces that
  with your own CA (`verify="/path/to/root_ca.crt"`). That's the right fix.
- Always set `timeout=`.

📖 [requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/) · Used in: P08 (Wazuh API), P06, P14

## 10. Sockets: talking TCP directly

```python
import socket
with socket.create_connection(("10.10.30.10", 80), timeout=3) as s:
    s.sendall(b"GET / HTTP/1.0\r\nHost: test\r\n\r\n")
    print(s.recv(4096).decode(errors="replace"))
```
This is what `curl`, `nc` and port scanners do underneath. Write a 20-line TCP port scanner
with this as practice (then compare its speed to nmap and find out why nmap uses raw SYN
packets).
📖 [Socket programming HOWTO](https://docs.python.org/3/howto/sockets.html) · Used in: P02, P06, P10

## 11. Packets: `scapy`

```python
from scapy.all import rdpcap, IP, TCP
for pkt in rdpcap("scan.pcap"):
    if IP in pkt and TCP in pkt and pkt[TCP].flags == "S":
        print(pkt[IP].src, "->", pkt[IP].dst, pkt[TCP].dport)
```
- `rdpcap` loads everything into RAM. Use `PcapReader` (a streaming iterator) for big files.
- Scapy can also *craft* packets (`sr1(IP(dst=...)/TCP(dport=80, flags="S"))`), but only
  against your lab.

📖 [Scapy usage](https://scapy.readthedocs.io/en/latest/usage.html) · Used in: P02

## 12. Concurrency (just enough): `concurrent.futures`

Network checks are slow because they wait on I/O. Threads let you check many hosts at once.

```python
from concurrent.futures import ThreadPoolExecutor
def check(host): ...
with ThreadPoolExecutor(max_workers=20) as pool:
    results = list(pool.map(check, ["10.10.30.10", "10.10.30.20"]))
```
📖 [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) · Used in: P10 (service checker)

## 13. Databases: `sqlite3`

```python
import sqlite3
db = sqlite3.connect("vulns.db")
db.execute("CREATE TABLE IF NOT EXISTS vulns (host TEXT, cve TEXT, cvss REAL)")
db.execute("INSERT INTO vulns VALUES (?, ?, ?)", ("10.10.30.20", "CVE-2011-2523", 9.8))  # ? = parameterized
db.commit()
for row in db.execute("SELECT host, MAX(cvss) FROM vulns GROUP BY host"):
    print(row)
```
**Always use `?` placeholders.** Building SQL with f-strings is exactly the SQL injection you
exploit in P06.
📖 [sqlite3](https://docs.python.org/3/library/sqlite3.html) · Used in: P12

## 14. Testing your own tools: `unittest` / `pytest`

```python
# test_parse.py  — run with:  python3 -m pytest
from wg_status import human_bytes
def test_human_bytes():
    assert human_bytes(2048) == "2 KiB"
```
Tests prove your parser handles weird input. Writing one test per tool is a good resume habit.
📖 [pytest getting started](https://docs.pytest.org/en/stable/getting-started.html)

## Where each project uses what

| Project | Sections |
|---|---|
| 01 | 1, 2, 3 |
| 02 | 1, 4, 6, 10, 11 |
| 03 | 1, 3, 8 |
| 04 | 1, 5, 7 |
| 05 | 1, 3 (+ PowerShell) |
| 06 | 9, 10 |
| 07 | 3, 4 (+ PowerShell) |
| 08 | 3, 4, 5, 8, 9 |
| 09 | 1, 9 |
| 10 | 10, 12 |
| 11 | 4, 5, 7, 8 |
| 12 | 2, 3, 6, 13 |
| 13 | 3 (+ HCL/YAML) |
| 14 | 9 (+ JSON IAM policies) |
