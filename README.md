# Cyber-Practice

A hands-on cybersecurity curriculum built for **one small Proxmox homelab**: a Dell OptiPlex
7070 Micro with 16 GB RAM and 256 GB of disk. It has 14 projects. Each one teaches a core
security skill, produces **professional documentation** you can show employers, and fits on
modest hardware.

Built for a college student aiming for **Summer 2027 cybersecurity internships** who hasn't
picked a specialty yet. The projects cover networking, SOC/blue team, pentesting/red team,
Active Directory, DFIR, GRC, CyberPatriot-style image building, CTFs, and red-vs-blue games with
friends, so you can find out what you enjoy.

## How this repo works

1. **Start with [`docs/00-start-here.md`](docs/00-start-here.md).** It covers the resource
   budget, lab profiles, and how to use each project.
2. **Follow the guide** (`projects/NN-*/README.md`). Build things yourself; that's where the
   learning happens.
3. **Write as you go.** Keep a dated lab notebook in each project's `WORKLOG.md`.
4. **Produce the deliverables** listed in each project (network design doc, pentest report,
   detection rules, incident report…). Templates are in [`templates/`](templates/).
5. **Stuck?** Each project has an `automation/` folder marked **"Solution — use only if
   stuck"** with scripts, configs and answer keys.
6. A project is **done** when its *Definition of done* checklist is fully ticked.

## Roadmap & progress

The order follows [`docs/schedule.md`](docs/schedule.md). It front-loads the projects hiring
managers ask about most, so your resume improves during this application cycle.

| ✔ | # | Project | Main skill (career path) | Hours | Phase |
|---|---|---|---|---|---|
| ☐ | 01 | [Lab Foundation](projects/01-lab-foundation/) | Networking, virtualization, firewalls (all) | 10 | 1 |
| ☐ | 02 | [Networking Deep Dive](projects/02-networking-deep-dive/) | Packet analysis, protocols, IDS (SOC, network) | 8 | 1 |
| ☐ | 08 | [SOC & Detection Engineering](projects/08-soc-detection-engineering/) (part 1) | SIEM, detections, triage (SOC) | 12 | 1 |
| ☐ | 06 | [Web & Network Pentesting](projects/06-web-network-pentesting/) (part 1) | Recon, OWASP Top 10, reporting (pentest) | 8 | 1 |
| ☐ | 04 | [CyberPatriot Linux Image Builder](projects/04-cyberpatriot-linux-image/) | Linux hardening, scoring engines (sec eng) | 10 | 1 |
| ☐ | 03 | [WireGuard Remote Access](projects/03-wireguard-remote-access/) | VPNs, least privilege (network sec) | 6 | 2 |
| ☐ | 07 | [Active Directory: Build → Attack → Defend](projects/07-active-directory/) | AD, Kerberos, hardening (pentest, sec eng) | 18 | 2 |
| ☐ | 08 | SOC & Detection Engineering (part 2) | Sysmon, purple team (SOC) | 8 | 2 |
| ☐ | 05 | [CyberPatriot Windows Image Builder](projects/05-cyberpatriot-windows-image/) | Windows hardening (sec eng) | 10 | 3 |
| ☐ | 06 | Web & Network Pentesting (part 2) | Network pentest, privesc (pentest) | 8 | 3 |
| ☐ | 09 | [Host Your Own CTF](projects/09-host-a-ctf/) | Challenge design, Docker (all) | 10 | 3 |
| ☐ | 10 | [Red vs Blue Game Night](projects/10-red-vs-blue/) | Defense under pressure, IR (SOC, pentest) | 12 | 3 |
| ☐ | 11 | [DFIR & Incident Response](projects/11-dfir-incident-response/) | Forensics, timelines (DFIR) | 12 | 3 |
| ☐ | 12 | [Vuln Mgmt, Data Security & GRC](projects/12-vuln-mgmt-data-security-grc/) | Scanning, PKI/TLS, policy, risk (GRC, sec eng) | 16 | 3 |
| ☐ | 13 | [Infrastructure as Code Capstone](projects/13-infrastructure-as-code/) | Terraform, Ansible (cloud/DevSecOps) | 16 | 4 |
| ☐ | 14 | [Cloud & AI Security](projects/14-cloud-ai-security/) | IAM, S3, LLM prompt injection (cloud, AI sec) | 10 | 4 |

## Track your progress

[`tracker/`](tracker/) is a small self-hosted web app (FastAPI + SQLite, ~55 MB RAM) that turns
every project checklist into tick-boxes, logs hours, shows schedule milestones and charts your
career interests. It runs on your Ubuntu server behind `tailscale serve`. See
[tracker/README.md](tracker/README.md).

## Docs

| Doc | What it's for |
|---|---|
| [00-start-here](docs/00-start-here.md) | Resource budget, lab profiles, how to work through a project |
| [network-reference](docs/network-reference.md) | **Single source of truth**: VLANs, IPs, VMIDs, RAM, firewall matrix |
| [schedule](docs/schedule.md) | Week-by-week plan from Nov 2026 to Summer 2027, plus internship application timing |
| [learning-path](docs/learning-path.md) | MIT/Harvard/Stanford courses, video series, and the Python → C/C++ → Bash/PowerShell programming track |
| [python-primer](docs/python-primer.md) | Every Python technique the project solutions use, with small examples |
| [what-employers-want](docs/what-employers-want.md) | Hiring research, skill → project → proof map, resume and interview tips |
| [documentation-guide](docs/documentation-guide.md) | How industry documents work, writing style, sanitizing before publishing |
| [career-paths](docs/career-paths.md) | SOC, pentest, DFIR, security engineering, GRC, cloud: what each does, which projects and certs fit |
| [resources](docs/resources.md) | Curated free platforms, GitHub projects, and references |
| [similar-projects](docs/similar-projects.md) | Reputable labs and courses that overlap with these projects, and what was adopted from them |
| [scaling-to-two-nodes](docs/scaling-to-two-nodes.md) | RAM upgrade vs. a second OptiPlex, VLAN trunking, clustering |
| [safety-and-legal](docs/safety-and-legal.md) | Isolation rules, licensing, rules of engagement with friends |

## Ground rules

- **Isolation first.** Vulnerable machines never touch the home network or the internet
  (see [safety-and-legal](docs/safety-and-legal.md)).
- **One lab profile at a time.** 16 GB goes fast.
- **Snapshot before every exercise.** Breaking things is the point; rebuilding should be cheap.
- **Never commit secrets.** No private keys, passwords, or public IPs in this repo.
