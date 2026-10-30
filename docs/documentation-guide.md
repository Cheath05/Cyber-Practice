# Documentation Guide: Write Like You're Already on the Job

In real security jobs, **if it isn't written down, it didn't happen**:
- A SOC analyst's ticket is the only record of an investigation.
- A pentester's *report* is the product the client pays for; the hacking is just how you get
  there.
- An engineer's change request is how a firewall change gets approved.
- An incident report can end up in front of lawyers or regulators.

Every project in this repo makes you produce the documents a professional would. They're
also your best resume evidence.

## Document types and who reads them

| Document | Template | Who reads it in the real world | Used in |
|---|---|---|---|
| Lab notebook / worklog | [`worklog.md`](../templates/worklog.md) | You, your team, future you | All |
| Network design doc | [`network-design.md`](../templates/network-design.md) | Network/security engineers, auditors | P01, P13 |
| Architecture decision record (ADR) | [`adr.md`](../templates/adr.md) | Engineers maintaining your system later | P01, P13 |
| Runbook / SOP | [`runbook-sop.md`](../templates/runbook-sop.md) | Whoever is on call at 2 a.m. | P01, P02, P03, P08 |
| Change request | [`change-request.md`](../templates/change-request.md) | Change advisory board (CAB), your manager | P03, P07 |
| Packet analysis report | [`packet-analysis-report.md`](../templates/packet-analysis-report.md) | Network/SOC analysts, IR team | P02 |
| Hardening baseline | [`hardening-baseline.md`](../templates/hardening-baseline.md) | Sysadmins, auditors | P04, P05 |
| Pentest report | [`pentest-report.md`](../templates/pentest-report.md) | Executives (summary) + engineers (findings) | P06, P07, P10 |
| CTF / box write-up | [`ctf-writeup.md`](../templates/ctf-writeup.md) | Community, hiring managers | P06, P09, P14 |
| Detection rule doc | [`detection-rule.md`](../templates/detection-rule.md) | SOC analysts, detection engineers | P08 |
| SOC ticket | [`soc-ticket.md`](../templates/soc-ticket.md) | SOC team, IR lead | P08, P10 |
| Incident report | [`incident-report.md`](../templates/incident-report.md) | Management, legal, IR team | P10, P11 |
| Chain of custody | [`chain-of-custody.md`](../templates/chain-of-custody.md) | Forensics, legal | P11 |
| Rules of engagement | [`rules-of-engagement.md`](../templates/rules-of-engagement.md) | Red team, blue team, management | P06, P10 |
| After-action report (AAR) | [`after-action-report.md`](../templates/after-action-report.md) | Everyone who took part, leadership | P09, P10 |
| Vulnerability remediation tracker | [`vuln-remediation-tracker.md`](../templates/vuln-remediation-tracker.md) | Vuln mgmt team, system owners | P12 |
| Policy | [`policy.md`](../templates/policy.md) | All employees, auditors | P03, P12 |
| Risk register | [`risk-register.md`](../templates/risk-register.md) | GRC, leadership | P12 |
| Resume bullets / STAR stories | [`resume-bullets.md`](../templates/resume-bullets.md), [`star-story.md`](../templates/star-story.md) | Recruiters, interviewers | All |

Create a deliverable from a template:

```bash
scripts/new-doc.sh 06-web-network-pentesting pentest-report            # → deliverables/pentest-report.md
scripts/new-doc.sh 08-soc-detection-engineering detection-rule ssh-brute-force
# → deliverables/detection-rule-ssh-brute-force.md
```

## Writing style rules

1. **Audience first.** Before writing, name who reads it and what decision they need to make.
   An executive summary is for someone with 2 minutes; a runbook step is for someone tired and
   stressed.
2. **Bottom line up front (BLUF).** Conclusion first, details after. "Three critical findings
   allow full domain takeover" comes before the methodology.
3. **Reproducible.** Every technical claim includes the exact command, file, or screenshot that
   proves it. Someone else should be able to repeat your work from the doc alone.
4. **Specific over vague.** ❌ "Configured the firewall." ✅ "Added rule #4 on TARGETS: block
   10.10.30.0/24 → any, logged."
5. **Timestamps and versions.** Dates in ISO format (`2026-11-03`), times with timezone, and
   software versions ("OPNsense 25.7").
6. **Facts vs. assumptions.** In incident and analysis docs, label what you *observed* separately
   from what you *infer*.
7. **Short paragraphs, tables, numbered steps.** Nobody reads walls of text.
8. **Plain language.** Define acronyms on first use. Your reader might be a manager.

## Diagrams

- Use **Mermaid** (renders on GitHub, lives in Markdown, diffs nicely in git) for flows and
  simple topologies. Every project README has examples.
- Use **draw.io / diagrams.net** for detailed network diagrams. Export the `.drawio` source
  *and* a `.png` into `deliverables/`.
- A good network diagram shows segments, subnets, VLAN IDs, gateways, trust boundaries,
  and what crosses them, not every cable.

## Screenshots

- Crop to what matters; highlight it with a red box.
- Caption every screenshot: *"Figure 3: Suricata alert ET SCAN Nmap triggered at 14:02."*
- **Redact** before saving: passwords, keys, public IPs, real names, email addresses.
- Keep them in `deliverables/img/` with descriptive names (`p08-fig3-suricata-nmap.png`).

## Version control your docs

- Commit docs alongside configs: `git commit -m "P01: add firewall rule matrix v2"`.
- When you change a design, update the doc and write an ADR for *why*.
- Your git history becomes evidence of consistent work over months. That itself tells
  employers something.

## Sanitizing before publishing

Before anything goes public (portfolio repo, blog, LinkedIn), check for:

| Remove / replace | Example | Replace with |
|---|---|---|
| Private keys, WireGuard keys, API tokens | `PrivateKey = kL3…` | `PrivateKey = <redacted>` |
| Passwords (even lab ones; they get reused) | `admin:Summer2026!` | `<password>` |
| Your public IP / DDNS hostname | `73.x.x.x`, `myhome.duckdns.org` | `<public-ip>`, `vpn.example.com` |
| Home network layout | `192.168.1.0/24` | `<home-net>` |
| Friends' names, emails, usernames | `alex@…` | `Player 2` |
| Serial numbers, MAC addresses | `bc:24:11:…` | `xx:xx:…` |

Quick scan before pushing:

```bash
git diff --cached | grep -nEi 'privatekey|password|passwd|secret|token|BEGIN .*PRIVATE|[0-9]{1,3}(\.[0-9]{1,3}){3}' | grep -v '10\.10\.'
```

The repo's `.gitignore` already blocks `*.key`, `*.pem`, `*wg*.conf`, `.env`, and
`secrets/`, but **you** are the final check.

## Public vs. private

| Keep private (this repo can stay private) | Publish (portfolio repo) |
|---|---|
| Raw WORKLOGs with real configs | Cleaned-up WORKLOG highlights ("lessons learned") |
| Answer keys for images/CTFs you'll reuse | Image *design* doc (no answers) |
| Exact firewall exports | Firewall rule matrix (sanitized) |
| Real IPs/hostnames | Diagrams with lab IPs (10.10.x.x is fine) |
| Friends' info | Anonymized AARs |

Suggested public portfolio structure:

```
security-portfolio/
  README.md               # who you are, diagram, links to each project
  01-network-design/      # sanitized design doc + diagram
  06-pentest-report/      # report PDF + markdown
  07-ad-purple-team/      # attack path + detections + fixes
  08-detections/          # rule docs + rule files
  writeups/               # CTF / box write-ups
```

## Worklog habits

- One entry per session, written **during** the session (keep the file open).
- Record: goal, what you did (commands), what broke, how you fixed it, time spent, and next steps.
- Paste exact error messages. Future you will search for them.
- End every entry with **"What I learned"** in one or two sentences. Those lines become
  interview answers.
