# Templates

Professional document templates. Don't edit these directly. Copy one into a project's
`deliverables/` folder with:

```bash
scripts/new-doc.sh <project-folder> <template-name> [suffix]
# e.g. scripts/new-doc.sh 08-soc-detection-engineering detection-rule kerberoasting
```

Then replace every `<placeholder>` and delete guidance lines starting with `>`.
See [`docs/documentation-guide.md`](../docs/documentation-guide.md) for how and why.

| Template | Purpose |
|---|---|
| `worklog.md` | Dated lab notebook entry format |
| `network-design.md` | Topology, IPAM, firewall matrix, trust boundaries |
| `adr.md` | Architecture Decision Record: one decision and its reasoning |
| `runbook-sop.md` | Step-by-step operational procedure |
| `change-request.md` | Change management request |
| `hardening-baseline.md` | Security configuration baseline/checklist |
| `packet-analysis-report.md` | Packet capture analysis |
| `pentest-report.md` | Penetration test report |
| `ctf-writeup.md` | CTF challenge / box write-up |
| `detection-rule.md` | Detection-as-code documentation |
| `soc-ticket.md` | SOC alert triage ticket |
| `incident-report.md` | Incident response report |
| `chain-of-custody.md` | Evidence handling log |
| `rules-of-engagement.md` | Red/blue/CTF rules and scope |
| `after-action-report.md` | Post-exercise review |
| `vuln-remediation-tracker.md` | Vulnerability tracking table |
| `policy.md` | Security policy |
| `risk-register.md` | Risk register |
| `resume-bullets.md` | Turning projects into resume lines |
| `star-story.md` | Behavioral interview answer |
