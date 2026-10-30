# Schedule: Nov 2026 → Summer 2027

**Assumptions**
- About **8 hours/week** during the semester (your range is 6–10), about 10/week over winter
  break, lighter during finals.
- About **20% buffer** is built in. Labs break, ISOs download slowly, and OPNsense rules lock
  you out. That's normal; the buffer absorbs it.
- Hours per project include the **documentation** (worklog plus deliverables). Docs typically
  take 25–30% of a project's time. That's realistic; it's about the same share in the industry.
- If you fall behind, **don't skip deliverables; skip stretch goals.** A finished, documented
  project is worth more than three half-built ones.

## The application timeline (read this first)

You're applying for **Summer 2027** internships *now*. Recruiting doesn't wait for your lab to
be finished:

| When | What's happening | What you do |
|---|---|---|
| **Now – Nov** | Large companies, defense contractors and consulting firms (Big 4 cyber consulting, aerospace, banks) are open; many close by Nov–Dec | **Apply now.** Put the lab on your resume as *in progress* with what you've built so far. Update it each checkpoint. |
| **Dec – Feb** | Second wave: mid-size companies, MSSPs, utilities, hospitals, state agencies | Apply with the Phase 1 portfolio (network design, SIEM, pentest report) |
| **Feb – Apr** | Late postings: government (watch USAJOBS and state agency boards), local companies, university IT security offices, startups | Apply with the Phase 2 portfolio (AD purple-team project) |
| **Ongoing** | Career fairs, BSides conferences, local ISSA/ISACA/OWASP chapter meetings, CyberPatriot mentoring | Bring a one-page portfolio summary (QR code to your GitHub) |

Tips:
- Many postings ask for a GPA floor (often 3.0), class standing (sophomore/junior+), and US
  work authorization. Some defense roles need clearance eligibility. Filter for these quickly so
  your time goes to roles you qualify for.
- Your university's IT/security office often hires student analysts. That's real SOC
  experience during the school year.
- Apply in batches of 5–10 per week, and track them in a spreadsheet (company, date, contact,
  status).

## Phase 1: Resume sprint (Mon Nov 2 – Sun Dec 20, 7 weeks, ~56 h)

Goal: by mid-December, your resume and GitHub show a **segmented network you designed**, a
**working SIEM with detections**, a **pentest report**, and a **CyberPatriot-style image you
built**. These are the artifacts hiring guides mention most (see
[what-employers-want](what-employers-want.md)).

| Week | Dates | Work | Hours | Deliverables due |
|---|---|---|---|---|
| 1 | Nov 2–8 | **P01 Lab Foundation**: resize OPNsense, VLANs, firewall rules, Ubuntu template | 10 | Network design doc, ADR, build runbook |
| 2 | Nov 9–15 | **P02 Networking Deep Dive**: captures, DNS/DHCP/ARP, Suricata | 8 | Packet-analysis report |
| 3 | Nov 16–22 | **P08 part 1**: install Wazuh, Linux agents, first alerts | 6 | — |
| 4 | Nov 23–29 (Thanksgiving) | **P08 part 1**: custom rules, triage tickets | 6 | 3 detection-rule docs, 2 SOC tickets |
| 5 | Nov 30–Dec 6 | **P06 part 1**: Juice Shop / DVWA, Burp, OWASP Top 10 | 8 | Pentest report (web), 2 write-ups |
| 6 | Dec 7–13 (finals) | **P04 CyberPatriot Linux image** (build + plant vulns) | 5 | — |
| 7 | Dec 14–20 (finals) | **P04**: aeacus scoring, swap images with a friend | 5 | Hardening baseline, answer key |
| — | buffer | Catch-up / troubleshooting | 8 | — |

**Checkpoint 1 (Dec 20):** update your resume, make the portfolio repo public (sanitized), pin
it on GitHub, and update your LinkedIn *Projects* section.

## Phase 2: Winter break (Mon Dec 21 – Sun Jan 17, 4 weeks, ~40 h)

Goal: the **Active Directory purple-team project**. Attack AD, catch it in Wazuh, then fix it.
This is the single strongest interview story in this repo.

| Week | Dates | Work | Hours | Deliverables due |
|---|---|---|---|---|
| 8 | Dec 21–27 | **P03 WireGuard** for you and friends (holiday week, light) | 6 | VPN access policy, onboarding runbook |
| 9 | Dec 28–Jan 3 | **P07** build: Windows templates, DC, client, domain join, users | 9 | AD design doc |
| 10 | Jan 4–10 | **P07** attack (Kerberoast, AS-REP, LLMNR, BloodHound) + defend | 9 | Attack-path write-up, change requests |
| 11 | Jan 11–17 | **P08 part 2**: Sysmon + Windows agents, detect your P07 attacks | 8 | 2 more detection rules, purple-team summary |
| — | buffer | | 8 | — |

Optional: start **Security+** study (about 30–40 h total across Phase 2–3, e.g. Professor
Messer's free videos plus practice tests). Many entry postings list it as *preferred*. Aim to
take the exam Feb–Mar. Check CompTIA's student pricing first.

**Checkpoint 2 (Jan 17):** resume v3 with the AD purple-team bullet. Apply to the second wave.

## Phase 3: Spring semester (Mon Jan 18 – Sun May 16, 17 weeks, ~120 h)

About 7 h/week, with lighter weeks around midterms and finals.

| Weeks | Dates | Work | Hours | Deliverables |
|---|---|---|---|---|
| 12–13 | Jan 18–31 | **P05 CyberPatriot Windows image** | 10 | Hardening baseline, answer key |
| 14–15 | Feb 1–14 | **P06 part 2**: Metasploitable 2, Vulhub, privesc | 8 | Pentest report v2 (network), write-ups |
| 16–17 | Feb 15–28 | **P09 Host a CTF**: CTFd + challenges, run it for friends | 10 | Challenge docs, event plan, retro |
| 18–19 | Mar 1–14 (spring break) | **P10 Red vs Blue game night** | 12 | ROE, red report, blue IRs, AAR |
| 20–21 | Mar 15–28 | **P11 DFIR** | 12 | Incident report, chain of custody, timeline |
| 22–24 | Mar 29–Apr 18 | **P12 Vuln Mgmt, Data Security & GRC** | 16 | Scan report + tracker, policies, risk register, CSF |
| 12–26 | throughout | Security+ study + exam (optional) | ~35 | Certification |
| 25–28 | Apr 19–May 16 | Finals buffer / catch-up | ~17 | — |

**Checkpoint 3 (mid-May):** final portfolio polish before the internship (or before fall 2027
recruiting if you're applying again).

## Phase 4: Summer 2027 (~26 h, at your own pace)

| Work | Hours | Deliverables |
|---|---|---|
| **P13 Infrastructure as Code**: rebuild the lab from Terraform + Ansible | 16 | Repo README, ADRs |
| **P14 Cloud & AI Security**: flAWS 1/2, PortSwigger LLM labs, Gandalf | 10 | Findings write-ups |

## Hours summary

| Phase | Project hours | Buffer / other | Total |
|---|---|---|---|
| 1 | 48 | 8 | 56 |
| 2 | 32 | 8 | 40 |
| 3 | 68 | 35 (Sec+) + 17 buffer | 120 |
| 4 | 26 | — | 26 |
| **Total** | **174** | **68** | **242** |

## If you fall behind

1. Cut stretch goals first, then Python exercises, then Phase 4.
2. Never cut: P01, P08, P07, P06 part 1 (the most-requested skills) or their deliverables.
3. If a project takes more than 2× its estimate, stop and write down why in your WORKLOG. Then
   use the `automation/` solution for the blocking step and move on.
