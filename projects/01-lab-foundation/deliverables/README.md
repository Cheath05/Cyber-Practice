# Deliverables: Project 01 – Lab Foundation

Create each document from its template, then fill it in. Tick it off when it's done
*and* sanitized (see [documentation guide](../../../docs/documentation-guide.md#sanitizing-before-publishing)).

| Done | Document | Create with |
|---|---|---|
| ☐ | Network design doc (diagram, IPAM, firewall matrix, validation results) | `scripts/new-doc.sh 01-lab-foundation network-design` |
| ☐ | ADR-001: production server placement | `scripts/new-doc.sh 01-lab-foundation adr 001-prod-placement` |
| ☐ | ADR-002: VLAN-aware bridge vs. separate bridges | `scripts/new-doc.sh 01-lab-foundation adr 002-vlan-aware` |
| ☐ | Runbook: create a lab VM from template | `scripts/new-doc.sh 01-lab-foundation runbook-sop create-vm` |
| ☐ | SOP: backup & restore (OPNsense config + vzdump), with a tested restore | `scripts/new-doc.sh 01-lab-foundation runbook-sop backup-restore` |

Screenshots go in `img/` next to this file.
