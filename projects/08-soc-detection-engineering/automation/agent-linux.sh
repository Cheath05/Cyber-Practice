#!/usr/bin/env bash
# Install and enroll a Wazuh agent on a Debian/Ubuntu lab endpoint (TEMP egress ON while running).
# Usage: sudo ./agent-linux.sh [manager-ip] [agent-group]
set -euo pipefail
MANAGER="${1:-10.10.40.10}"
GROUP="${2:-default}"
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }

apt-get install -y gnupg curl auditd
if [[ ! -f /usr/share/keyrings/wazuh.gpg ]]; then
  curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH \
    | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import
  chmod 644 /usr/share/keyrings/wazuh.gpg
fi
grep -qs packages.wazuh.com /etc/apt/sources.list.d/wazuh.list || \
  echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
    > /etc/apt/sources.list.d/wazuh.list
apt-get update
WAZUH_MANAGER="$MANAGER" WAZUH_AGENT_GROUP="$GROUP" apt-get install -y wazuh-agent
# Pin the agent so a routine apt upgrade can't make it newer than the manager
apt-mark hold wazuh-agent

# Collect auditd logs too
if ! grep -q '/var/log/audit/audit.log' /var/ossec/etc/ossec.conf; then
  sed -i 's#</ossec_config>#  <localfile>\n    <log_format>audit</log_format>\n    <location>/var/log/audit/audit.log</location>\n  </localfile>\n</ossec_config>#' /var/ossec/etc/ossec.conf
fi
# A few useful audit rules (identity files, sudoers, root command execution)
cat > /etc/audit/rules.d/50-lab.rules <<'RULES'
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers
-a always,exit -F arch=b64 -F euid=0 -S execve -k root_cmd
RULES
augenrules --load || true

systemctl daemon-reload
systemctl enable --now wazuh-agent auditd
echo "Agent installed. Check it shows Active in the dashboard. Now DISABLE the TEMP egress rule."
