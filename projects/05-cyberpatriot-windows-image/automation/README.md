# ⚠️ Solution: use only if stuck

**Answer key inside.** Don't read it if you'll compete on this exact image.

| File | Run where | What it does |
|---|---|---|
| `create-windows-vm.sh` | Proxmox host | Creates a UEFI + vTPM + VirtIO Windows VM ready for install (Win11 or Server 2022) |
| `plant-vulns.ps1` | cp-windows (elevated) | Plants ~20 misconfigurations, inert persistence, noise, 3 forensic questions |
| `aeacus/scoring.conf` | `C:\aeacus\` | Windows aeacus checks + penalties |
| `aeacus/ReadMe.conf` | `C:\aeacus\` | Competitor README |
| `answer-key.md` | — | Each item: plant / find / fix / check / mapping |
| `Audit-Windows.ps1` | any Windows | PowerShell exercise: 10-control audit → objects → CSV/JSON |
| `python/compare_audits.py` | anywhere | Python exercise: diff two audit JSON files |

The `.ps1` files were reviewed by hand but not executed in CI (no Windows/PowerShell runner).
Run them in a snapshot first and report anything that breaks in your WORKLOG.
