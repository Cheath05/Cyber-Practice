-- Vulnerability metrics for the Project 12 tracker (SQL exercise, solution).
-- Run:  sqlite3 -header -column vulns.db < metrics.sql
-- To practice: mark some findings fixed first, e.g.
--   UPDATE vulns SET status='Fixed', fixed='2026-04-10' WHERE id IN ('V-001','V-002');

-- 1. Open findings by (priority) severity
SELECT priority_severity AS severity, COUNT(*) AS open_findings
FROM vulns
WHERE status = 'Open'
GROUP BY priority_severity
ORDER BY CASE priority_severity
  WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 WHEN 'low' THEN 4 ELSE 5 END;

-- 2. Findings past their SLA due date
SELECT id, asset, title, priority_severity, due
FROM vulns
WHERE status = 'Open' AND due <> '' AND due < date('now')
ORDER BY due;

-- 3. Top 5 assets by risk (weighted count of open findings)
SELECT asset,
       SUM(CASE priority_severity WHEN 'critical' THEN 10 WHEN 'high' THEN 5
                                  WHEN 'medium' THEN 2 WHEN 'low' THEN 1 ELSE 0 END) AS risk_score,
       COUNT(*) AS open_findings
FROM vulns
WHERE status = 'Open'
GROUP BY asset
ORDER BY risk_score DESC
LIMIT 5;

-- 4. Mean days to remediate, by severity, for fixed findings
SELECT priority_severity AS severity,
       ROUND(AVG(julianday(fixed) - julianday(found)), 1) AS mean_days_to_remediate,
       COUNT(*) AS fixed_findings
FROM vulns
WHERE status = 'Fixed' AND fixed IS NOT NULL
GROUP BY priority_severity;

-- 5. Known-exploited (KEV) findings still open: these jump the queue
SELECT id, asset, title, cve FROM vulns WHERE kev = 'yes' AND status = 'Open';
