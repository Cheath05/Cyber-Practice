#!/usr/bin/env python3
"""Summarize a PCAP: top talkers, protocols, DNS queries, and likely port scans.

Project 02 Python exercise (solution).
    pip install scapy
    python3 pcap_summary.py capture.pcap [--scan-threshold 20]
"""
import argparse
from collections import Counter, defaultdict

try:
    from scapy.all import ARP, DNS, DNSQR, ICMP, IP, TCP, UDP, PcapReader
except ImportError as exc:  # pragma: no cover
    raise SystemExit("scapy is required: pip install scapy") from exc


def summarize(path, scan_threshold):
    talkers = Counter()
    protocols = Counter()
    dns_queries = Counter()
    syn_targets = defaultdict(set)  # (src, dst) -> set of dst ports that got a bare SYN
    total = 0

    with PcapReader(path) as packets:
        for pkt in packets:
            total += 1
            if ARP in pkt:
                protocols["ARP"] += 1
                continue
            if IP not in pkt:
                protocols["other"] += 1
                continue
            src, dst = pkt[IP].src, pkt[IP].dst
            talkers[src] += 1
            if TCP in pkt:
                protocols["TCP"] += 1
                flags = pkt[TCP].flags
                if flags & 0x02 and not flags & 0x10:  # SYN set, ACK not set
                    syn_targets[(src, dst)].add(pkt[TCP].dport)
            elif UDP in pkt:
                protocols["UDP"] += 1
            elif ICMP in pkt:
                protocols["ICMP"] += 1
            else:
                protocols["other-IP"] += 1
            if pkt.haslayer(DNS) and pkt[DNS].qr == 0 and pkt.haslayer(DNSQR):
                name = pkt[DNSQR].qname.decode(errors="replace").rstrip(".")
                dns_queries[name] += 1

    print(f"Packets: {total}\n")
    print("Top talkers (by packets sent):")
    for ip, count in talkers.most_common(5):
        print(f"  {ip:<16} {count}")
    print("\nProtocols:")
    for proto, count in protocols.most_common():
        print(f"  {proto:<9} {count}")
    print(f"\nDNS queries ({len(dns_queries)} unique):")
    for name, count in dns_queries.most_common(20):
        print(f"  {count:>4}  {name}")
    print(f"\nPossible port scans (> {scan_threshold} distinct ports SYN'd on one host):")
    found = False
    for (src, dst), ports in sorted(syn_targets.items(), key=lambda kv: -len(kv[1])):
        if len(ports) > scan_threshold:
            found = True
            sample = ", ".join(str(p) for p in sorted(ports)[:10])
            print(f"  {src} -> {dst}: {len(ports)} ports (e.g. {sample} ...)")
    if not found:
        print("  none")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pcap")
    parser.add_argument("--scan-threshold", type=int, default=20)
    args = parser.parse_args()
    summarize(args.pcap, args.scan_threshold)


if __name__ == "__main__":
    main()
