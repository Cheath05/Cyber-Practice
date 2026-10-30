# What Internship Employers Actually Want

Research compiled October 2026 from hiring-manager surveys, Summer 2027 internship postings,
and hiring guides. Sources are linked at the bottom. **Re-check postings yourself.** Every
company is different, and requirements change each cycle.

## TL;DR

1. **Show, don't list.** Hiring managers trust *evidence* (a documented lab, a report, a
   detection rule, a write-up) more than a list of tools or coursework.
2. **Fundamentals beat fancy tools:** networking (TCP/IP, DNS, routing, VLANs), Linux *and*
   Windows administration, and Python/Bash scripting.
3. **Soft skills come first in surveys:** problem solving, teamwork and communication.
   Documentation is how you *prove* communication on paper.
4. **Security+ is often "preferred", rarely "required"** for internships.
5. **Cloud security, data security and AI** are the rising technical asks.
6. **Eligibility filters are real:** GPA floors (often 3.0), class standing, graduation window,
   US work authorization, and sometimes clearance eligibility. Check these before spending time
   on an application.

## What the surveys say

**ISC2 2025 Cybersecurity Hiring Trends** (929 hiring managers in 6 countries, surveyed Dec 2024):
- Hiring managers prioritize candidates with **hands-on IT experience or entry-level
  certifications** over candidates with only education. 90% would consider candidates with
  prior IT experience only; 89% would consider entry-level certs only.
- **Non-technical skills topped the list:** teamwork, problem solving, analytical thinking.
- **84% use skills-based assessments** while hiring. Expect practical questions and live
  exercises, not just "what does X stand for".
- Top early-career *technical* skills: **data security** (encryption, data handling and
  monitoring), **cloud security**, **data analysis**.

**ISC2 2025 Workforce Study** (reported April 2026): hiring managers named problem solving
(29%), collaboration (24%), communication (22%), curiosity (20%) and strategic thinking (16%)
ahead of their top technical needs: **AI and cloud security (15% each)**.

**Hiring guides and practitioner blogs** (vendor-written, so weigh them accordingly) repeat
the same themes:
- A **running homelab with a SIEM** (multiple endpoints reporting, tuned rules, and a
  documented history of investigations) is the most-cited differentiator.
- A **GitHub repo** with diagrams, detection rules, packet captures and CTF write-ups is more
  convincing than a cert line.
- Resume screeners spend about 20 seconds looking for **tools and outcomes, not adjectives**.

## What Summer 2027 postings ask for

This is a *sample*, not a statistically valid survey. It covers about 20 Summer/Fall 2027
postings found in October 2026 across SOC/general cyber, security engineering, offensive
security and GRC roles (listed in Sources). The "how common" column is a rough read across
that sample.

| Skill / requirement | How common | Role types | Where you build it here |
|---|---|---|---|
| Enrolled in CS/IT/cyber degree, class standing | Nearly all | All | — |
| Python (often + Bash/PowerShell) | Very common | Sec eng, pentest, SOC | Python exercise in **every** project; P08, P12, P13 |
| Linux administration | Common | Sec eng, SOC, pentest | P01, P04, P06, P11 |
| Networking fundamentals (OSI, TCP/IP, DNS, routing, VLANs) | Common | All, esp. network/security eng | **P01, P02, P03** |
| Windows administration / Active Directory | Common | Sec eng, SOC, pentest | P05, P07 |
| SIEM, alert triage, dashboards | Common in SOC/general cyber | SOC, IR | **P08**, P10 |
| Incident response: investigate, document, recommend | Common in SOC/general cyber | SOC, IR | P08, P10, **P11** |
| Pentest tools (Nmap, Burp, Metasploit) | Common in offensive | Pentest | **P06**, P07 |
| OWASP Top 10, MITRE ATT&CK, PTES | Some | Pentest, SOC | P06, P08 |
| Security+ / CySA+ (preferred) | Some | SOC, GRC, general | Optional, Phase 2–3 |
| NIST CSF / 800-53 / risk management | Most GRC postings | GRC, federal | **P12** |
| Cloud (AWS/Azure) security | Some, rising | Cloud sec, sec eng | P13, **P14** |
| Data loss prevention / data security | Some | Sec eng, GRC | P12 |
| AI / LLM security | Few but rising (e.g. offensive teams) | Pentest, sec eng | P14 |
| Git / version control | Some | Sec eng | This whole repo |
| Clearance / US person | Defense & federal | All federal | — |
| GPA ≥ 3.0 | Some | Large/defense employers | — |

## Skill → project → proof

When a recruiter or interviewer asks "do you know X?", point to the artifact.

| Skill they ask about | Project | Artifact to show |
|---|---|---|
| Network design, segmentation, firewalls | P01 | Network design doc (diagram, IPAM, firewall matrix), ADR |
| Packet analysis, protocols | P02 | Packet-analysis report with screenshots |
| VPN, least privilege, access control | P03 | VPN access policy + rule matrix |
| Linux & Windows hardening | P04, P05 | Hardening baselines + your scored CyberPatriot images |
| Web app security, OWASP Top 10 | P06 | Pentest report (exec summary + CVSS findings) |
| Active Directory attacks & defenses | P07 | Attack-path write-up + hardening change requests |
| SIEM, detection engineering, triage | P08 | Detection-rule docs mapped to ATT&CK, SOC tickets |
| Teamwork, communication under pressure | P09, P10 | CTF event retro, red-vs-blue after-action report |
| Incident response, forensics | P11 | Incident report, timeline, chain of custody |
| Vuln management, CVSS, patching | P12 | Scan report + remediation tracker |
| Data security (PKI/TLS, encryption, backups) | P12 | Internal CA design + encryption runbook |
| GRC, NIST CSF, policy | P12 | Policies, risk register, CSF self-assessment |
| Automation, IaC, DevSecOps | P13 | Terraform/Ansible repo |
| Cloud & AI security | P14 | flAWS / LLM-lab write-ups |
| Python / data analysis | All | Scripts in each project (`pcap_summary.py`, `enrich_alerts.py`, `scan_to_tracker.py`…) |

## Resume bullets that work

Formula: **Action verb + what you built/did + tools + measurable result or scope.**

- ❌ "Familiar with Wazuh, Splunk, Wireshark."
- ✅ "Deployed a Wazuh SIEM monitoring 4 Linux/Windows endpoints across 5 firewalled VLANs;
  wrote 7 custom detection rules mapped to MITRE ATT&CK that detected Kerberoasting and
  LLMNR poisoning in purple-team tests."

Put the lab under **Projects** (or "Security Homelab"), with a link to the GitHub repo. Each
project README ends with ready-made bullets you can tailor. See also
[`templates/resume-bullets.md`](../templates/resume-bullets.md).

## Interview prep: STAR stories

Skills-based interviews ask behavioral questions ("tell me about a time…"). Your WORKLOGs and
after-action reports are the raw material. Prepare 5 STAR stories
([`templates/star-story.md`](../templates/star-story.md)):

| Likely question | Story from this repo |
|---|---|
| A time you solved a hard technical problem | Locked yourself out of OPNsense / VLAN routing bug (P01) |
| A time you worked on a team | Red vs Blue game night (P10) or hosting the CTF (P09) |
| A time you explained something technical to non-technical people | Pentest report executive summary (P06) |
| A time you made a mistake | Anything from your WORKLOG where a fix broke something else |
| Walk me through investigating an alert | Purple-team detection of Kerberoasting (P07 + P08) |

Common technical screen questions, all answerable from these projects:
- What happens when you type a URL into a browser? (DNS, TCP, TLS, HTTP: P02)
- Difference between TCP and UDP? Why does WireGuard use UDP? (P02, P03)
- What's a VLAN and why segment a network? (P01)
- Explain Kerberos at a high level. What's Kerberoasting? (P07)
- How would you triage an alert for a suspicious PowerShell process? (P08)
- What's the difference between a vulnerability, a threat, and a risk? (P12)
- How do symmetric and asymmetric encryption differ? Where is each used? (P03, P12)

## Portfolio tips

- **Keep two repos:** this one for working notes (can stay private) and a **public portfolio**
  with sanitized deliverables, diagrams and a strong README. See
  [documentation-guide](documentation-guide.md#public-vs-private).
- Pin the portfolio repo on GitHub. Add a short README with a diagram at the top. Recruiters
  click and scroll for about 30 seconds.
- In LinkedIn's *Projects* section, add 3 projects with one sentence and a link each.
- Optional: a simple blog (GitHub Pages) with write-ups. CTF write-ups and "what I learned"
  posts get read.

## Sources

Surveys and research:
- ISC2, [Organizations Must Amend Early Career Hiring Practices (Jun 2025)](https://www.isc2.org/insights/2025/06/isc2-research-organizations-must-amend-early-career-hiring-practices)
- ISC2, [Cybersecurity Hiring Trends: Skills Deep Dive (Sep 2025)](https://www.isc2.org/insights/2025/09/cybersecurity-hiring-trends-skills-deep-dive)
- ISC2, [Aligning Skills, People and Hiring in Cybersecurity (Apr 2026)](https://www.isc2.org/Insights/2026/04/Aligning-Skills-People-and-Hiring-in-Cybersecurity)
- Infosecurity Magazine, [Hands-On Skills Now Key to Landing Your First Cyber Role](https://www.infosecurity-magazine.com/news/hands-on-skills-first-cyber-role/)
- TechRepublic, [Top 5 Skills Entry-Level Cybersecurity Professionals Need](https://www.techrepublic.com/article/news-cybersecurity-hiring-survey-isc2/)

Hiring guides (vendor/practitioner opinion):
- [simeononsecurity: Entry-Level Cybersecurity Jobs in 2026](https://simeononsecurity.com/cyber-security-career-playbook/getting-a-job-in-cyber-security/preparation-and-resources-for-entry-level-cyber-security-jobs/)
- [TryHackMe: What qualifications employers recognise for SOC roles](https://tryhackme.com/resources/blog/what-qualifications-do-employers-actually-recognise-for-soc-analyst-roles)
- [CyberDefenders: How to build a resume for SOC analyst roles](https://cyberdefenders.org/blog/how-to-build-a-resume-for-soc-analyst/)
- [Build a Home Lab That Actually Gets You Hired](https://thisisanitsupportgroup.com/blog/build-home-lab-it-career-guide-2026/)

Sampled Summer/Fall 2027 postings (Oct 2026; links may expire):
- General / SOC: [CNA](https://career.virginia.edu/jobs/cna-cybersecurity-intern-summer-2027/),
  [The Aerospace Corporation](https://www.builtinboston.com/job/cyber-security-intern-summer-2027/10943241),
  [The Home Depot](https://careers.homedepot.com/job/23777892/2027-summer-internship-cybersecurity-remote/),
  [ULA](https://jobs.ulalaunch.com/job/Centennial-Cyber-Security-Internship-Summer-2027-CO-80112/1427397700/),
  [Siemens](https://jobs.siemens.com/en_US/externaljobs/JobDetail/525197),
  [PwC Cyber Consulting](https://pwc.wd3.myworkdayjobs.com/en-US/US_Entry_Level_Careers/job/Cybersecurity-Consulting-Intern---Summer-2027_757226WD),
  [Allentown, PA cybersecurity intern](https://www.tealhq.com/job/cybersecurity-intern_7ea1af86a3d42db7531c1953835be53bbaba1),
  [GlobalFoundries](https://zapply.jobs/jobs/0b85e647-f294-4758-9e30-7a2bdf748458/)
- Security engineering: [Cloud security SWE intern](https://builtin.com/job/summer-2027-software-engineer-cloud-security-summer-internship/11783548),
  [Visa Network & Security Eng](https://www.dreamworkhq.com/job/bebd97d4-517c-4b3e-a7f5-52ac11f91c07),
  [Google Security Eng](https://zapply.jobs/jobs/3b2affe1-e2c7-4327-b6a9-351e308cacb5/),
  [General Dynamics Cyber Eng](https://www.gd.com/careers/cyber-engineering-intern-summer-2027-middletown-ri-us-2026-75514-gdms-opportunity),
  [RTX Secure Systems](https://zapply.jobs/jobs/f4defb9f-1781-4057-b0d1-2a064af0ff51/),
  [Intel InfoSec](https://zapply.jobs/jobs/d3497dca-7450-4174-aa1c-11f77af03b59/),
  [CoStar Security Eng](https://zapply.jobs/jobs/f272a7da-0f52-47b1-83b8-8aa2f59c19e8/)
- Offensive: [IBM X-Force Red "Hacker Intern"](https://www.wayup.com/i-Technology-j-Hacker-Intern-2027-IBM-628062721715147/),
  [Coalfire Division Hex](https://remoteleaf.com/company/coalfire/rochester-institute-of-technology-division-hex-pen-testing-2027-summer-internship-united-states/),
  [Tevora Threat (Winter 2027)](https://jobs.lever.co/tevora/1048eaf2-66b6-466d-bb59-8a75d7f5c968)
- GRC: [Cybersecurity GRC Analyst Intern](https://builtin.com/job/cybersecurity-grc-analyst-intern/4600873),
  [Cyber Security Intern (GRC)](https://dailyremote.com/remote-job/cyber-security-intern-grc-5164116)
