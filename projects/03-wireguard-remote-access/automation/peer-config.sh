#!/usr/bin/env bash
# Build a WireGuard client config for a peer. The peer generates their OWN private key;
# this file contains a placeholder for it. Private keys never travel.
# Usage: ./peer-config.sh <peer-name> <tunnel-ip> <server-public-key> <endpoint-host[:port]>
#   ./peer-config.sh friend-sam 10.10.99.11 'AbC...=' myhome.duckdns.org
set -euo pipefail

if [[ $# -lt 4 ]]; then sed -n '2,5p' "$0"; exit 1; fi
name="$1"; ip="$2"; server_pub="$3"; endpoint="$4"
[[ "$endpoint" == *:* ]] || endpoint="$endpoint:51820"

if [[ ! "$ip" =~ ^10\.10\.99\.([0-9]{1,3})$ ]] || (( BASH_REMATCH[1] < 2 || BASH_REMATCH[1] > 254 )); then
  echo "Tunnel IP must be in 10.10.99.2-254" >&2; exit 1
fi

out="${name}.conf.example"
cat > "$out" <<CONF
# WireGuard config for $name, generated $(date +%F)
# 1. Generate your key pair ON THIS DEVICE:   wg genkey | tee $name.key | wg pubkey > $name.pub
# 2. Send ONLY $name.pub to the lab admin.
# 3. Paste the contents of $name.key below, rename this file to $name.conf, import it.
[Interface]
PrivateKey = <PASTE-YOUR-PRIVATE-KEY-HERE>
Address = $ip/32

[Peer]
PublicKey = $server_pub
Endpoint = $endpoint
# Split tunnel: only lab traffic uses the VPN. Your normal internet is unaffected.
AllowedIPs = 10.10.0.0/16
PersistentKeepalive = 25
CONF

echo "Wrote $out"
echo
echo "OPNsense → VPN → WireGuard → Peers → +"
echo "  Name:        $name"
echo "  Public key:  <the .pub the peer sends you>"
echo "  Allowed IPs: $ip/32"
echo "  Instance:    wg-lab"
echo
echo "Then add the peer to your peer register (name, IP, date added, expiry). No keys in git."
