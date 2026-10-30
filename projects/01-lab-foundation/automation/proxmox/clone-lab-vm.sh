#!/usr/bin/env bash
# Linked-clone a template into a lab VLAN with a static IP.
# Usage: ./clone-lab-vm.sh <template-vmid> <new-vmid> <name> <vlan|0> <ip/cidr> [memory-MiB] [disk-GB]
# Example: ./clone-lab-vm.sh 9000 301 lab-docker 30 10.10.30.10/24 3072 40
#   vlan 0 = untagged (LAB-MGMT)
set -euo pipefail

if [[ $# -lt 5 ]]; then
  sed -n '2,6p' "$0"; exit 1
fi

TPL="$1"; NEWID="$2"; NAME="$3"; VLAN="$4"; IPCIDR="$5"
MEM="${6:-2048}"; DISK_GB="${7:-}"
BRIDGE="${BRIDGE:-vmbr1}"

if qm status "$NEWID" >/dev/null 2>&1; then
  echo "VMID $NEWID already exists." >&2; exit 1
fi

# Gateway = first host of the /24 (10.10.X.1)
GW="$(echo "${IPCIDR%/*}" | awk -F. '{print $1"."$2"."$3".1"}')"
NET="virtio,bridge=$BRIDGE"
[[ "$VLAN" != "0" ]] && NET="$NET,tag=$VLAN"

qm clone "$TPL" "$NEWID" --name "$NAME"
qm set "$NEWID" --net0 "$NET" --ipconfig0 "ip=$IPCIDR,gw=$GW" --nameserver "$GW" \
  --memory "$MEM" --balloon "$(( MEM / 2 ))"
if [[ -n "$DISK_GB" ]]; then
  qm disk resize "$NEWID" scsi0 "${DISK_GB}G"
fi
echo "Created $NAME ($NEWID) on VLAN $VLAN with $IPCIDR (gw $GW). Start with: qm start $NEWID"
