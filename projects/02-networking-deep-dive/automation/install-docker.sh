#!/usr/bin/env bash
# Run INSIDE lab-docker with the TARGETS TEMP egress rule enabled. Disable it afterwards!
set -euo pipefail
sudo apt-get update
sudo apt-get install -y qemu-guest-agent tcpdump tshark docker.io docker-compose-v2 curl
sudo systemctl enable --now qemu-guest-agent docker
sudo usermod -aG docker "${SUDO_USER:-$USER}"
# Pre-pull images used in later projects so the VM works offline afterwards
for img in traefik/whoami bkimminich/juice-shop ghcr.io/digininja/dvwa:latest docker.io/library/mariadb:10; do
  sudo docker pull "$img"
done
sudo docker run -d --name whoami -p 80:80 --restart unless-stopped traefik/whoami
echo "Done. Log out/in for docker group. NOW DISABLE THE TEMP EGRESS RULE."
