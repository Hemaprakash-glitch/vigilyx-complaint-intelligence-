/*
Sprint 1.3.4 - Investigation Resolution Cycle Time
*/
SELECT
    complaint_id,
    investigation_start_date,
    investigation_close_date,
    investigation_close_date - investigation_start_date AS cycle_days
FROM investigations
WHERE investigation_close_date IS NOT NULL
ORDER BY cycle_days DESC;