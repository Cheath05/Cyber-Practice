# Answer Key: Project 05 Windows Practice Image

> Spoilers. Authors only, or after you've competed.

| # | Item | Find it with | Fix | aeacus check | Mapping |
|---|---|---|---|---|---|
| 1 | Unauthorized admin `helpdesk2` | `Get-LocalGroupMember Administrators` vs README | `Remove-LocalUser helpdesk2` | `UserExistsNot` | CIS 1.x / T1136.001 |
| 2 | `jlee` is an admin but should be standard | same | `Remove-LocalGroupMember Administrators jlee` | `UserInGroupNot` | T1078 |
| 3 | Guest enabled | `Get-LocalUser Guest` | `Disable-LocalUser Guest` | `SecurityPolicy EnableGuestAccount 0` | CIS 2.3.1 |
| 4 | Weak password/lockout policy | `net accounts` | `net accounts /minpwlen:12 /maxpwage:90 /lockoutthreshold:5` (or secpol) | `SecurityPolicy` ×3 | CIS 1.1, 1.2 |
| 5 | Logon auditing off | `auditpol /get /subcategory:"Logon"` | `auditpol /set /subcategory:"Logon" /success:enable /failure:enable` | `CommandContains` | CIS 17.5 |
| 6 | Firewall off | `Get-NetFirewallProfile` | `Set-NetFirewallProfile -All -Enabled True` | `FirewallUp` | CIS 9 |
| 7 | RDP without NLA | System Properties → Remote | tick "Allow connections only … with NLA" | `RegistryKey UserAuthentication 1` | T1021.001 |
| 8 | SMBv1 enabled | `Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol` | `Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol` | `WindowsFeatureNot` | CIS 18.3 |
| 9 | Share `Files` (Everyone: Full) | `Get-SmbShare` | `Remove-SmbShare Files` | `ShareExistsNot` | T1039 |
| 10 | Remote Registry running | `Get-Service RemoteRegistry` | Stop + Disabled | `ServiceStartup disabled` | CIS 5.x |
| 11 | Scheduled task `Updater` (SYSTEM, at logon) | Task Scheduler / `Get-ScheduledTask` | `Unregister-ScheduledTask Updater` | `ScheduledTaskExistsNot` | T1053.005 |
| 12 | Run key `OneDriveHelper` | `Get-ItemProperty HKLM:\...\Run` | `Remove-ItemProperty` | `RegistryKeyExistsNot` | T1547.001 |
| 13 | Defender exclusion `C:\Users\Public` | `Get-MpPreference \| select ExclusionPath` | `Remove-MpPreference -ExclusionPath C:\Users\Public` | `CommandContainsNot` | T1562.001 |
| 14 | UAC silent elevation | secpol → UAC: Behavior of the elevation prompt | set to "Prompt for consent" | `RegistryKeyNot ConsentPromptBehaviorAdmin 0` | CIS 2.3.17 |
| 15 | LM hashes stored | secpol → Network security: Do not store LAN Manager hash | Enabled | `RegistryKey NoLMHash 1` | CIS 2.3.11 |
| 16 | Anonymous SAM enumeration | secpol → Network access: Do not allow anonymous enumeration of SAM accounts | Enabled | `RegistryKey RestrictAnonymousSAM 1` | CIS 2.3.10 |
| 17 | Prohibited media file | `Get-ChildItem C:\Users -Recurse -Include *.mp3` | delete | `PathExistsNot` | policy |
| 18 | Plaintext passwords on Desktop | look around! | delete, rotate those creds | `PathExistsNot` | T1552.001 |

Forensic answers: Q1 `Updater` · Q2 `C:\Users\Public` · Q3 `helpdesk2`

Penalties: deleting `svc_print` (authorized service account) · disabling RDP entirely
(the README says it's required; secure it with NLA instead).

Common competitor mistakes this image is designed to catch:
- Disabling RDP to "fix" item 7 → penalty. Read the README.
- Deleting `svc_print` because "svc accounts look suspicious".
- Fixing item 13 before answering forensic Q2 (the evidence is gone).
