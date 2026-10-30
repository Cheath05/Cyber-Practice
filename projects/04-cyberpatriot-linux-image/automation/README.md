# ⚠️ Solution: use only if stuck

**This folder is an answer key.** If you plan to compete on this exact image, don't read it.
Build your own image with different vulnerabilities instead.

| File | What it does |
|---|---|
| `plant-vulns.sh` | Plants ~20 misconfigurations, noise, and 3 forensic questions on a fresh Ubuntu 24.04 VM (cp-linux only) |
| `install-aeacus.sh` | Downloads aeacus into `/opt/aeacus` and copies the config (TEMP egress needed) |
| `aeacus/scoring.conf` | aeacus checks for every planted item + penalties |
| `aeacus/ReadMe.conf` | Competitor README: scenario, authorized users, critical services |
| `answer-key.md` | Every item: how it was planted, how to find it, how to fix it, CIS / ATT&CK mapping, plus the SUID-PATH C exercise explained |
| `c/backup_helper_fixed.c` | The hardened "backup helper" (C exercise target) |
| `c/Makefile` | Builds the fixed helper |
| `python/linux_audit.py` | Python exercise: mini compliance scanner |
