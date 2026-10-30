#!/usr/bin/env python3
"""RAM allocation report for a Proxmox host (Project 01 Python exercise, solution).

Run on the Proxmox host:
    python3 ram_report.py            # report
    python3 ram_report.py --profile C   # would profile C fit right now?

Uses only the standard library and the `pvesh` CLI that ships with Proxmox.
"""
import argparse
import json
import subprocess
import sys

MIB = 1024 * 1024
WARN_PCT = 85
HEADROOM_MIB = 1024  # never plan to use the last ~1 GiB

# Planned RAM per profile in MiB (docs/network-reference.md). Keep in sync with lab-profile.sh.
PROFILES = {
    "A": {301: 3072, 302: 512},
    "B": {501: 2560, 502: 4096, 201: 2560},
    "C": {401: 5120, 301: 3072},
    "CB": {401: 5120, 501: 2048, 502: 4096},
    "D": {110: 2048, 321: 1536, 322: 1536, 323: 1536},
    "E": {303: 2048, 301: 3072},
    "F": {402: 4096, 301: 3072, 302: 512},
}


def pvesh(path, **params):
    cmd = ["pvesh", "get", path, "--output-format", "json"]
    for key, value in params.items():
        cmd += [f"--{key}", str(value)]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=sorted(PROFILES), help="check if a lab profile fits")
    args = parser.parse_args()

    try:
        guests = pvesh("/cluster/resources", type="vm")
        nodes = pvesh("/cluster/resources", type="node")
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        sys.exit(f"pvesh failed ({exc}). Run this on the Proxmox host as root.")

    host_total = sum(n.get("maxmem", 0) for n in nodes) // MIB
    host_used = sum(n.get("mem", 0) for n in nodes) // MIB

    print(f"{'VMID':>5}  {'TYPE':<4} {'NAME':<22} {'STATUS':<8} {'ALLOC MiB':>9} {'USED MiB':>9}")
    allocated_running = 0
    running_ids = set()
    for g in sorted(guests, key=lambda g: g["vmid"]):
        alloc = g.get("maxmem", 0) // MIB
        used = g.get("mem", 0) // MIB
        if g.get("status") == "running":
            allocated_running += alloc
            running_ids.add(g["vmid"])
        print(f"{g['vmid']:>5}  {g['type']:<4} {g.get('name', '?'):<22} {g.get('status', '?'):<8} "
              f"{alloc:>9} {used:>9}")

    pct = 100 * allocated_running / host_total if host_total else 0
    print(f"\nHost RAM: {host_total} MiB total, {host_used} MiB used (actual)")
    print(f"Allocated to running guests: {allocated_running} MiB ({pct:.0f}% of host)")
    if pct > WARN_PCT:
        print(f"WARNING: running guests are allocated more than {WARN_PCT}% of host RAM.")

    if args.profile:
        plan = PROFILES[args.profile]
        extra = sum(mem for vmid, mem in plan.items() if vmid not in running_ids)
        free_now = host_total - host_used - HEADROOM_MIB
        verdict = "FITS" if extra <= free_now else "DOES NOT FIT"
        print(f"\nProfile {args.profile}: needs {extra} MiB more; ~{free_now} MiB free after headroom -> {verdict}")
        if verdict != "FITS":
            print("Try: stop other lab VMs (lab-profile.sh stop) or prod-ubuntu, then re-check.")


if __name__ == "__main__":
    main()
