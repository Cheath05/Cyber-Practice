#!/usr/bin/env bash
# Run on the Proxmox host. Creates lab-docker (VMID 301) on TARGETS from template 9000.
set -euo pipefail
TPL="${TPL:-9000}"; ID="${ID:-301}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$here/../../01-lab-foundation/automation/proxmox/clone-lab-vm.sh" "$TPL" "$ID" lab-docker 30 10.10.30.10/24 3072 40
qm set "$ID" --balloon 1024 --cores 2
qm start "$ID"
echo "Now enable the TARGETS TEMP egress rule, then run install-docker.sh inside the VM."
