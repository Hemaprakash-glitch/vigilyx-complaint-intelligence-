import logging
import pandas as pd
import psycopg2
import os

# ----------------------------------------
# Logging
# ----------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("vigilyx.etl")


# ----------------------------------------
# Extract
# ----------------------------------------

def extract(csv_path: str) -> pd.DataFrame:

    df = pd.read_csv(csv_path)

    logger.info(f"Extracted {len(df)} rows from {csv_path}")

    return df


# ----------------------------------------
# Normalize Dates
# ----------------------------------------

def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:

    def convert_date(value):

        if pd.isna(value):
            return value

        value = str(value).strip()

        try:

            # Already ISO format
            if len(value) >= 10 and value[:4].isdigit():

                return (
                    pd.to_datetime(value)
                    .strftime("%Y-%m-%d")
                )

            # DD-MM-YYYY format
            return (
                pd.to_datetime(
                    value,
                    dayfirst=True
                )
                .strftime("%Y-%m-%d")
            )

        except Exception:

            return value

    df["received_date"] = df["received_date"].apply(convert_date)
    df["close_date"] = df["close_date"].apply(convert_date)

    return df


# ----------------------------------------
# Normalize Text
# ----------------------------------------

def normalize_text(df: pd.DataFrame) -> pd.DataFrame:

    text_columns = [
        "product_code",
        "imdrf_code",
        "regulatory_market",
        "status"
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .where(df[column].notna(), pd.NA)
            .str.strip()
        )

    df["product_code"] = (
        df["product_code"]
        .str.upper()
    )

    return df


# ----------------------------------------
# Flag Quality Issues
# ----------------------------------------

def flag_quality_issues(df: pd.DataFrame) -> pd.DataFrame:

    df["quality_issue"] = ""

    # Missing received date

    mask = df["received_date"].isna()

    df.loc[
        mask,
        "quality_issue"
    ] += "Missing received_date; "

    # Missing event description

    mask = df["event_description"].isna()

    df.loc[
        mask,
        "quality_issue"
    ] += "Missing event_description; "

    # Invalid status

    valid_status = [
        "Open",
        "Investigating",
        "Closed",
        "Reopened"
    ]

    mask = ~df["status"].isin(valid_status)

    df.loc[
        mask,
        "quality_issue"
    ] += "Invalid status; "

    # Orphan product code

    mask = df["product_code"] == "XXX-999"

    df.loc[
        mask,
        "quality_issue"
    ] += "Unknown product_code; "

    # Duplicate complaint_id

    duplicate_mask = df.duplicated(
        subset="complaint_id",
        keep=False
    )

    df.loc[
        duplicate_mask,
        "quality_issue"
    ] += "Duplicate complaint_id; "

    logger.info(
        "Quality issue summary"
    )

    logger.info(
        df["quality_issue"]
        .value_counts()
    )

    return df


# ----------------------------------------
# Clean
# ----------------------------------------

def clean(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Cleaning started")

    df = normalize_dates(df)

    df = normalize_text(df)

    df = flag_quality_issues(df)

    logger.info("Cleaning completed")

    return df



# ----------------------------------------
# Validate
# ----------------------------------------

def validate(df: pd.DataFrame):

    logger.info("Validation started")

    # Valid rows have no quality issues
    valid_mask = (
        df["quality_issue"]
        .fillna("")
        .str.strip()
        == ""
    )

    valid_df = (
        df[valid_mask]
        .copy()
        .reset_index(drop=True)
    )

    quarantine_df = (
        df[~valid_mask]
        .copy()
        .reset_index(drop=True)
    )

    logger.info(f"Valid records      : {len(valid_df)}")
    logger.info(f"Quarantine records : {len(quarantine_df)}")

    return valid_df, quarantine_df

def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        database="vigilyx_complaints",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        port=5432
    )

    return conn
# ----------------------------------------
# Load
# ----------------------------------------

def load(valid_df: pd.DataFrame):

    logger.info("Loading records into PostgreSQL")

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO complaints
        (
            complaint_id,
            product_code,
            received_date,
            close_date,
            event_description,
            imdrf_code,
            regulatory_market,
            status
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s, %s, %s
        )

        ON CONFLICT (complaint_id)

        DO UPDATE SET

            product_code = EXCLUDED.product_code,
            received_date = EXCLUDED.received_date,
            close_date = EXCLUDED.close_date,
            event_description = EXCLUDED.event_description,
            imdrf_code = EXCLUDED.imdrf_code,
            regulatory_market = EXCLUDED.regulatory_market,
            status = EXCLUDED.status;
        """

        for _, row in valid_df.iterrows():

            cursor.execute(
                sql,
                (
                    row["complaint_id"],
                    row["product_code"],
                    None if pd.isna(row["received_date"]) else row["received_date"],
                    None if pd.isna(row["close_date"]) else row["close_date"],
                    None if pd.isna(row["event_description"]) else row["event_description"],
                    row["imdrf_code"],
                    row["regulatory_market"],
                    row["status"]
                )
            )

        conn.commit()

        logger.info(f"Successfully loaded {len(valid_df)} records.")

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(f"Database load failed: {e}")

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

        logger.info("Database connection closed.")


def main():

    input_file = (
        "phase1-data-engineering/etl/"
        "messy_trackwise_export.csv"
    )

    cleaned_output = (
        "phase1-data-engineering/etl/"
        "cleaned_trackwise_export.csv"
    )

    valid_output = (
        "phase1-data-engineering/etl/"
        "valid_records.csv"
    )

    quarantine_output = (
        "phase1-data-engineering/etl/"
        "quarantine_records.csv"
    )

    df = extract(input_file)

    cleaned_df = clean(df)

    cleaned_df.to_csv(
        cleaned_output,
        index=False
    )

    valid_df, quarantine_df = validate(cleaned_df)

    load(valid_df)

    valid_df.to_csv(
        valid_output,
        index=False
    )

    quarantine_df.to_csv(
        quarantine_output,
        index=False
    )

    logger.info("Validation completed successfully.")
    logger.info(f"Cleaned records written to {cleaned_output}")
    logger.info(f"Valid records written to {valid_output}")
    logger.info(f"Quarantine records written to {quarantine_output}")

if __name__ == "__main__":
    main()

