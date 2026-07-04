import os
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import psycopg2


@dataclass
class QualityIssue:
    """
    Represents the result of a single data quality check.
    """

    check_name: str
    severity: str
    count: int
    detail: str


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    return psycopg2.connect(
        host="localhost",
        database="vigilyx_complaints",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        port=5432
    )


def check_stale_open_complaints(conn) -> QualityIssue:
    """
    Identify complaints that:
    1. Are still Open
    2. Older than 90 days
    3. Have no investigation record
    """

    query = """
    SELECT COUNT(*)
    FROM complaints c
    LEFT JOIN investigations i
        ON c.complaint_id = i.complaint_id
    WHERE
        c.status = 'Open'
        AND CURRENT_DATE - c.received_date > 90
        AND i.complaint_id IS NULL;
    """

    cursor = conn.cursor()
    cursor.execute(query)

    stale_count = cursor.fetchone()[0]

    cursor.close()

    return QualityIssue(
        check_name="Stale Open Complaints",
        severity="warning" if stale_count > 0 else "info",
        count=stale_count,
        detail=f"{stale_count} complaint(s) are open for more than 90 days without an investigation."
    )


def check_null_mandatory_fields(conn) -> QualityIssue:
    """
    Check business-mandatory fields that should be populated
    after ETL.
    """

    query = """
    SELECT COUNT(*)
    FROM complaints
    WHERE
        event_description IS NULL
        OR imdrf_code IS NULL;
    """

    cursor = conn.cursor()
    cursor.execute(query)

    null_count = cursor.fetchone()[0]

    cursor.close()

    return QualityIssue(
        check_name="Business Mandatory Fields",
        severity="critical" if null_count > 0 else "info",
        count=null_count,
        detail=f"{null_count} complaint(s) are missing event_description or IMDRF code."
    )


def check_orphaned_investigations(conn) -> QualityIssue:
    """
    Detect investigations that reference complaints
    which do not exist.
    """

    query = """
    SELECT COUNT(*)
    FROM investigations i
    LEFT JOIN complaints c
        ON i.complaint_id = c.complaint_id
    WHERE c.complaint_id IS NULL;
    """

    cursor = conn.cursor()
    cursor.execute(query)

    orphan_count = cursor.fetchone()[0]

    cursor.close()

    return QualityIssue(
        check_name="Orphaned Investigations",
        severity="critical" if orphan_count > 0 else "info",
        count=orphan_count,
        detail=f"{orphan_count} investigation(s) reference a complaint that does not exist."
    )


def run_all_checks(conn) -> list:
    """
    Execute all configured data quality checks.
    """

    checks = [
        check_stale_open_complaints,
        check_null_mandatory_fields,
        check_orphaned_investigations,
    ]

    return [check(conn) for check in checks]


def render_report(issues: list, output_path: str):
    """
    Generate an Excel data quality report.
    """

    data = [
        {
            "Check Name": issue.check_name,
            "Severity": issue.severity,
            "Count": issue.count,
            "Detail": issue.detail,
        }
        for issue in issues
    ]

    df = pd.DataFrame(data)

    df.to_excel(output_path, index=False)

    print(f"✅ Report written to {output_path}")


if __name__ == "__main__":

    conn = get_connection()

    try:

        issues = run_all_checks(conn)

    finally:

        conn.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = (
        f"phase1-data-engineering/quality/"
        f"quality_report_{timestamp}.xlsx"
    )

    render_report(issues, output_path)