# ⚠️ Solution: use only if stuck

| File | Run where | What it does |
|---|---|---|
| `install-wazuh.sh` | wazuh VM (401) | All-in-one install via the official script + indexer heap cap for a 5 GB VM |
| `agent-linux.sh` | Linux endpoints | Adds the Wazuh apt repo, installs + enrolls the agent, installs auditd |
| `agent-windows.ps1` | dc01 / ws01 (elevated) | Installs the agent MSI + Sysmon with a community config, adds the Sysmon channel, enables key audit subcategories |
| `ossec-remote-syslog.xml` | manager `ossec.conf` | Syslog listener for OPNsense (firewall + Suricata), restricted to 10.10.40.1 |
| `rules/local_rules.xml` | manager `/var/ossec/etc/rules/` | 8 custom rules (Linux FIM/persistence, Windows AD attacks, Sysmon) mapped to ATT&CK |
| `sigma/*.yml` | — | The same ideas as vendor-neutral Sigma rules |
| `python/enrich_alerts.py` | anywhere | Python exercise: analytics over `alerts.json` |

Rule field names follow Wazuh 4.x decoders. **Always verify with `wazuh-logtest`** against
your own events before trusting a rule; decoders change between versions.
