import pandas as pd

df = pd.read_csv(
    "phase1-data-engineering/etl/valid_records.csv"
)

codes = sorted(df["imdrf_code"].dropna().unique())

print("Distinct IMDRF Codes:")
print(codes)

print("\nTotal Distinct Codes:", len(codes))