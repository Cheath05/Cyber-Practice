#!/usr/bin/env bash
# Install Wazuh all-in-one (manager + indexer + dashboard) on the wazuh VM, then cap the heap.
# Usage: sudo WAZUH_MINOR=4.x ./install-wazuh.sh
#   WAZUH_MINOR is the "X.Y" in the quickstart's download URL
#   (https://packages.wazuh.com/<X.Y>/wazuh-install.sh). Copy it from the current quickstart page.
#   Agents must be the same or OLDER version than the manager, so use the newest release here.
set -euo pipefail
: "${WAZUH_MINOR:?Set WAZUH_MINOR to the version in the official quickstart URL, e.g. WAZUH_MINOR=4.12}"
HEAP="${HEAP:-1536m}"     # ~30% of a 5 GB VM; the default is often too large for this box

[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
mem_mb=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
(( mem_mb >= 4500 )) || echo "WARNING: only ${mem_mb} MiB RAM; Wazuh will struggle below ~5 GB."

cd /root
curl -sSfO "https://packages.wazuh.com/${WAZUH_MINOR}/wazuh-install.sh"
bash ./wazuh-install.sh -a --install-dependencies | tee /root/wazuh-install.log

echo "[*] Capping wazuh-indexer heap at ${HEAP}"
sed -i "s/^-Xms.*/-Xms${HEAP}/; s/^-Xmx.*/-Xmx${HEAP}/" /etc/wazuh-indexer/jvm.options
systemctl restart wazuh-indexer
systemctl is-active wazuh-manager wazuh-indexer wazuh-dashboard

echo
echo "Done. Admin credentials are at the end of /root/wazuh-install.log."
echo "All internal passwords: tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt"
echo "Store them in your password manager, then: shred -u /root/wazuh-install.log"
