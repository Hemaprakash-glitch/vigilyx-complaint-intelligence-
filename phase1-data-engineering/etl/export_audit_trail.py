import os
from datetime import datetime

import pandas as pd
import psycopg2


conn = psycopg2.connect(
    host="localhost",
    database="vigilyx_complaints",
    user="postgres",
    password=os.getenv("POSTGRES_PASSWORD"),
    port=5432
)

try:

    with open(
        "phase1-data-engineering/sql/mdr_audit_trail.sql",
        "r",
        encoding="utf-8"
    ) as file:
        query = file.read()

    df = pd.read_sql(query, conn)

    os.makedirs(
        "phase1-data-engineering/exports",
        exist_ok=True
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = (
        f"phase1-data-engineering/exports/"
        f"audit_trail_{timestamp}.xlsx"
    )

    df.to_excel(output_path, index=False)

    print(f"✅ Audit trail exported successfully: {output_path}")

except Exception as e:

    print(f"❌ Export failed: {e}")

finally:

    conn.close()