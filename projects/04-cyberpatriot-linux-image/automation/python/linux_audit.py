#!/usr/bin/env python3
"""Mini Linux compliance scanner (Project 04 Python exercise, solution).

Checks a handful of hardening-baseline controls and prints PASS/FAIL with a score, the same
idea as aeacus, Lynis or OpenSCAP but small enough to read in one sitting.

    sudo python3 linux_audit.py [--allow-sudo labadmin] [--suid-allowlist suid.txt] [--json]

Run as root so /etc/shadow and `sshd -T` are readable. Read-only: it changes nothing.
"""
import argparse
import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path

# Typical SUID binaries on a stock Ubuntu 24.04 install. Anything else is suspicious.
DEFAULT_SUID = {
    "/usr/bin/passwd", "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/mount", "/usr/bin/umount",
    "/usr/bin/chsh", "/usr/bin/chfn", "/usr/bin/gpasswd", "/usr/bin/newgrp", "/usr/bin/fusermount3",
    "/usr/lib/openssh/ssh-keysign", "/usr/lib/dbus-1.0/dbus-daemon-launch-helper",
    "/usr/lib/polkit-1/polkit-agent-helper-1", "/usr/bin/pkexec",
}
SUID_SEARCH_DIRS = ["/usr/bin", "/usr/sbin", "/usr/local/bin", "/usr/local/sbin", "/bin", "/sbin",
                    "/usr/lib", "/opt", "/tmp", "/home"]


def run(cmd):
    """Run a command, return stdout ('' if it fails or is missing)."""
    if not shutil.which(cmd[0]):
        return ""
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return res.stdout


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def check_uid0():
    others = [l.split(":")[0] for l in (read("/etc/passwd") or "").splitlines()
              if l.count(":") >= 6 and l.split(":")[2] == "0" and not l.startswith("root:")]
    return not others, f"extra UID-0 accounts: {others}" if others else "only root has UID 0"


def check_empty_passwords():
    shadow = read("/etc/shadow")
    if shadow is None:
        return None, "cannot read /etc/shadow (run as root)"
    empty = [l.split(":")[0] for l in shadow.splitlines() if l.count(":") >= 1 and l.split(":")[1] == ""]
    return not empty, f"empty passwords: {empty}" if empty else "no empty passwords"


def check_sudo_members(allowed):
    group = run(["getent", "group", "sudo"]).strip()
    members = set(filter(None, group.split(":")[-1].split(","))) if group else set()
    extra = sorted(members - set(allowed))
    return not extra, f"unexpected sudo members: {extra}" if extra else f"sudo members ok: {sorted(members)}"


def check_nopasswd():
    hits = []
    for path in [Path("/etc/sudoers"), *Path("/etc/sudoers.d").glob("*")]:
        text = read(path) or ""
        if any("NOPASSWD" in l and not l.lstrip().startswith("#") for l in text.splitlines()):
            hits.append(str(path))
    return not hits, f"NOPASSWD in {hits}" if hits else "no NOPASSWD rules"


def check_ssh_root():
    out = run(["sshd", "-T"])
    if not out:
        return None, "sshd -T unavailable (not installed or not root)"
    m = re.search(r"^permitrootlogin\s+(\S+)", out, re.M)
    value = m.group(1) if m else "unknown"
    return value == "no", f"effective PermitRootLogin = {value}"


def check_firewall():
    out = run(["ufw", "status"])
    if not out:
        return None, "ufw not available"
    return "Status: active" in out, out.splitlines()[0] if out else "no output"


def check_pass_max_days():
    text = read("/etc/login.defs") or ""
    m = re.search(r"^\s*PASS_MAX_DAYS\s+(\d+)", text, re.M)
    days = int(m.group(1)) if m else None
    return (days is not None and days <= 90), f"PASS_MAX_DAYS = {days}"


def check_nullok():
    text = read("/etc/pam.d/common-auth") or ""
    bad = any("nullok" in l and not l.lstrip().startswith("#") for l in text.splitlines())
    return not bad, "nullok present in common-auth" if bad else "no nullok"


def check_passwd_perms():
    mode = os.stat("/etc/passwd").st_mode
    world_writable = bool(mode & stat.S_IWOTH)
    return not world_writable, f"/etc/passwd mode {stat.filemode(mode)}"


def check_suid(allowlist):
    found, seen = [], set()
    # /bin -> /usr/bin on modern distros: resolve real paths so nothing is counted twice
    for base in sorted({os.path.realpath(d) for d in SUID_SEARCH_DIRS if os.path.isdir(d)}):
        for root, _dirs, files in os.walk(base, onerror=lambda e: None):
            for name in files:
                p = os.path.realpath(os.path.join(root, name))
                if p in seen:
                    continue
                seen.add(p)
                try:
                    st = os.lstat(p)
                except OSError:
                    continue
                if stat.S_ISREG(st.st_mode) and st.st_mode & stat.S_ISUID and p not in allowlist:
                    found.append(p)
    return not found, f"unexpected SUID: {sorted(found)}" if found else "no unexpected SUID binaries"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--allow-sudo", nargs="*", default=["labadmin"], help="authorized sudo members")
    parser.add_argument("--suid-allowlist", help="file with one allowed SUID path per line")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    allow = set(DEFAULT_SUID)
    if args.suid_allowlist:
        allow |= {l.strip() for l in open(args.suid_allowlist, encoding="utf-8") if l.strip()}

    checks = [
        ("ACC-01", "No extra UID-0 accounts", check_uid0),
        ("ACC-02", "No empty passwords", check_empty_passwords),
        ("ACC-03", "Sudo group matches allowlist", lambda: check_sudo_members(args.allow_sudo)),
        ("ACC-04", "No NOPASSWD sudo rules", check_nopasswd),
        ("PWD-01", "PASS_MAX_DAYS <= 90", check_pass_max_days),
        ("PWD-02", "No nullok in PAM", check_nullok),
        ("NET-01", "SSH root login disabled", check_ssh_root),
        ("NET-02", "UFW firewall active", check_firewall),
        ("FIL-01", "/etc/passwd not world-writable", check_passwd_perms),
        ("FIL-02", "No unexpected SUID binaries", lambda: check_suid(allow)),
    ]
    results = []
    for cid, desc, fn in checks:
        ok, detail = fn()
        results.append({"id": cid, "control": desc, "result": {True: "PASS", False: "FAIL", None: "SKIP"}[ok],
                        "detail": detail})

    if args.json:
        print(json.dumps(results, indent=2))
        return
    scored = [r for r in results if r["result"] != "SKIP"]
    passed = sum(r["result"] == "PASS" for r in scored)
    for r in results:
        print(f"{r['result']:<4}  {r['id']}  {r['control']:<32} {r['detail']}")
    print(f"\nScore: {passed}/{len(scored)} controls passed")


if __name__ == "__main__":
    main()
