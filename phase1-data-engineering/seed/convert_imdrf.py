import pandas as pd

df = pd.read_excel(
    "data/TW_Complaint_Export_2021_2024.xlsx"
)

a_codes = (
    df[["IMDRF_A_Code", "IMDRF_A_Description"]]
    .rename(
        columns={
            "IMDRF_A_Code": "imdrf_code",
            "IMDRF_A_Description": "description"
        }
    )
)

a_codes["code_level"] = "A"

e_codes = (
    df[["IMDRF_E_Code", "IMDRF_E_Description"]]
    .rename(
        columns={
            "IMDRF_E_Code": "imdrf_code",
            "IMDRF_E_Description": "description"
        }
    )
)

e_codes["code_level"] = "E"

f_codes = (
    df[["IMDRF_F_Code", "IMDRF_F_Description"]]
    .rename(
        columns={
            "IMDRF_F_Code": "imdrf_code",
            "IMDRF_F_Description": "description"
        }
    )
)

f_codes["code_level"] = "F"

imdrf = pd.concat(
    [a_codes, e_codes, f_codes],
    ignore_index=True
)

imdrf = (
    imdrf
    .dropna(subset=["imdrf_code"])
    .drop_duplicates(subset=["imdrf_code"])
    .sort_values("imdrf_code")
)

print(imdrf.head())

print(f"\nTotal IMDRF Codes : {len(imdrf)}")

imdrf.to_csv(
    "phase1-data-engineering/seed/imdrf_codes_from_trackwise.csv",
    index=False
)

print("\nCSV created successfully.")