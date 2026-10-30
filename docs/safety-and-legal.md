# Safety & Legal

## The isolation rules (non-negotiable)

1. **Vulnerable VMs live on VLANs 30/50 behind OPNsense.** Never attach them to `vmbr0`.
2. **TARGETS and AD have no internet by default.** The "⏱ build/update" egress rules stay
   *disabled* except while you're installing packages. Re-disable them right after. (A
   compromised target with internet access can become a bot that attacks real people.)
3. **No lab segment can reach `HOME_NET`** (your home LAN, your family's devices, the Proxmox
   GUI, prod-ubuntu). Test this in Project 01 and re-test after every firewall change.
4. **The only inbound port is WireGuard UDP 51820.** Never port-forward a vulnerable service,
   CTFd, or the OPNsense GUI to the internet.
5. **Vulnerable targets run in VMs, not LXC containers.** LXC shares the host kernel.
6. **Snapshots before exercises; restore after.** A box that's been attacked may have
   leftovers (backdoors from your friends!). Don't keep using it.
7. **Malware samples** (P11 PCAPs/memory images) stay inside the lab. Download them to an
   analysis VM, never to your daily laptop. Keep them in password-protected zips (`infected`
   is the industry-standard password).

## Legal basics

- **Only attack systems you own or have written permission to test.** Your lab, and the
  platforms in [resources](resources.md) within their rules, are fine. Your school network,
  your ISP, or "just scanning" a website are **not**. In the US, the Computer Fraud and Abuse
  Act (CFAA) applies even to "harmless" scanning without authorization, and schools take it
  seriously.
- **Friends attacking your lab:** you own it, so you authorize it. Put it in writing anyway
  with the Rules of Engagement template. It's good practice and sets the boundaries.
- **Friends' devices:** your WireGuard rules must make sure friends can only reach the lab, and
  that the lab can't reach *their* home networks either (WG peers are a one-way trust).
- **Windows licensing:** evaluation editions are licensed for evaluation/testing. Server is
  180 days and Windows 11 Enterprise is 90 days. When they expire, rebuild from your template
  (that's what Project 13 automates). Don't use pirated activators; they're malware magnets.
- **CyberPatriot:** the official competition images and scoring engine are the Air Force
  Association's property. Build your *own* practice images (Projects 04/05) and don't
  redistribute official competition material.
- **Your ISP's terms:** running a VPN endpoint for a few friends is normally fine. Check the
  terms if you plan anything bigger.

## Personal security of your homelab

- Change all default passwords (OPNsense root, Proxmox root, Wazuh admin) and store them in a
  password manager.
- Enable 2FA on the Proxmox GUI (Datacenter → Permissions → Two Factor) and OPNsense
  (System → Access → Servers → TOTP).
- Keep Proxmox and OPNsense updated (but update *before* a game night, not during).
- Back up the OPNsense config (System → Configuration → Backups) after every change. Recovering
  from a firewall lockout without a backup is painful.
- Revoke a friend's WireGuard peer when they're done (P03 covers this).

## Lockout recovery cheat sheet

| Problem | Fix |
|---|---|
| Locked out of OPNsense GUI by a firewall rule | Proxmox → OPNsense VM → Console → option `8` (shell) → `pfctl -d` (disables the packet filter temporarily) → fix the rule in the GUI → reboot (or `pfctl -e`) |
| Broke OPNsense interfaces | Console menu → `1) Assign interfaces` / `2) Set interface IP` |
| Broke `/etc/network/interfaces` on Proxmox | Use the physical console (keyboard + monitor) or restore `/etc/network/interfaces.bak` (always copy before editing) |
| Ran out of RAM and everything froze | `qm stop <vmid>` the biggest lab VM from the Proxmox shell; see the lab profiles |
| Disk full | `lvs` to see thin pool usage; delete old snapshots (`qm delsnapshot`) and unused ISOs |
