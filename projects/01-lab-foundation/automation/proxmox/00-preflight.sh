#!/usr/bin/env bash
# Read-only capacity report for the Proxmox host. Safe to run any time.
# Usage: ./00-preflight.sh
set -uo pipefail

warn() { printf '  \e[33mWARN\e[0m %s\n' "$*"; }
ok()   { printf '  \e[32mOK\e[0m   %s\n' "$*"; }
hdr()  { printf '\n\e[1m== %s ==\e[0m\n' "$*"; }

command -v qm >/dev/null || { echo "Run this on the Proxmox host."; exit 1; }

hdr "Memory"
free -h
avail_mb=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
total_mb=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
echo "  Available: ${avail_mb} MiB of ${total_mb} MiB"
if (( avail_mb < 2048 )); then warn "Less than 2 GiB available. Stop a lab profile before starting another."; else ok "Available memory looks fine"; fi
if [[ -r /proc/pressure/memory ]]; then
  echo "  Memory pressure: $(head -1 /proc/pressure/memory)"
fi
if [[ -r /sys/kernel/mm/ksm/pages_sharing ]]; then
  pages=$(cat /sys/kernel/mm/ksm/pages_sharing)
  echo "  KSM shared pages: $pages (~$(( pages * 4 / 1024 )) MiB saved)"
fi
if systemctl is-active --quiet ksmtuned; then ok "ksmtuned active"; else warn "ksmtuned not active"; fi

hdr "ZFS ARC"
if [[ -r /proc/spl/kstat/zfs/arcstats ]]; then
  arc_max=$(awk '$1=="c_max" {print int($3/1024/1024)}' /proc/spl/kstat/zfs/arcstats)
  arc_size=$(awk '$1=="size" {print int($3/1024/1024)}' /proc/spl/kstat/zfs/arcstats)
  echo "  ARC size ${arc_size} MiB, max ${arc_max} MiB"
  (( arc_max > 2048 )) && warn "ARC max > 2 GiB. Consider capping it (see Project 01 step 2)."
else
  ok "ZFS not in use (no ARC to cap)"
fi

hdr "Guests"
qm list
command -v pct >/dev/null && pct list

running_mb=0
while read -r vmid; do
  mem=$(qm config "$vmid" | awk '/^memory:/ {print $2}')
  running_mb=$(( running_mb + ${mem:-0} ))
done < <(qm list | awk 'NR>1 && $3=="running" {print $1}')
echo "  RAM allocated to running VMs: ${running_mb} MiB"
(( running_mb > total_mb * 85 / 100 )) && warn "Running VMs are allocated >85% of host RAM"

hdr "Storage"
pvesm status
if command -v lvs >/dev/null; then
  lvs --noheadings -o lv_name,data_percent,metadata_percent 2>/dev/null | awk '$2!="" {print "  thin pool " $1 ": data " $2 "%, meta " $3 "%"}'
fi

hdr "Bridges"
for br in vmbr0 vmbr1; do
  if ip link show "$br" >/dev/null 2>&1; then
    aware=$(cat "/sys/class/net/$br/bridge/vlan_filtering" 2>/dev/null || echo "?")
    echo "  $br: vlan_filtering=$aware  $(ip -br addr show "$br" | awk '{print $3}')"
  else
    warn "$br does not exist"
  fi
done
if [[ "$(cat /sys/class/net/vmbr1/bridge/vlan_filtering 2>/dev/null)" == "1" ]]; then
  ok "vmbr1 is VLAN-aware"
else
  warn "vmbr1 is not VLAN-aware yet (Project 01 step 3)"
fi

hdr "Which bridge is each VM NIC on?"
for vmid in $(qm list | awk 'NR>1 {print $1}'); do
  qm config "$vmid" | awk -v id="$vmid" '/^net[0-9]+:/ {print "  " id ": " $0}'
done
echo
echo "Done. Nothing was changed."
