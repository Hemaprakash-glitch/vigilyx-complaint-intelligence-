# Local Scheduling — Data Quality Report

## Current Setup (Windows Task Scheduler)

The quality report script (`quality_checks.py`) can be scheduled to run
weekly using Windows Task Scheduler:

1. Open Task Scheduler → Create Basic Task
2. Trigger: Weekly, Monday 7:00 AM
3. Action: Start a program
   - Program: `C:\Users\Hemu\Documents\vigilyx-complaint-intelligence\venv\Scripts\python.exe`
   - Arguments: `phase1-data-engineering\quality\quality_checks.py`
   - Start in: `C:\Users\Hemu\Documents\vigilyx-complaint-intelligence`

## Handling Silent Failures

If the script fails silently (e.g., DB connection drops), no report is
generated and no one is notified. A future improvement: log failures to
a separate `scheduler_errors.log` file and alert via email if the log
grows.

## Migration Path to Production Orchestration

This manual/cron-based approach works for a single-developer setup, but
does not scale. Moving to **Apache Airflow** or **Prefect** would provide:
- Retry logic on failure
- Dependency chaining (ETL → quality check → report, in sequence)
- Centralized monitoring dashboard
- Alerting on failure (Slack/email)

This is not implemented now, but is the natural next step once this
pipeline moves beyond a single local machine.