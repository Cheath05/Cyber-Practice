#!/usr/bin/env bash
# Run INSIDE a lab VM to test the firewall matrix (docs/network-reference.md) from its segment.
# Usage: ./validate-isolation.sh <segment> <home-router-ip> <proxmox-ip>
#   segment: mgmt | red | targets | blue | ad
# Optional: test real hosts in other segments with PEERS="name=ip:port ..." where name is one of
#   mgmt red targets blue ad, e.g.
#   PEERS="targets=10.10.30.10:22 blue=10.10.40.10:1514 ad=10.10.50.10:445" ./validate-isolation.sh red 192.168.1.1 192.168.1.50
# Exits with the number of failed tests.
set -uo pipefail

SEG="${1:-}"; HOME_GW="${2:-}"; PVE="${3:-}"
if [[ -z "$SEG" || -z "$HOME_GW" || -z "$PVE" ]]; then
  sed -n '2,9p' "$0"; exit 2
fi

fails=0
# probe <description> <expect: allow|block> <command...>
probe() {
  local desc="$1" expect="$2"; shift 2
  local result
  if timeout 6 "$@" >/dev/null 2>&1; then result=allow; else result=block; fi
  if [[ "$result" == "$expect" ]]; then
    printf '  PASS  %-42s expected %-5s got %s\n' "$desc" "$expect" "$result"
  else
    printf '  FAIL  %-42s expected %-5s got %s\n' "$desc" "$expect" "$result"
    fails=$((fails + 1))
  fi
}
# TCP connect test without needing nc. It must be a real command (not a function) because
# `timeout` can only run executables: usage  probe ... "${TCP[@]}" <host> <port>
# shellcheck disable=SC2016  # $0/$1 are expanded by the inner bash, on purpose
TCP=(bash -c 'exec 3<>"/dev/tcp/$0/$1"')

# Expected reachability of *hosts* in each destination segment, from each source segment.
# Wazuh agent ports (1514/1515) to BLUE are the one exception for targets/ad (handled below).
expect_for() {
  local src="$1" dst="$2"
  case "$src:$dst" in
    mgmt:*) echo allow ;;
    red:targets|red:ad|red:red) echo allow ;;
    blue:red|blue:targets|blue:ad|blue:blue) echo allow ;;
    targets:targets|ad:ad) echo allow ;;
    *) echo block ;;
  esac
}

case "$SEG" in
  mgmt)    gw=10.10.10.1; inet=allow; fwgui=allow ;;
  red)     gw=10.10.20.1; inet=allow; fwgui=block ;;
  targets) gw=10.10.30.1; inet=block; fwgui=block ;;
  blue)    gw=10.10.40.1; inet=allow; fwgui=block ;;
  ad)      gw=10.10.50.1; inet=block; fwgui=block ;;
  *) echo "unknown segment $SEG"; exit 2 ;;
esac

echo "Testing from segment: $SEG"
probe "own gateway ping ($gw)"            allow  ping -c1 -W2 "$gw"
probe "DNS via own gateway"               allow  dig +time=3 +tries=1 +short example.com "@$gw"
probe "internet (1.1.1.1:443)"            "$inet" "${TCP[@]}" 1.1.1.1 443
probe "firewall GUI ($gw:443)"            "$fwgui" "${TCP[@]}" "$gw" 443
probe "home router ($HOME_GW)"            block  ping -c1 -W2 "$HOME_GW"
probe "Proxmox GUI ($PVE:8006)"           block  "${TCP[@]}" "$PVE" 8006

for peer in ${PEERS:-}; do
  name="${peer%%=*}"; hostport="${peer#*=}"; host="${hostport%%:*}"; port="${hostport##*:}"
  exp="$(expect_for "$SEG" "$name")"
  if [[ "$name" == "blue" && ( "$SEG" == "targets" || "$SEG" == "ad" ) && ( "$port" == "1514" || "$port" == "1515" ) ]]; then
    exp=allow   # TARGETS and AD may send agent traffic to Wazuh
  fi
  probe "$name host $host:$port"          "$exp" "${TCP[@]}" "$host" "$port"
done

echo
if (( fails == 0 )); then echo "All tests passed."; else echo "$fails test(s) FAILED. Check firewall rules/logs."; fi
exit "$fails"
