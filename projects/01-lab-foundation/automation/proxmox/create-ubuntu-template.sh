#!/usr/bin/env bash
# Build an Ubuntu 24.04 cloud-init template (default VMID 9000).
# Usage: ./create-ubuntu-template.sh [vmid]
# Env overrides: STORAGE, BRIDGE, SSH_KEYS_FILE, CI_USER, SNIPPET
set -euo pipefail

VMID="${1:-9000}"
NAME="tpl-ubuntu-2404"
STORAGE="${STORAGE:-local-lvm}"
BRIDGE="${BRIDGE:-vmbr1}"
CI_USER="${CI_USER:-labadmin}"
SSH_KEYS_FILE="${SSH_KEYS_FILE:-/root/.ssh/authorized_keys}"
IMG_URL="https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
IMG_DIR="/var/lib/vz/template/iso"
IMG="$IMG_DIR/noble-server-cloudimg-amd64.img"
# Optional cloud-init vendor snippet (see vendor-base.yaml), e.g. SNIPPET=local:snippets/vendor-base.yaml
SNIPPET="${SNIPPET:-}"

if qm status "$VMID" >/dev/null 2>&1; then
  echo "VMID $VMID already exists. Pick another or remove it first (qm destroy $VMID)." >&2
  exit 1
fi
[[ -s "$SSH_KEYS_FILE" ]] || { echo "SSH key file $SSH_KEYS_FILE is empty/missing." >&2; exit 1; }

mkdir -p "$IMG_DIR"
if [[ ! -f "$IMG" ]]; then
  echo "Downloading Ubuntu cloud image..."
  wget -q --show-progress -O "$IMG" "$IMG_URL"
fi

qm create "$VMID" --name "$NAME" --ostype l26 --memory 1024 --balloon 512 --cores 2 --cpu host \
  --net0 "virtio,bridge=$BRIDGE" --scsihw virtio-scsi-single --agent enabled=1
qm set "$VMID" --scsi0 "$STORAGE:0,import-from=$IMG,discard=on,ssd=1"
qm set "$VMID" --ide2 "$STORAGE:cloudinit" --boot order=scsi0 --serial0 socket --vga serial0
qm set "$VMID" --ciuser "$CI_USER" --sshkeys "$SSH_KEYS_FILE" --ipconfig0 ip=dhcp
if [[ -n "$SNIPPET" ]]; then
  qm set "$VMID" --cicustom "vendor=$SNIPPET"
fi
qm disk resize "$VMID" scsi0 10G
qm template "$VMID"
echo "Template $VMID ($NAME) created. Clone it with clone-lab-vm.sh."
