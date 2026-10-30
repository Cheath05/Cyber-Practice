# Network & Resource Reference (single source of truth)

Every guide in this repo uses the values on this page. If you change something here, change it
everywhere (or better: keep it the same). Your **network design doc** in Project 01 is the
"official" version of this page for your own lab.

> Before any project: check what is actually free.
> On the Proxmox shell run `free -h`, `pvesm status`, and `qm list` (or look at
> **Datacenter → node → Summary**). The numbers below are *recommendations*, not guarantees.

## Physical host

| Item | Value |
|---|---|
| Hardware | Dell OptiPlex 7070 Micro, i5-9500T (6C/6T), 16 GB DDR4, 256 GB NVMe, 1× GbE |
| Hypervisor | Proxmox VE (`vmbr0` = home LAN / WAN side, `vmbr1` = lab) |
| Storage IDs used in scripts | `local` (ISOs, snippets), `local-lvm` (VM disks). Change `STORAGE=` in scripts if yours differ. |

## Segments (VLANs)

`vmbr1` is made **VLAN-aware** in Project 01. OPNsense's vmbr1 NIC carries *all* VLANs (trunk);
each VM NIC gets a VLAN **tag** in Proxmox.

| Segment | VLAN tag | Subnet | Gateway (OPNsense) | DHCP range | Purpose |
|---|---|---|---|---|---|
| LAB-MGMT | none (untagged) | 10.10.10.0/24 | 10.10.10.1 | .100–.199 | Existing lab LAN, admin boxes, white-team/scoring, step-ca |
| RED | 20 | 10.10.20.0/24 | 10.10.20.1 | .100–.199 | Attacker VMs (Kali) |
| TARGETS | 30 | 10.10.30.0/24 | 10.10.30.1 | .100–.199 | Vulnerable VMs/containers, CyberPatriot images, CTF host |
| BLUE | 40 | 10.10.40.0/24 | 10.10.40.1 | .100–.199 | Wazuh SIEM, vuln scanner |
| AD | 50 | 10.10.50.0/24 | 10.10.50.1 | .100–.199 (DNS → DC 10.10.50.10) | Windows domain `lab.local` |
| WG-FRIENDS | n/a (tunnel) | 10.10.99.0/24 | 10.10.99.1 (`wg0`) | static per peer | WireGuard peers (friends, your laptop) |

Home network (`vmbr0`, e.g. `192.168.1.0/24`) is **never** reachable from any lab segment.
In OPNsense, create an alias `HOME_NET` with your real home subnet.

## Static IP plan & VMIDs

VMID convention: `1xx` mgmt · `2xx` red · `3xx` targets · `4xx` blue · `5xx` AD · `9xxx` templates.

| VMID | Name | Segment | IP | RAM | vCPU | Disk | Project |
|---|---|---|---|---|---|---|---|
| *(yours)* | opnsense | WAN + LAB trunk | 10.10.10.1 (+ .1 on each VLAN) | **2 GB** (down from 8) | 2 | 16 GB | 01 |
| *(yours)* | prod-ubuntu | home LAN (vmbr0) | — | ~2 GB (check) | 2 | — | existing |
| 110 | scoring | LAB-MGMT | 10.10.10.20 | 2 GB | 2 | 20 GB | 10 |
| 120 | step-ca (LXC) | LAB-MGMT | 10.10.10.30 | 256 MB | 1 | 4 GB | 12 |
| 201 | kali | RED | 10.10.20.10 | 3 GB | 2 | 40 GB | 06/07 (optional — laptop Kali preferred) |
| 301 | lab-docker | TARGETS | 10.10.30.10 | 3 GB | 2 | 40 GB | 06/02/12 |
| 302 | metasploitable2 | TARGETS | 10.10.30.20 | 512 MB | 1 | 8 GB | 06 |
| 303 | ctf-host | TARGETS | 10.10.30.30 | 2 GB | 2 | 20 GB | 09 |
| 310 | cp-linux | TARGETS | 10.10.30.40 | 2 GB | 2 | 25 GB | 04 |
| 311 | cp-windows | TARGETS | 10.10.30.41 | 4 GB | 2 | 64 GB | 05 |
| 321–323 | rvb-blue-1..3 | TARGETS | 10.10.30.51–.53 | 1.5 GB each | 1 | linked clones | 10 |
| 401 | wazuh | BLUE | 10.10.40.10 | 5 GB | 4 | 50 GB | 08 |
| 402 | scanner | BLUE | 10.10.40.20 | 4 GB | 2 | 40 GB | 12 |
| 501 | dc01 | AD | 10.10.50.10 | 2.5 GB (2 GB if Server Core) | 2 | 50 GB | 07 |
| 502 | ws01 | AD | 10.10.50.20 | 4 GB | 2 | 64 GB | 07/08 |
| 9000 | tpl-ubuntu-2404 | — | cloud-init | — | — | 10 GB | 01 |
| 9010 | tpl-winserver-2022 | — | sysprep | — | — | 50 GB | 07 |
| 9011 | tpl-win11 | — | sysprep | — | — | 64 GB | 05/07 |

Disks are **thin-provisioned** on `local-lvm`, so a 64 GB disk only uses what Windows actually
writes (~20–25 GB). Linked clones of templates use only their changes.

## RAM budget

| Consumer | RAM |
|---|---|
| Proxmox host itself (+ page cache headroom) | ~1.5 GB |
| OPNsense (after resizing) | 2 GB |
| prod-ubuntu (FastAPI + simulation) | ~2 GB — **verify** |
| Safety headroom (never allocate this) | ~1 GB |
| **Lab budget with prod-ubuntu running** | **≈ 9 GB** |
| **Lab budget with prod-ubuntu stopped** | **≈ 11 GB** |

> If your Proxmox root/VM storage is **ZFS**, the ZFS ARC cache can take up to 50% of RAM by
> default. Cap it (Project 01 shows how) or the budget above is wrong.

## Lab profiles (run ONE at a time)

| Profile | VMs | Lab RAM | prod-ubuntu | Used by |
|---|---|---|---|---|
| **A – Network/Linux** | lab-docker 3 + metasploitable2 0.5 + kali 3 (optional) | 3.5–6.5 GB | can stay on | 02, 04, 06, 09, 12 |
| **B – Active Directory** | dc01 2.5 + ws01 4 + kali 2.5 | 9 GB | **stop it** (or use laptop Kali → 6.5 GB) | 07 |
| **C – SOC** | wazuh 5 + lab-docker 3 *or* ws01 4 | 8–9 GB | **stop it** to be safe | 08 |
| **C+B – Purple team** | wazuh 5 + dc01 2 (Core) + ws01 4 | 11 GB | **must stop**; tight — best on two nodes | 08 part 2 |
| **D – Game night** | scoring 2 + rvb-blue ×3 4.5 (+ cp-windows 4 optional) | 6.5–10.5 GB | stop if adding Windows | 10 |
| **E – CTF night** | ctf-host 2 + lab-docker 3 | 5 GB | can stay on | 09 |
| **F – Vuln mgmt** | scanner 4 + lab-docker 3 + metasploitable2 0.5 | 7.5 GB | can stay on | 12 |

Helper: `projects/01-lab-foundation/automation/proxmox/lab-profile.sh` starts/stops profiles and
cleanly stops prod-ubuntu when a profile needs it.

## Firewall policy matrix (OPNsense, default deny)

Rows = source interface, columns = destination. ✅ allow · ❌ block · ⏱ allow only while
building/updating (rule exists but is **disabled** by default).

| From \ To | LAB-MGMT | RED | TARGETS | BLUE | AD | WG-FRIENDS | Internet | HOME_NET | Firewall GUI |
|---|---|---|---|---|---|---|---|---|---|
| **LAB-MGMT** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **RED** | ❌ | ✅ | ✅ | ❌ | ✅ (AD project only) | ❌ | ✅ (updates) | ❌ | ❌ (DNS only) |
| **TARGETS** | ❌ | ❌ | ✅ | ✅ tcp/1514-1515 to Wazuh only | ❌ | ❌ | ⏱ | ❌ | ❌ |
| **BLUE** | ❌ | ✅ (scan) | ✅ (scan) | ✅ | ✅ (scan) | ❌ | ✅ (updates/feeds) | ❌ | ❌ (DNS only) |
| **AD** | ❌ | ❌ | ❌ | ✅ tcp/1514-1515 to Wazuh only | ✅ | ❌ | ⏱ | ❌ | ❌ (DNS → DC) |
| **WG-FRIENDS** | ❌ (except scoring 10.10.10.20:80) | ❌ | ✅ | ❌ | ⏱ (game nights) | ❌ | ❌ | ❌ | ❌ |

Notes:
- **Admin laptop:** until WireGuard (P03), your laptop on the home LAN reaches `LAB_NETS` through
  a WAN rule `ADMIN_LAPTOP → LAB_NETS` plus a static route on the laptop (P01 step 5b). This is
  inbound-only; lab hosts still can't initiate connections to `HOME_NET`.
- "Firewall GUI" means OPNsense's own web UI/SSH. Only LAB-MGMT (and your own WireGuard peer, if
  you add a rule for it) may manage the firewall.
- LLMNR/NBT-NS poisoning (Project 07) only works **inside the same broadcast domain** — the
  attacker must have a NIC in VLAN 50 for that exercise. Routing from RED is not enough.

## DNS names

OPNsense Unbound host overrides (Services → Unbound DNS → Overrides), domain `lab.home.arpa`:
`scoring`, `ca`, `kali`, `lab-docker`, `msf2`, `ctf`, `cp-linux`, `cp-windows`, `wazuh`,
`scanner`. The AD domain `lab.local` is served by **dc01**; add a Unbound *domain override*
forwarding `lab.local` → `10.10.50.10` so other segments can resolve it.
