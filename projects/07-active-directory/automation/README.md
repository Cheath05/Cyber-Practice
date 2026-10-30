# ⚠️ Solution: use only if stuck

Build/defend automation lives here. **No attack tooling is shipped** — the attacks in Part B use
standard public tools (Impacket, NetExec, Responder, BloodHound) exactly as their own docs and
[The Hacker Recipes](https://www.thehacker.recipes/ad/) describe. The point is to learn them, so
work through those rather than running a script.

| File | Run where | What it does |
|---|---|---|
| `01-build-dc.ps1` | dc01 (elevated) | Installs AD DS and promotes a new `lab.local` forest |
| `02-populate-ad.ps1` | dc01 (elevated, after reboot) | Creates OUs, users, groups, and the intentional training weaknesses |
| `Audit-AD.ps1` | dc01 or any domain box with RSAT | Read-only AD hygiene audit → objects/CSV |
| `answer-key.md` | — | The planted weaknesses and their exact fixes |
| `python/kerberoast_watch.py` | anywhere | Flags RC4 Kerberoasting in exported 4769 events |

The `.ps1` files were written and reviewed by hand but not executed in CI (no Windows runner).
Test them in a snapshot and note issues in your WORKLOG.
