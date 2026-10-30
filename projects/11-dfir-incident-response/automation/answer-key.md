# Answer Key: Project 11 simulated incident

| # | Artifact | Where it's found | ATT&CK |
|---|---|---|---|
| 1 | Brute force then successful login as `webdev` from `10.10.20.77` | `/var/log/auth.log` / journal (`sshd` lines) | T1110.001, T1078 |
| 2 | Recon + staging commands, then `history -c` attempt | `/home/webdev/.bash_history` (with `#epoch` timestamps) | T1033, T1082, T1070.003 |
| 3 | Staged "tool" in hidden dir `/var/tmp/.cache-x/` (marker `HOMELAB-IR-0001`) | filesystem, `find / -name '.*' -path '*tmp*'` | T1105, T1564.001 |
| 4 | Backdoor account `sysupdate` in the `sudo` group | `/etc/passwd`, `/etc/group` | T1136.001, T1098 |
| 5 | Persistence: `sys-healthcheck.service` + `.timer` | `/etc/systemd/system/`, `systemctl list-timers` | T1053.006 |
| 6 | Root SSH key with comment `attacker@kali` | `/root/.ssh/authorized_keys` | T1098.004 |
| 7 | Timestomping: `tool` mtime set to 2026-01-01 03:14 | `stat` shows ctime/birth **newer** than mtime | T1070.006 |

Key teaching points:
- The `history -c` was *in* the history file because bash wrote the file on exit before/after.
  Clearing in-memory history doesn't erase what was already saved.
- Timestomping changes mtime/atime but `touch` can't set **ctime** (or birth time) from user
  space, so ctime newer than mtime is a red flag.
- IOCs: IP `10.10.20.77`, user `sysupdate`, path `/var/tmp/.cache-x/`, key comment `attacker@kali`,
  unit `sys-healthcheck`.

Containment/eradication: disable `webdev` and `sysupdate`, remove the key, disable and delete
the timer/service, remove the staged directory, rotate credentials, block the source IP, and
(in real life) rebuild from a known-good image.
