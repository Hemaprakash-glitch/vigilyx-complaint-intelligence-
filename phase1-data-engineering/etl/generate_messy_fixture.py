import random
import pandas as pd

# ----------------------------------------
# Make the fixture reproducible
# ----------------------------------------
random.seed(42)

EXCEL_FILE = "data/TW_Complaint_Export_2021_2024.xlsx"

df = pd.read_excel(
    EXCEL_FILE,
    sheet_name="Complaints_Raw"
)

# ----------------------------------------
# Verify all workflow states
# ----------------------------------------
print("Workflow States Found:")
print(df["TW_Workflow_State"].unique())

# ----------------------------------------
# Sample 200 rows (reproducible)
# ----------------------------------------
sample = (
    df.sample(
        n=200,
        random_state=42
    )
    .reset_index(drop=True)
)

# ----------------------------------------
# Select required columns
# ----------------------------------------
sample = sample[
    [
        "Complaint_ID",
        "Product_Code_FDA",
        "Date_Complaint_Received",
        "Date_Complaint_Closed",
        "Event_Description_Narrative",
        "IMDRF_A_Code",
        "Regulatory_Market",
        "TW_Workflow_State"
    ]
]

# ----------------------------------------
# Rename to schema fields
# ----------------------------------------
sample = sample.rename(
    columns={
        "Complaint_ID": "complaint_id",
        "Product_Code_FDA": "product_code",
        "Date_Complaint_Received": "received_date",
        "Date_Complaint_Closed": "close_date",
        "Event_Description_Narrative": "event_description",
        "IMDRF_A_Code": "imdrf_code",
        "Regulatory_Market": "regulatory_market",
        "TW_Workflow_State": "status"
    }
)

# ----------------------------------------
# Status Mapping
# ----------------------------------------
status_map = {
    "Open": "Open",
    "Under Investigation": "Investigating",
    "On Hold – Awaiting Sample": "Investigating",
    "Closed – MDR Filed": "Closed",
    "Closed – No MDR": "Closed",
    "Closed – Reportable EU": "Closed",
    "Reopened": "Reopened"
}

sample["status"] = sample["status"].map(status_map)

# Warn if any unmapped status exists
if sample["status"].isna().any():
    print("\nWARNING: Unmapped workflow status detected!")
    print(df["TW_Workflow_State"].unique())

# ----------------------------------------
# Inject Issue 1
# Mixed Date Formats
# ----------------------------------------
date_rows = random.sample(range(len(sample)), 25)

for idx in date_rows:

    if pd.notna(sample.loc[idx, "received_date"]):

        sample.loc[idx, "received_date"] = (
            pd.to_datetime(sample.loc[idx, "received_date"])
            .strftime("%d-%m-%Y")
        )

# Keep remaining rows in ISO format
for idx in range(len(sample)):

    if idx not in date_rows and pd.notna(sample.loc[idx, "received_date"]):

        sample.loc[idx, "received_date"] = (
            pd.to_datetime(sample.loc[idx, "received_date"])
            .strftime("%Y-%m-%d")
        )

sample["received_date"] = sample["received_date"].astype(str)

# ----------------------------------------
# Inject Issue 2
# Null Mandatory Fields
# ----------------------------------------
null_rows = random.sample(range(len(sample)), 12)

for idx in null_rows:

    if random.random() < 0.5:
        sample.loc[idx, "received_date"] = None
    else:
        sample.loc[idx, "event_description"] = None

# ----------------------------------------
# Inject Issue 3
# Orphaned Product Codes
# ----------------------------------------
orphan_rows = random.sample(range(len(sample)), 5)

for idx in orphan_rows:
    sample.loc[idx, "product_code"] = "XXX-999"

# ----------------------------------------
# Inject Issue 4
# Duplicate Complaint ID
# ----------------------------------------
duplicate_row = sample.iloc[[10]].copy()

sample = pd.concat(
    [sample, duplicate_row],
    ignore_index=True
)

duplicates = sample["complaint_id"].duplicated().sum()

print(f"\nDuplicate IDs Created: {duplicates}")

# ----------------------------------------
# Export
# ----------------------------------------
sample.to_csv(
    "phase1-data-engineering/etl/messy_trackwise_export.csv",
    index=False
)

print("Messy fixture exported successfully.")