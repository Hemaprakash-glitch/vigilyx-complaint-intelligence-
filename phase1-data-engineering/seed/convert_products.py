import pandas as pd

# Read TrackWise product list
df = pd.read_csv(
    "phase1-data-engineering/seed/products_from_trackwise.csv"
)

# Rename columns to match schema
df = df.rename(
    columns={
        "Product_Code_FDA": "product_code",
        "Product_Name": "product_name"
    }
)

# Add missing schema columns
df["device_code"] = df["product_code"]
df["launch_date"] = "2020-01-01"

# Reorder columns
df = df[
    [
        "product_code",
        "product_name",
        "device_code",
        "launch_date"
    ]
]

# Save as products.csv
df.to_csv(
    "phase1-data-engineering/seed/products.csv",
    index=False
)

print("products.csv created successfully.")
print(df)