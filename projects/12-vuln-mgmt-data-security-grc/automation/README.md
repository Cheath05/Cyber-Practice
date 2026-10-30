# ⚠️ Solution: use only if stuck

| File | What it does |
|---|---|
| `python/scan_to_tracker.py` | Python exercise: Nuclei JSONL / Greenbone CSV → de-duplicated tracker CSV + SQLite, SLA dates, CISA KEV flag |
| `sql/metrics.sql` | SQL exercise: vulnerability metrics queries for the SQLite tracker (`sudo apt install sqlite3`, then `sqlite3 -header -column vulns.db < sql/metrics.sql`) |
| `samples/nuclei-sample.jsonl`, `samples/kev-sample.json` | Tiny sample inputs to test the tracker without running a scan |
| `step-ca-compose.yml` | Alternative to the LXC install: step-ca in Docker |
| `csf-assessment-example.md` | Example structure for the NIST CSF 2.0 self-assessment |
