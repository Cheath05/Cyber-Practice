#!/usr/bin/env bash
# Install aeacus into /opt/aeacus on the practice VM (TARGETS TEMP egress must be ON).
# Usage: sudo ./install-aeacus.sh [release-zip-url]
# If the asset name changes, grab the Linux zip from https://github.com/elysium-suite/aeacus/releases
set -euo pipefail
url="${1:-https://github.com/elysium-suite/aeacus/releases/latest/download/aeacus-linux.zip}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
apt-get install -y unzip curl >/dev/null
tmp="$(mktemp -d)"
curl -fL -o "$tmp/aeacus.zip" "$url"
mkdir -p /opt/aeacus
unzip -o "$tmp/aeacus.zip" -d /opt/aeacus >/dev/null
# Some release zips contain a top-level folder; flatten it if so.
if [[ ! -x /opt/aeacus/aeacus ]] && compgen -G "/opt/aeacus/*/aeacus" >/dev/null; then
  mv /opt/aeacus/*/* /opt/aeacus/ 2>/dev/null || true
fi
chmod +x /opt/aeacus/aeacus
cp "$here/aeacus/scoring.conf" "$here/aeacus/ReadMe.conf" /opt/aeacus/
cd /opt/aeacus
./aeacus --verbose check
echo "Installed. Next: ./aeacus --verbose score   (then disable TEMP egress)"
