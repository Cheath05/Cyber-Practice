#!/usr/bin/env bash
# Create a Windows VM on Proxmox with UEFI, vTPM 2.0 and VirtIO devices, ready to install.
# Usage: ./create-windows-vm.sh <vmid> <name> <windows-iso> [vlan] [memory-MiB] [disk-GB] [ostype]
#   ./create-windows-vm.sh 9011 tpl-win11 Win11_Eval.iso 30 4096 64 win11
#   ./create-windows-vm.sh 9010 tpl-winserver-2022 Server2022_Eval.iso 50 3072 50 win11
# ISOs must already be uploaded to the 'local' storage (ISO Images).
# Proxmox uses ostype 'win11' for Windows 11 and Server 2022/2025.
set -euo pipefail

if [[ $# -lt 3 ]]; then sed -n '2,7p' "$0"; exit 1; fi
VMID="$1"; NAME="$2"; WIN_ISO="$3"
VLAN="${4:-30}"; MEM="${5:-4096}"; DISK="${6:-64}"; OSTYPE="${7:-win11}"
STORAGE="${STORAGE:-local-lvm}"
VIRTIO_ISO="${VIRTIO_ISO:-virtio-win.iso}"

for iso in "$WIN_ISO" "$VIRTIO_ISO"; do
  [[ -f "/var/lib/vz/template/iso/$iso" ]] || { echo "Missing ISO: /var/lib/vz/template/iso/$iso" >&2; exit 1; }
done
if qm status "$VMID" >/dev/null 2>&1; then echo "VMID $VMID exists." >&2; exit 1; fi

qm create "$VMID" --name "$NAME" --ostype "$OSTYPE" --machine q35 --bios ovmf \
  --cpu host --cores 2 --memory "$MEM" --agent enabled=1 \
  --efidisk0 "$STORAGE:1,efitype=4m,pre-enrolled-keys=1" \
  --tpmstate0 "$STORAGE:1,version=v2.0" \
  --scsihw virtio-scsi-single --scsi0 "$STORAGE:$DISK,discard=on,iothread=1,ssd=1" \
  --ide2 "local:iso/$WIN_ISO,media=cdrom" --ide0 "local:iso/$VIRTIO_ISO,media=cdrom" \
  --net0 "virtio,bridge=vmbr1,tag=$VLAN" \
  --boot "order=scsi0;ide2"
echo "Created $NAME ($VMID). Start it, open the Console, and press a key to boot the ISO."
printf '%s\n' "At 'Where do you want to install Windows?': Load driver -> virtio CD -> vioscsi/w11/amd64 (Server: 2k22)."
