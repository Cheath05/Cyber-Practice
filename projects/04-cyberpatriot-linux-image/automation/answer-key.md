# Answer Key: Project 04 CyberPatriot Linux Image

> Spoilers. Read only if you're the author or you've finished competing.

Each row: how `plant-vulns.sh` creates the issue, how a competitor finds it, how aeacus scores
it, and the CIS / MITRE mapping.

| # | Vulnerability | Plant | Find | aeacus check | CIS / ATT&CK |
|---|---|---|---|---|---|
| 1 | Hidden UID-0 account `svcadm` | `useradd -o -u 0` | `awk -F: '$3==0' /etc/passwd` | `UserExistsNot user=svcadm` | 6.2 / T1136.001 |
| 2 | `NOPASSWD` sudoers drop-in | `/etc/sudoers.d/90-guest` | `grep -r NOPASSWD /etc/sudoers*` | `DirContainsNot /etc/sudoers.d/ NOPASSWD` | 5.3 / T1548.003 |
| 3 | Root SSH login allowed | `/etc/ssh/sshd_config.d/99-weak.conf` | `sshd -T \| grep -i permitroot` | `FileContainsNot` on the drop-in, `PathExistsNot` passoverride | 5.2 / T1021.004 |
| 4 | Empty-password account `operator` | `passwd -d operator` | `awk -F: '$2==""' /etc/shadow` | `FileContainsNot /etc/shadow 'operator::'` | 5.4 / T1078 |
| 5 | Weak password aging | `PASS_MAX_DAYS 99999` | read `/etc/login.defs` | `FileContainsRegex '^PASS_MAX_DAYS\s+([1-9]\|[1-8][0-9]\|90)$'` | 5.5.1 |
| 6 | UFW disabled | `ufw disable` | `ufw status` | `FirewallUp` | 4.1 |
| 7 | World-writable `/etc/passwd` | `chmod 646` | `ls -l /etc/passwd` | `PermissionIsNot value='????????w?'` | 6.1 |
| 8 | Cron persistence (inert) | `/etc/cron.d/0update-check` | `ls /etc/cron.d`, read each | `PathExistsNot` | T1053.003 |
| 9 | Profile persistence (inert) | `/etc/profile.d/zz-maint.sh` | read `/etc/profile.d/*` | `PathExistsNot` | T1546.004 |
| 10 | Unauthorized sudo member `guest` | `usermod -aG sudo guest` | `getent group sudo` | `UserInGroupNot`, `UserExistsNot` passoverride | 5.3 |
| 11 | Auto-updates off | `20auto-upgrades` set to 0 | read apt config | `AutoCheckUpdatesEnabled` | 1.2 |
| 12 | IP forwarding on | `/etc/sysctl.conf` | `sysctl net.ipv4.ip_forward` | `FileContainsNot 'net.ipv4.ip_forward=1'` | 3.1 |
| 13 | Rogue service on tcp/4444 | `sysmon.service` | `ss -lntp`, `systemctl list-units` | `ServiceUpNot name=sysmon` | T1543.002 |
| 14 | SUID backup-helper (C exercise) | you build + `chmod 4755` | `find / -perm -4000 -type f` | `PermissionIsNot value='???s??????'`, `PathExistsNot` passoverride | T1548.001 |
| 15 | Unauthorized user `guest` | `useradd guest` | compare `/etc/passwd` to README | (combined with #10) | 5.x |
| 16–25 | **Add your own**: prohibited software, media files, Apache `Options Indexes`, `ServerTokens`, pwquality minlen, `nullok`, syncookies, world-writable dirs | | | | |

Penalties (negative points): removing an authorized admin, stopping SSH (critical service),
stopping Apache (critical service).

Forensic questions and answers:
- Q1: hidden root account username → `svcadm` (find via UID-0 scan).
- Q2: the port the backdoor listens on → read the planted unit / `ss -lntp`.
- Q3: base64 string on the Desktop decodes to → `base64 -d` gives "Well done! The flag is: CYBERPATIO".

## The SUID PATH-hijack C exercise (item 11), explained

The intentionally weak "backup helper" is made SUID root and runs, in effect:

```c
setuid(0);                                   /* the admin's "make it work" hack */
system("tar -czf /tmp/backup.tgz /home");    /* RELATIVE "tar" + inherited PATH = the bug */
```

`system()` runs `/bin/sh -c "..."`, and the shell finds `tar` using **the caller's `$PATH`**.
Because the process runs as root, a competitor who puts their own `tar` earlier in `PATH` gets
that script executed as root. The lesson: a SUID binary must never trust `PATH`, the
environment, or a shell. The hardened rewrite is `c/backup_helper_fixed.c` (absolute path,
`execve`, fixed environment, ideally not SUID at all).

Write the vulnerable version yourself from the two-line pattern above to see it work on
cp-linux; the fix is the deliverable that matters.
