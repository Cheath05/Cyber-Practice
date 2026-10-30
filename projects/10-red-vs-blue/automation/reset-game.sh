#!/usr/bin/env bash
# Roll all blue boxes back to their 'game-start' snapshot between rounds (run on the Proxmox host).
# Usage: ./reset-game.sh [vmid ...]      (default: 321 322 323)
set -euo pipefail
SNAP="${SNAP:-game-start}"
ids=("$@"); [[ ${#ids[@]} -gt 0 ]] || ids=(321 322 323)

read -r -p "Roll back ${ids[*]} to snapshot '$SNAP'? Current state will be lost. [y/N] " a
[[ "$a" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }

for id in "${ids[@]}"; do
  if ! qm listsnapshot "$id" 2>/dev/null | grep -q "$SNAP"; then
    echo "  $id: no '$SNAP' snapshot, skipping"; continue
  fi
  echo "  $id: stopping and rolling back..."
  qm stop "$id" >/dev/null 2>&1 || true
  qm rollback "$id" "$SNAP"
  qm start "$id"
done
echo "Reset complete. Give services ~1 minute to come up before the next round."
