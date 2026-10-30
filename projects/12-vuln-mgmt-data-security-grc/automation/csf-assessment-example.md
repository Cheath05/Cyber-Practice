# NIST CSF 2.0 Self-Assessment: Homelab (example structure)

Rate maturity 0–4 (0 none · 1 ad hoc · 2 documented · 3 implemented and tested · 4 measured
and improving). **Evidence** must link to a real artifact in this repo.

| Function | Subcategory (CSF 2.0) | Current | Target | Evidence | Gap / next step |
|---|---|---|---|---|---|
| Govern (GV) | GV.PO-01: Policy is established | 2 | 3 | P03 VPN policy, P12 policies | annual review not scheduled |
| Govern (GV) | GV.RM-01: Risk management objectives | 1 | 2 | P12 risk register | define risk appetite statement |
| Identify (ID) | ID.AM-01: Hardware inventory | 3 | 3 | P01 IPAM + P12 asset inventory | — |
| Identify (ID) | ID.RA-01: Vulnerabilities identified | 3 | 4 | P12 scan report + tracker | schedule monthly scans |
| Protect (PR) | PR.AA-05: Access permissions, least privilege | 3 | 3 | P01 firewall matrix, P03 WG rules | — |
| Protect (PR) | PR.DS-01: Data-at-rest protected | 2 | 3 | P12 LUKS + encrypted backup runbook | extend to all VMs with data |
| Protect (PR) | PR.DS-02: Data-in-transit protected | 2 | 3 | P12 internal CA + TLS | ACME auto-renewal |
| Detect (DE) | DE.CM-01: Networks monitored | 3 | 3 | P02 Suricata, P08 Wazuh | — |
| Detect (DE) | DE.AE-02: Events analyzed | 3 | 4 | P08 rule docs + SOC tickets | measure time-to-detect |
| Respond (RS) | RS.MA-01: Incident response plan executed | 2 | 3 | P10 incident reports, P11 IR report | write IR policy |
| Recover (RC) | RC.RP-01: Recovery plan executed | 2 | 3 | P01 backup/restore SOP | test full VM restore quarterly |
