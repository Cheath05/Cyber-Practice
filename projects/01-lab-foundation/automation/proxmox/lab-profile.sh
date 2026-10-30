#!/usr/bin/env bash
# Start/stop lab profiles (see docs/network-reference.md#lab-profiles).
# Usage: ./lab-profile.sh <A|B|C|CB|D|E|F> | stop | status
# Edit PROD_VMID and the profile lists to match your VMIDs.
set -euo pipefail

PROD_VMID="${PROD_VMID:-101}"        # your prod-ubuntu VMID: CHECK THIS
SHUTDOWN_TIMEOUT=180

# Profile -> VMIDs to start. "needs_prod_off" profiles stop prod-ubuntu first.
declare -A PROFILE=(
  [A]="301 302"            # lab-docker, metasploitable2 (+201 kali if you use the VM)
  [B]="501 502"            # dc01, ws01 (+201 kali for LLMNR exercise)
  [C]="401 301"            # wazuh + lab-docker as an endpoint
  [CB]="401 501 502"       # purple team
  [D]="110 321 322 323"    # scoring + blue boxes
  [E]="303 301"            # ctf-host + lab-docker
  [F]="402 301 302"        # scanner + targets
)
declare -A NEEDS_PROD_OFF=( [B]=1 [C]=1 [CB]=1 )
ALL_LAB_VMIDS="110 201 301 302 303 310 311 321 322 323 401 402 501 502"

exists()  { qm status "$1" >/dev/null 2>&1; }
running() { [[ "$(qm status "$1" 2>/dev/null | awk '{print $2}')" == "running" ]]; }

stop_vm() {
  local id="$1"
  if exists "$id" && running "$id"; then
    echo "Shutting down $id..."
    qm shutdown "$id" --timeout "$SHUTDOWN_TIMEOUT" || { echo "  forcing stop $id"; qm stop "$id"; }
  fi
}

case "${1:-}" in
  status)
    qm list
    free -h
    ;;
  stop)
    for id in $ALL_LAB_VMIDS; do stop_vm "$id"; done
    if exists "$PROD_VMID" && ! running "$PROD_VMID"; then
      read -r -p "Start prod-ubuntu ($PROD_VMID) again? [y/N] " a
      [[ "$a" =~ ^[Yy]$ ]] && qm start "$PROD_VMID"
    fi
    ;;
  A|B|C|CB|D|E|F)
    p="$1"
    # Stop every lab VM that isn't in this profile
    for id in $ALL_LAB_VMIDS; do
      [[ " ${PROFILE[$p]} " == *" $id "* ]] || stop_vm "$id"
    done
    if [[ -n "${NEEDS_PROD_OFF[$p]:-}" ]] && exists "$PROD_VMID" && running "$PROD_VMID"; then
      read -r -p "Profile $p needs prod-ubuntu ($PROD_VMID) stopped. Stop it now? [y/N] " a
      if [[ "$a" =~ ^[Yy]$ ]]; then
        stop_vm "$PROD_VMID"
      else
        echo "Continuing with prod running. Watch memory (free -h)."
      fi
    fi
    for id in ${PROFILE[$p]}; do
      if exists "$id"; then
        running "$id" || { echo "Starting $id..."; qm start "$id"; }
      else
        echo "  (skip $id: not created yet)"
      fi
    done
    free -h
    ;;
  *)
    sed -n '2,4p' "$0"; exit 1
    ;;
esac
