# Hardening Baseline: <OS / system> v<1.0>

| Field | Value |
|---|---|
| Applies to | <e.g. Ubuntu 24.04 servers in TARGETS> |
| Based on | <CIS Benchmark vX section …, vendor guide, CyberPatriot checklist> |
| Author / date | <you> / YYYY-MM-DD |

> Each control: what, why, how to check, how to fix. Keep the "check" commands exact so the
> baseline can be audited (and later automated: aeacus, Ansible, OpenSCAP).

## Summary
| Category | # controls | Automated? |
|---|---|---|
| Accounts & authentication | | |
| Services | | |
| Network/firewall | | |
| Logging & auditing | | |
| Updates | | |
| File permissions | | |

## Controls
| ID | Control | Rationale | Check | Remediation | CIS ref |
|---|---|---|---|---|---|
| ACC-01 | Password max age ≤ 90 days | Limits use of stolen creds | `grep PASS_MAX_DAYS /etc/login.defs` | Set `PASS_MAX_DAYS 90` | 5.5.1.2 |
| | | | | | |

## Exceptions
| Control | Reason | Compensating control | Approved by |
|---|---|---|---|
