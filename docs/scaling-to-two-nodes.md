# Scaling Beyond One Node (optional)

Everything in this repo works on the single 16 GB OptiPlex. This page is for when RAM limits
start to hurt, mostly in Project 08 part 2 (purple team: Wazuh + DC + workstation at once) and
Project 10 (multiple Windows blue boxes).

## Option 1 (cheapest): upgrade the current box's RAM

- The OptiPlex 7070 Micro has **2 SO-DIMM slots** (DDR4-2666). Dell's spec sheet lists up to
  64 GB for this model. Confirm against your exact service tag on Dell's support site before
  buying.
- **16 → 32 GB (2×16 GB)** roughly *triples* your lab budget (≈9 GB → ≈25 GB), because the
  host, OPNsense and prod-ubuntu overhead stays fixed.
- A bigger NVMe (1 TB) also helps once you have several Windows templates. You'd migrate with a
  Proxmox backup/restore or a fresh install plus restore.
- **Do this first.** It's the best value per dollar.

## Option 2: a second OptiPlex Micro (node 2)

Buy one with **32 GB+** already installed (used 7070/7080 Micros are common and cheap). That
gives you more CPU too, and teaches multi-host networking.

### Suggested roles

| Node | Runs | Why |
|---|---|---|
| **pve1** (current) | OPNsense, prod-ubuntu, Linux labs (Profiles A, E, F), scoring, step-ca | Keeps the router and prod on the box you know |
| **pve2** (new) | Windows/AD (B), Wazuh (C), game-night blue boxes (D) | The RAM-hungry stuff; lets B and C run together |

### Networking: getting VLANs to the second node

Both Micros have **one NIC**. Lab VLANs live behind OPNsense on pve1, so pve2's VMs need those
VLANs delivered over a wire. Two ways:

**A. 802.1Q managed switch (recommended, very educational)**
- Buy a cheap managed switch with VLAN support (5–8 ports).
- Each node's single NIC becomes a **trunk**: untagged = home LAN (management + OPNsense
  WAN), tagged 10/20/30/40/50 = lab. LAB-MGMT also needs a tag on the trunk; give it
  **VLAN 10**, since untagged traffic is the home LAN on the switch.
- On each node, `vmbr0` becomes VLAN-aware. OPNsense's LAN NIC moves to `vmbr0` with the lab
  VLANs as tags. Lab VMs on pve2 use `vmbr0` + their VLAN tag.
- Your home router port connects to an **untagged home-LAN** switch port.
- Risk: a misconfigured trunk can leak lab VLANs into your home LAN. Document the switch port
  config in your network design doc and test isolation from a home device.

**B. Dedicated lab link with a USB 3 gigabit NIC**
- Add a USB NIC to each node and connect them directly with a cable (no switch needed).
- On both nodes, put the USB NIC into a VLAN-aware `vmbr1`. Lab VLANs ride this cable,
  physically separate from the home LAN.
- Simpler isolation story; USB NICs are slightly less reliable under heavy load.

### Cluster or two standalone nodes?

| | Proxmox cluster | Two standalone nodes |
|---|---|---|
| Single GUI for both | ✅ | ❌ (two browser tabs) |
| Live/offline migration between nodes | ✅ | Backup → restore |
| Quorum risk | ⚠️ With 2 nodes, if one is off the other loses quorum and VMs can't start or be changed. **Fix: add a QDevice** (a third vote from any small always-on Linux box *outside* the cluster, e.g. a Raspberry Pi) | None |
| Complexity | Medium | Low |

Recommendation: start **standalone**. Cluster only once you have a QDevice host. A QDevice
cannot run as a VM *on* the cluster it votes for. (Temporary workaround: `pvecm expected 1`
on the surviving node. Use it knowingly; it bypasses split-brain protection.)

### Backups (stretch)

Run **Proxmox Backup Server** as a VM/LXC on the *other* node, or on an external disk, so each
node backs up to the other. It dedupes, so Windows templates back up small.

## How the lab profiles change with two nodes

| Profile | One node | Two nodes |
|---|---|---|
| B – AD | Stop prod-ubuntu | Runs on pve2, prod stays up |
| C+B – Purple team | 11 GB, prod off, tight | Comfortable on pve2 (32 GB) |
| D – Game night | 3 Linux blue boxes (+1 Windows if prod off) | 3 Linux + 2 Windows blue boxes |
| Full GOAD (P07 stretch) | ❌ | Possible on a 32–64 GB node |

Each project's *Resources* section notes the two-node option where it matters.
