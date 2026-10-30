#!/usr/bin/env python3
"""Generate an Ansible inventory from Terraform output (Project 13 Python exercise, solution).

    terraform -chdir=../terraform output -json | python3 tf_to_inventory.py > ../ansible/inventory.ini
    python3 tf_to_inventory.py tf-output.json

Group assignment is by name prefix (edit GROUPS to match your naming).
"""
import json
import sys

GROUPS = {
    "docker_hosts": ("lab-docker", "ctf-host"),
    "blue_boxes": ("rvb-blue-",),
    "siem": ("wazuh",),
}


def main():
    src = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
    data = json.load(src)
    hosts = data["lab_hosts"]["value"]          # {name: ip} from outputs.tf

    grouped = {g: [] for g in GROUPS}
    ungrouped = []
    for name, ip in sorted(hosts.items()):
        for group, prefixes in GROUPS.items():
            if name.startswith(prefixes):
                grouped[group].append((name, ip))
                break
        else:
            ungrouped.append((name, ip))

    print("# Generated from terraform output by tf_to_inventory.py. Do not edit by hand.")
    for group, members in grouped.items():
        if not members:
            continue
        print(f"[{group}]")
        for name, ip in members:
            print(f"{name} ansible_host={ip}")
        print()
    if ungrouped:
        print("[ungrouped_lab]")
        for name, ip in ungrouped:
            print(f"{name} ansible_host={ip}")
        print()
    print("[all_lab:children]")
    for group, members in grouped.items():
        if members:
            print(group)
    if ungrouped:
        print("ungrouped_lab")


if __name__ == "__main__":
    main()
