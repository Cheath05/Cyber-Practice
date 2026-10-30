# ⚠️ Solution: use only if stuck

Try the guide first. If a step has blocked you for more than about 45 minutes, read the
matching file here, understand it, then do the step yourself (or run it). Note in your
WORKLOG what you were missing.

| File | Run where | What it does |
|---|---|---|
| `proxmox/00-preflight.sh` | Proxmox host | Read-only report: RAM, storage, VMs, bridges, ZFS ARC, warnings |
| `proxmox/create-ubuntu-template.sh` | Proxmox host | Builds template 9000 (Ubuntu 24.04 cloud-init) |
| `proxmox/clone-lab-vm.sh` | Proxmox host | Linked-clones a template into a VLAN with a static IP |
| `proxmox/lab-profile.sh` | Proxmox host | Starts/stops lab profiles A–F; stops prod-ubuntu cleanly when needed |
| `proxmox/vendor-base.yaml` | Proxmox `local:snippets` | Cloud-init vendor data: installs qemu-guest-agent, sets timezone |
| `proxmox/validate-isolation.sh` | A lab VM | Tests the firewall matrix from the VM's segment and prints PASS/FAIL |
| `opnsense/config-checklist.md` | — | Click-by-click OPNsense checklist for VLANs, DHCP, aliases, rules |
| `python/ram_report.py` | Proxmox host | Python exercise solution: RAM allocation report + profile fit check |

All scripts are parameterized at the top. Read them before running.
