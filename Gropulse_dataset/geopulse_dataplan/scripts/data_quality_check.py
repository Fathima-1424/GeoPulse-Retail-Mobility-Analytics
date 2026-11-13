
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "geopulse_cleaned_pings.csv"
REPORT_PATH = BASE_DIR / "reports" / "data_quality_report.txt"

# Read dataset
df = pd.read_csv(CSV_PATH)

required_columns = [
    "DeviceID", "Latitude", "Longitude", "Timestamp"
]

# Check required columns
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Validation checks
total_records = len(df)
missing_values = df[required_columns].isnull().sum()

duplicate_records = df.duplicated().sum()

latitude = pd.to_numeric(df["Latitude"], errors="coerce")
longitude = pd.to_numeric(df["Longitude"], errors="coerce")

invalid_latitude = (
    latitude.isna() | ~latitude.between(-90, 90)
).sum()

invalid_longitude = (
    longitude.isna() | ~longitude.between(-180, 180)
).sum()

timestamps = pd.to_datetime(
    df["Timestamp"], errors="coerce"
)
invalid_timestamps = timestamps.isna().sum()

invalid_device_ids = (
    df["DeviceID"].isna()
    | df["DeviceID"].astype("string").str.strip().eq("")
).sum()

# Create report
report = f"""
GEOPULSE - GPS DATA QUALITY REPORT
==================================

Total Records: {total_records}

1. MISSING VALUES
{missing_values.to_string()}

2. DUPLICATE RECORDS
Duplicate Rows: {duplicate_records}

3. LATITUDE VALIDATION
Invalid Latitude Values: {invalid_latitude}

4. LONGITUDE VALIDATION
Invalid Longitude Values: {invalid_longitude}

5. TIMESTAMP VALIDATION
Invalid Timestamps: {invalid_timestamps}

6. DEVICE ID VALIDATION
Invalid DeviceIDs: {invalid_device_ids}

7. OVERALL SUMMARY
Data Quality Checks Completed Successfully.
"""

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(report, encoding="utf-8")

print(report)
print("Data quality report generated successfully!")
