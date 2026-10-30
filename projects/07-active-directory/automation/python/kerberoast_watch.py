#!/usr/bin/env python3
"""Flag Kerberoasting in exported Windows Security events (Project 07 Python exercise, solution).

Kerberoasting tools request service tickets (event 4769) and usually ask for RC4 encryption
(Ticket Encryption Type 0x17), because RC4 tickets are much faster to crack. Legitimate modern
clients use AES (0x11 / 0x12). This script looks for RC4 TGS requests for user-account SPNs and
counts them per requesting account, which is the same logic you'll put into Wazuh in P08.

Export events on the DC (PowerShell), then run this anywhere:
    Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4769} -MaxEvents 5000 |
      ForEach-Object { $x=[xml]$_.ToXml(); $d=@{TimeCreated=$_.TimeCreated.ToString('o')};
        $x.Event.EventData.Data | ForEach-Object { $d[$_.Name]=$_.'#text' }; [pscustomobject]$d } |
      ConvertTo-Json | Set-Content 4769.json
    python3 kerberoast_watch.py 4769.json --threshold 3

Also accepts CSV with the same field names (ServiceName, TicketEncryptionType, TargetUserName,
IpAddress, TimeCreated).
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict

RC4 = {"0x17", "23"}


def load(path):
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8-sig") as fh:
            return list(csv.DictReader(fh))
    with open(path, encoding="utf-8-sig") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("events", help="JSON or CSV export of event 4769")
    parser.add_argument("--threshold", type=int, default=3,
                        help="distinct RC4 service tickets per requester before flagging (default 3)")
    args = parser.parse_args()

    rc4_by_requester = defaultdict(set)   # requester -> set of services
    rc4_services = Counter()
    sources = defaultdict(set)
    total = 0
    for ev in load(args.events):
        total += 1
        enc = str(ev.get("TicketEncryptionType", "")).lower()
        service = ev.get("ServiceName", "")
        # Ignore machine accounts (end in $) and krbtgt: those aren't roastable user SPNs
        if enc not in RC4 or not service or service.endswith("$") or service.lower() == "krbtgt":
            continue
        requester = ev.get("TargetUserName", "?")
        rc4_by_requester[requester].add(service)
        rc4_services[service] += 1
        sources[requester].add(ev.get("IpAddress", "?"))

    print(f"Events read: {total}")
    print(f"RC4 service-ticket requests for user SPNs: {sum(rc4_services.values())}\n")
    print("Most-requested RC4 services (likely Kerberoasting targets):")
    for svc, n in rc4_services.most_common(10):
        print(f"  {svc:<20} {n}")
    print(f"\nRequesters with >= {args.threshold} distinct RC4 service tickets (ALERT):")
    flagged = 0
    for requester, services in sorted(rc4_by_requester.items(), key=lambda kv: -len(kv[1])):
        if len(services) >= args.threshold:
            flagged += 1
            print(f"  {requester:<20} {len(services)} services from {', '.join(sorted(sources[requester]))}")
    if not flagged:
        print("  none")
    print("\nNote: one RC4 request is enough to investigate in a modern AES-only domain.")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
