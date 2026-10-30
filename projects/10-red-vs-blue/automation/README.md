# ⚠️ Solution: use only if stuck

| File | Run where | What it does |
|---|---|---|
| `competition.yaml` | scoring VM, `~/se/bin/competition.yaml` | scoringengine config: white/red/blue teams, scored SSH + HTTP per blue box |
| `reset-game.sh` | Proxmox host | Rolls every blue box back to the `game-start` snapshot |
| `python/service_check.py` | anywhere on LAB-MGMT | Python exercise: concurrent uptime checker + CSV log |

Change every password in `competition.yaml` before game night.
