# Rules of Engagement: <Event name>

| Field | Value |
|---|---|
| Date / time window | YYYY-MM-DD HH:MM–HH:MM <TZ> |
| White team (referee) | <name> |
| Red team | <names> |
| Blue team(s) | <names> |
| Emergency stop word | "<word>" (anyone can call it; all activity stops) |

All participants must read and agree before the event starts (sign or reply "I agree").

## 1. Scope
| ✅ In scope | ❌ Out of scope |
|---|---|
| <10.10.30.51–.53 (blue boxes)> | OPNsense, Proxmox, scoring server 10.10.10.20 |
| | Anyone's home network, the internet, personal devices |
| | Other players' laptops |

## 2. Allowed
- <scanning, exploitation, persistence on in-scope hosts, …>

## 3. Not allowed
- Denial of service / resource exhaustion (one shared 16 GB server!)
- Attacking the scoring engine or white-team infrastructure
- Deleting/encrypting the whole box (ransomware simulation only if agreed)
- Social engineering of real accounts; physical access to the server
- Changing other players' VPN configs

## 4. Blue team rules
- Required services that must stay up (scored): <SSH, HTTP, …>
- Allowed: change passwords, patch, firewall *without* blocking the scoring engine
  (10.10.10.20), remove backdoors
- Not allowed: blanket-blocking the red team subnet (`10.10.20.0/24` / WG peers) unless the
  rules for this round say so

## 5. Scoring
> Summarize: service uptime points, red-team flag captures, incident reports, penalties.

## 6. Communication
- Channel: <Discord voice/text channel>
- Report findings / incidents to white team via: <form/channel>

## 7. Data handling
- No real personal data on any lab system.
- Anything found in the lab stays in the lab.

## 8. Sign-off
| Name | Role | Agreed (date) |
|---|---|---|
