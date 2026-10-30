#!/usr/bin/env bash
# Collect volatile state + key logs from a live Linux host into a hashed tarball (Project 11).
# Usage: sudo ./triage-collect.sh [case-id]      Output: /root/triage-<case>-<host>-<utc>.tar.gz
# Read-only on the system (writes only its output). Copy the tarball off the host afterwards.
set -uo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
case_id="${1:-case}"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="/root/triage-${case_id}-$(hostname)-${ts}"
mkdir -p "$out"

run() { local name="$1"; shift; { echo "# $(date -u +%FT%TZ) :: $*"; "$@"; } > "$out/$name.txt" 2>&1; }

# Most volatile first
run 01-date       date -u
run 02-network    ss -tulpanw
run 03-processes  ps auxwwf
run 04-logins     w
run 05-last       last -Faiw
run 06-ip         ip -d addr
run 07-routes     ip route
run 08-arp        ip neigh
run 09-mounts     findmnt
run 10-modules    lsmod
run 11-services   systemctl list-units --all --no-pager
run 12-timers     systemctl list-timers --all --no-pager
while IFS=: read -r u _; do
  crontab -l -u "$u" >> "$out/13-crontabs.txt" 2>/dev/null && echo "## ^ $u" >> "$out/13-crontabs.txt"
done < /etc/passwd
run 14-suid       find / -xdev -perm -4000 -type f
run 15-recent     find / -xdev -mtime -2 -type f -not -path '/proc/*' -not -path '/sys/*'

# Configuration and logs (copied, not moved)
mkdir -p "$out/files"
cp -a --parents /etc/passwd /etc/group /etc/sudoers /etc/sudoers.d /etc/crontab /etc/cron.d \
  /etc/systemd/system /var/log/auth.log /root/.ssh /home/*/.bash_history "$out/files/" 2>/dev/null
journalctl --no-pager -o short-iso > "$out/16-journal.txt" 2>/dev/null

tar -czf "$out.tar.gz" -C "$(dirname "$out")" "$(basename "$out")"
rm -rf "$out"
sha256sum "$out.tar.gz" | tee "$out.tar.gz.sha256"
echo "Record this hash in your chain-of-custody form, then copy both files off the host."
