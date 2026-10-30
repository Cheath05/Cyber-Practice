#!/usr/bin/env bash
# Run INSIDE the Debian 12 Tailscale LXC (VMID 220, RED 10.10.20.20) as root.
# Host side first: add the two TUN lines to /etc/pve/lxc/220.conf and restart the container.
set -euo pipefail
[[ -e /dev/net/tun ]] || { echo "/dev/net/tun missing: fix the LXC config on the host"; exit 1; }
apt-get update && apt-get install -y curl
curl -fsSL https://tailscale.com/install.sh | sh
cat > /etc/sysctl.d/99-tailscale.conf <<SYSCTL
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
SYSCTL
sysctl -p /etc/sysctl.d/99-tailscale.conf
# SNAT (default) makes friends appear as 10.10.20.20 inside the lab, so RED's rules apply.
tailscale up --advertise-routes=10.10.30.0/24 --advertise-tags=tag:lab-router
echo "Approve the route in the Tailscale admin console if autoApprovers isn't set."
