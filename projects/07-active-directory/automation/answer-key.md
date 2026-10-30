# Answer Key: Project 07 Active Directory

> Spoilers. The planted weaknesses from `02-populate-ad.ps1` and the exact fixes.

| # | Weakness | Attack it enables | Detection (P08) | Fix |
|---|---|---|---|---|
| 1 | `svc_sql` has an SPN and the weak password `Summer2026` | Kerberoasting: any domain user requests its service ticket and cracks it offline | Event 4769 with ticket encryption `0x17` (RC4) for `svc_sql`, often a burst from one user | 25+ char random password or a **gMSA**; enforce AES-only (`msDS-SupportedEncryptionTypes`); least privilege |
| 2 | `jmartin` has *Do not require Kerberos preauthentication* | AS-REP roasting: request an AS-REP without a password, crack offline | Event 4768 for that account with pre-auth type 0 | `Set-ADAccountControl jmartin -DoesNotRequirePreAuth $false` |
| 3 | `tgreen` description contains a password | Any user who can read AD (everyone) gets a credential | `Audit-AD.ps1` "password in description" | Clear the description, rotate the password, policy against secrets in attributes |
| 4 | `Helpdesk` nested in `Account Operators` | BloodHound path: rwhite → Helpdesk → Account Operators → can reset/abuse privileged accounts | 4728/4732/4756 (group changes); BloodHound | Remove the nesting; delegate only the specific rights help desk needs on the Staff OU |
| 5 | LLMNR/NBT-NS enabled (Windows default) | Responder poisoning captures NetNTLMv2 hashes on the same VLAN | Host-based: LLMNR traffic to a non-DNS host; 4648 anomalies | GPO *Turn off multicast name resolution*; disable NetBIOS over TCP/IP via DHCP option or adapter |
| 6 | SMB signing not required on ws01 (default for clients) | NTLM relay | NetExec `--gen-relay-list` shows signing: False | GPO *Microsoft network server: Digitally sign communications (always)* |
| 7 | No lockout policy (lab default may vary) | Password spraying | Many 4625 across many accounts from one source | Fine-grained/default lockout policy + monitoring 4625/4740 |

## Verification after hardening

- Re-run NetExec enumeration: SMB signing **True** on both hosts.
- `GetNPUsers` returns no roastable users.
- `GetUserSPNs` still lists `svc_sql` (that's by design!) but the new long password doesn't crack.
- Responder on VLAN 50 captures nothing when ws01 mistypes a share name.
- BloodHound "Shortest path to Domain Admins" from `rwhite` no longer exists.
- `Audit-AD.ps1` shows only the expected Info rows.
