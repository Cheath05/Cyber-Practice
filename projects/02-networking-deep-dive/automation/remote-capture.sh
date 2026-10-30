#!/usr/bin/env bash
# Stream a remote tcpdump into local Wireshark.
# Usage: ./remote-capture.sh <user@host> [interface] [capture filter]
#   ./remote-capture.sh labadmin@10.10.30.10 eth0 'port 80'
set -euo pipefail
target="${1:?user@host required}"
iface="${2:-eth0}"
filter="${3:-not port 22}"
# -U: packet-buffered output so packets appear immediately; -w -: write pcap to stdout
# shellcheck disable=SC2029  # expanding the filter locally is intended
ssh "$target" "sudo tcpdump -i $iface -U -s0 -w - '$filter'" | wireshark -k -i -
