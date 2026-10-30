# Similar Projects & How This Curriculum Compares

Researched October 2026. These are reputable, widely used projects that overlap with this
repo. Use them as second opinions, alternative instructions when you're stuck, or "next level"
challenges. Where they had a better idea, it's already folded into the matching project.

## Lab platforms (automated ranges)

| Project | What it is | vs. this repo | Fits 16 GB? |
|---|---|---|---|
| [Ludus](https://docs.ludus.cloud/) (Bad Sector Labs) | Builds whole Proxmox ranges from one config file, with WireGuard access | P13 teaches the same ideas by hand (Terraform + Ansible) | ❌ Needs ~32 GB per range |
| [GOAD](https://github.com/Orange-Cyberdefense/GOAD) (Orange Cyberdefense) | Multi-domain vulnerable AD lab | P07 is a smaller, build-it-yourself version; GOAD-Mini/Light is the P07 stretch goal | ⚠️ Mini/Light only, with everything else off |
| [DetectionLab](https://github.com/clong/DetectionLab) (Chris Long) | Classic AD + logging lab | **Retired since 2023**: don't follow it. P07 + P08 cover the same ground | — |
| [Splunk Attack Range](https://attack-range.readthedocs.io/) | Builds an instrumented lab, simulates attacks, and ships data to Splunk | Same idea as the P08 purple team; it now targets the cloud | ❌ Cloud-oriented |
| [CISA Logging Made Easy (LME)](https://github.com/cisagov/LME) | Free government-built log management (Wazuh + Elastic) for small orgs | P08 uses plain Wazuh (lighter). LME is a P08 stretch comparison | ⚠️ Heavier than Wazuh alone |
| [SCALE 23x homelab workshop](https://www.socallinuxexpo.org/sites/default/files/2026-03/Self-hosting%20a%20Secure%20Home%20Lab%20Book.pdf) ([code](https://github.com/henryreed/scale23x-homelab-workshop)) | Conference workbook: Proxmox, OPNsense, AdGuard Home | Very close to P01–P02; a good second set of instructions | ✅ |

## Guided learning paths

| Project | vs. this repo |
|---|---|
| [MyDFIR](https://www.youtube.com/@MyDFIR) *30-Day SOC Challenge* and *SOC Automation Project* (Wazuh + Shuffle + TheHive) | Same skills as P08; the SOAR part is a P08 stretch goal |
| [soc-roadmap-2026](https://github.com/Ak-cybe/soc-roadmap-2026) | A 16–20 week SOC study plan ending in Sigma detections; complements P08 + the schedule |
| [TCM Security](https://academy.tcm-sec.com/) PEH/PJPT AD lab | Same AD attack set as P07 (paid course, free YouTube content) |
| [TryHackMe SOC Level 1](https://tryhackme.com/path/outline/soclevel1) / [HTB Academy](https://academy.hackthebox.com/) | Guided theory to pair with P02, P06, P07, P08 |

## Tools adopted from this research

| Tool | Added to | Why |
|---|---|---|
| [PingCastle](https://www.pingcastle.com/) / [Purple Knight](https://www.purple-knight.com/) | P07 Part C | Measurable before/after AD risk score |
| AD CS + [Locksmith](https://github.com/jakehildreth/Locksmith) | P07 Part D | Certificate-template abuse (ESC1) is a top modern AD attack path most labs skip |
| Wazuh CDB lists + [abuse.ch](https://abuse.ch/) feeds | P08 step 8b | Threat-intel matching is a core SOC task |
| [MITRE Caldera](https://caldera.mitre.org/), [Shuffle](https://shuffler.io/) | P08 stretch | Automated adversary emulation; SOAR |
| [Velociraptor](https://docs.velociraptor.app/) | P11 | The open-source DFIR platform IR teams actually use |
| [OWASP DefectDojo](https://github.com/DefectDojo/django-DefectDojo) | P12 stretch | Industry vuln-management platform |
| [NVIDIA garak](https://github.com/NVIDIA/garak), [Microsoft PyRIT](https://github.com/Azure/PyRIT) | P14 | Industry LLM red-teaming tools to compare with your harness |

## Competitions (see the calendar in [schedule](schedule.md#competitions--events-calendar))

| Event | Who | Why it matters |
|---|---|---|
| [National Cyber League (NCL)](https://nationalcyberleague.org/) | US/Canadian students | Individual + team CTF with a personalized scouting report you can put on a resume |
| [NCAE Cyber Games](https://www.caecommunity.org/ncae-cybergames) | First-time competitors at NCAE-C designated schools | Beginner-friendly red/blue + CTF; on-ramp to CCDC |
| [CCDC](https://www.nationalccdc.org/) | College teams | The defense competition P10 imitates |
| [TryHackMe Advent of Cyber](https://tryhackme.com/) | Anyone, free, every December | 24 short daily labs; great during finals week |
| [SANS Holiday Hack Challenge](https://www.sans.org/holidayhack) | Anyone, free | Story-driven CTF; write-ups make good portfolio pieces |
