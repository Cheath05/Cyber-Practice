# Detection: <Rule name>

| Field | Value |
|---|---|
| Rule ID | <Wazuh rule id, e.g. 100100> |
| Author / date | <you> / YYYY-MM-DD |
| Status | Experimental / Testing / Production |
| Severity | Low / Medium / High / Critical (Wazuh level: <n>) |
| MITRE ATT&CK | <Tactic> / <T1558.003 – Kerberoasting> |
| Data source | <Windows Security 4769, Sysmon EID 1, auditd, …> |
| Platform | <Wazuh / Sigma> |

## Goal
> What adversary behavior this detects, in one sentence.

## Logic
> Plain English first, then the rule.

```xml
<!-- Wazuh rule / Sigma YAML here -->
```

## Test procedure (how you proved it works)
1. Attack: `<command / Atomic Red Team test ID>`
2. Expected alert: <rule id, description>
3. Result: ✅ fired at <timestamp> (screenshot: `img/…`)

## False positives
| Benign cause | How to tell apart | Tuning applied |
|---|---|---|

## Triage guidance for analysts
1. <first thing to check>
2. <escalate if …>

## Blind spots / bypasses
> How could an attacker avoid this rule?

## References
