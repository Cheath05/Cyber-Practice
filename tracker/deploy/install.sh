#!/usr/bin/env bash
# Install the tracker as a systemd service on the Ubuntu server.
# Usage (from the repo checkout, as your normal user with sudo rights):
#   tracker/deploy/install.sh [--port 8002] [--with-pull-timer] [--serve-port 10000]
# It never touches ports 8000/8001 (Cardinal, Footsim) or their tailscale serve entries.
set -euo pipefail

PORT=8002
SERVE_PORT=10000
PULL_TIMER=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --serve-port) SERVE_PORT="$2"; shift 2 ;;
    --with-pull-timer) PULL_TIMER=1; shift ;;
    *) echo "unknown option $1" >&2; exit 1 ;;
  esac
done

TRACKER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$TRACKER/.." && pwd)"
RUN_USER="${SUDO_USER:-$USER}"
[[ "$RUN_USER" != "root" ]] || { echo "Run as your normal user (the script uses sudo where needed)." >&2; exit 1; }

case "$PORT" in 8000|8001) echo "Port $PORT is used by Cardinal/Footsim. Pick another." >&2; exit 1 ;; esac
case "$SERVE_PORT" in 443|8443) echo "Tailscale HTTPS port $SERVE_PORT is used by Cardinal/Footsim. Pick another." >&2; exit 1 ;; esac
if ss -ltn "sport = :$PORT" | grep -q LISTEN && ! systemctl is-active --quiet cyber-tracker; then
  echo "Something is already listening on port $PORT. Pick another with --port." >&2; exit 1
fi

echo "[1/4] Python virtualenv in $TRACKER/.venv"
python3 -m venv "$TRACKER/.venv"
"$TRACKER/.venv/bin/pip" install --quiet --upgrade pip
"$TRACKER/.venv/bin/pip" install --quiet -r "$TRACKER/requirements.txt"

render() {  # render <template> <dest>
  sed -e "s|@USER@|$RUN_USER|g" -e "s|@REPO@|$REPO|g" -e "s|@TRACKER@|$TRACKER|g" -e "s|@PORT@|$PORT|g" "$1" \
    | sudo tee "$2" >/dev/null
}

echo "[2/4] systemd service (127.0.0.1:$PORT)"
render "$TRACKER/deploy/cyber-tracker.service" /etc/systemd/system/cyber-tracker.service
if [[ "$PULL_TIMER" == 1 ]]; then
  render "$TRACKER/deploy/cyber-tracker-pull.service" /etc/systemd/system/cyber-tracker-pull.service
  sudo cp "$TRACKER/deploy/cyber-tracker-pull.timer" /etc/systemd/system/cyber-tracker-pull.timer
fi
sudo systemctl daemon-reload
sudo systemctl enable --now cyber-tracker.service
if [[ "$PULL_TIMER" == 1 ]]; then sudo systemctl enable --now cyber-tracker-pull.timer; fi

echo "[3/4] Health check"
for _ in $(seq 1 15); do
  if curl -fsS "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS "http://127.0.0.1:$PORT/healthz" && echo

echo "[4/4] Tailscale (tailnet only, NOT funnel). Current serve config:"
sudo tailscale serve status || true
echo
echo "To publish it on your tailnet at https://<this-machine>.<tailnet>.ts.net:$SERVE_PORT run:"
echo "  sudo tailscale serve --bg --https=$SERVE_PORT http://127.0.0.1:$PORT"
echo "Optional: restrict to your Tailscale login:"
echo "  echo 'CT_ALLOWED_LOGINS=you@example.com' | sudo tee /etc/cyber-tracker.env && sudo systemctl restart cyber-tracker"
