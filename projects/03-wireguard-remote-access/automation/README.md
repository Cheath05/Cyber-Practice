# ⚠️ Solution: use only if stuck

| File | What it does |
|---|---|
| `peer-config.sh` | Builds a client `.conf` for a peer **without** a private key (the peer pastes their own) and prints the OPNsense peer fields |
| `client.conf.example` | Annotated split-tunnel client config |
| `rule-matrix.md` | WG_FRIENDS rules + troubleshooting table |
| `tailscale/acl.hujson` | Tailscale ACL: admins → everything, friends → TARGETS + scoreboard |
| `tailscale/lxc-setup.sh` | Commands to run inside the Tailscale LXC |
| `python/wg_status.py` | Python exercise: parse `wg show all dump`, flag stale peers |
| `python/peers.csv.example` | Peer register format used by `wg_status.py` (public keys only) |
