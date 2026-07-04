import json
import os
from datetime import datetime

import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="vigilyx_complaints",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        port=5432
    )


def parse_maude_date(date_str):
    """
    Convert MAUDE date format:
    YYYYMMDD -> YYYY-MM-DD
    """

    if not date_str:
        return None

    try:
        return datetime.strptime(
            date_str,
            "%Y%m%d"
        ).date()

    except Exception:
        return None


def load_maude_records(json_path, search_term):

    with open(
        json_path,
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    conn = get_connection()

    cursor = conn.cursor()

    sql = """
    INSERT INTO maude_external_events
    (
        maude_event_id,
        product_code,
        device_name,
        event_type,
        date_received,
        source_search_term
    )

    VALUES (%s,%s,%s,%s,%s,%s)

    ON CONFLICT (maude_event_id)

    DO NOTHING;
    """

    inserted = 0

    for record in records:

        report_number = record.get("report_number")

        if not report_number:
            continue

        devices = record.get("device", [])

        if devices:

            first_device = devices[0]

            product_code = first_device.get(
                "device_report_product_code"
            )

            device_name = first_device.get(
                "generic_name"
            )

        else:

            product_code = None

            device_name = None

        event_type = record.get("event_type")

        received_date = parse_maude_date(
            record.get("date_received")
        )

        cursor.execute(

            sql,

            (
                report_number,
                product_code,
                device_name,
                event_type,
                received_date,
                search_term
            )

        )

        inserted += 1

    conn.commit()

    cursor.close()

    conn.close()

    print(f"Loaded {inserted} MAUDE records.")


if __name__ == "__main__":

    load_maude_records(

        "shared/data/maude_sample.json",

        'device.device_report_product_code:"OZO"'

    )