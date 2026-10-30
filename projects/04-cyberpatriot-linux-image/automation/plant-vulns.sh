#!/usr/bin/env bash
# plant-vulns.sh - create a CyberPatriot-style PRACTICE image (Project 04 solution/answer key).
#
# It introduces ~20 common misconfigurations plus harmless "noise" so a competitor can practise
# finding and fixing them. The backdoors here are deliberately INERT markers (they touch a file
# or run `true`/a benign listener), not real malware, so this script is a training fixture, not
# a weapon. You still have to find and remove them to score.
#
# RUN ONLY on your throwaway cp-linux practice VM. It refuses to run unless the hostname is
# 'cp-linux' and you confirm. Snapshot first.
set -euo pipefail

EXPECTED_HOST="cp-linux"
AUTH_USER="${AUTH_USER:-labadmin}"     # the authorized main user (do NOT break this one)

if [[ $EUID -ne 0 ]]; then echo "Run with sudo." >&2; exit 1; fi
if [[ "$(hostname)" != "$EXPECTED_HOST" ]]; then
  echo "Hostname is '$(hostname)', expected '$EXPECTED_HOST'. Refusing (safety guard)." >&2
  echo "Set it with: sudo hostnamectl set-hostname $EXPECTED_HOST   (practice VM only)" >&2
  exit 1
fi
read -r -p "This will intentionally WEAKEN this machine. Type 'PRACTICE' to continue: " ans
[[ "$ans" == "PRACTICE" ]] || { echo "Aborted."; exit 1; }

echo "[*] 1 hidden UID-0 account 'svcadm'"
useradd -o -u 0 -g 0 -M -d /root -s /bin/bash svcadm 2>/dev/null || true
echo 'svcadm:Password1' | chpasswd

echo "[*] 2 NOPASSWD sudoers drop-in"
echo 'guest ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/90-guest
chmod 440 /etc/sudoers.d/90-guest

echo "[*] 3 unauthorized + weak users (noise: 'webmaster' IS authorized per README)"
for u in guest webmaster backupsvc; do id "$u" >/dev/null 2>&1 || useradd -m -s /bin/bash "$u"; done
echo 'guest:guest' | chpasswd
usermod -aG sudo guest                                  # 12: unauthorized sudo member

echo "[*] 4 empty-password account"
id operator >/dev/null 2>&1 || useradd -m -s /bin/bash operator
passwd -d operator

echo "[*] 3b allow root SSH login via drop-in"
mkdir -p /etc/ssh/sshd_config.d
printf 'PermitRootLogin yes\nPasswordAuthentication yes\n' > /etc/ssh/sshd_config.d/99-weak.conf

echo "[*] 5 weak password policy"
sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS\t99999/' /etc/login.defs
sed -i 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS\t0/' /etc/login.defs

echo "[*] 6 disable the firewall"
ufw --force disable 2>/dev/null || true

echo "[*] 8 world-writable /etc/passwd"
chmod 646 /etc/passwd

echo "[*] 9 cron 'backdoor' (INERT marker: just touches a file)"
cat > /etc/cron.d/0update-check <<'CRON'
* * * * * root /usr/bin/touch /var/run/.update-marker
CRON

echo "[*] 10 profile.d persistence (INERT marker)"
echo '/usr/bin/true  # left by former contractor' > /etc/profile.d/zz-maint.sh

echo "[*] 13 turn off automatic updates"
printf 'APT::Periodic::Update-Package-Lists "0";\nAPT::Periodic::Unattended-Upgrade "0";\n' \
  > /etc/apt/apt.conf.d/20auto-upgrades

echo "[*] 14 enable IP forwarding"
sed -i '/net.ipv4.ip_forward/d' /etc/sysctl.conf
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
sysctl -p >/dev/null 2>&1 || true

echo "[*] 15 benign 'rogue' service on tcp/4444 (competitor must find & disable it)"
cat > /etc/systemd/system/sysmon.service <<'UNIT'
[Unit]
Description=System Monitor
[Service]
# INERT: a harmless listener, not a shell. The point is to notice an unexpected service/port.
ExecStart=/bin/sh -c 'while true; do echo ok | nc -l -p 4444 -q1 || sleep 2; done'
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now sysmon.service 2>/dev/null || true

echo "[*] 11 SUID PATH-hijack 'backup-helper' (build the vulnerable C yourself per answer-key.md)"
echo "    Place it at /usr/local/bin/backup-helper, then: chown root:root && chmod 4755"

echo "[*] forensic questions on ${AUTH_USER}'s Desktop"
DESK="/home/${AUTH_USER}/Desktop"; mkdir -p "$DESK"
cat > "$DESK/Forensic Question 1.txt" <<'FQ'
A hidden account with root privileges (UID 0) was added to this system.
What is its username?
ANSWER:
FQ
cat > "$DESK/Forensic Question 2.txt" <<'FQ'
An unauthorized service is listening on a TCP port it should not be.
What port number is it?
ANSWER:
FQ
echo -n "V2VsbCBkb25lISBUaGUgZmxhZyBpczogQ1lCRVJQQVRJTw==" > "$DESK/Forensic Question 3.txt.b64"
cat > "$DESK/Forensic Question 3.txt" <<'FQ'
Decode the base64 in 'Forensic Question 3.txt.b64'. What does it say?
ANSWER:
FQ
chown -R "${AUTH_USER}:${AUTH_USER}" "$DESK"

echo
echo "[*] noise so competitors must READ the README:"
echo "    - 'webmaster' and 'backupsvc' ARE authorized. Removing them is a penalty."
echo "    - sshd and apache2 are CRITICAL services. Stopping them is a penalty."
echo
echo "Done. ~15 items planted; add more by hand to reach 20-25. Snapshot: qm snapshot <id> planted"
