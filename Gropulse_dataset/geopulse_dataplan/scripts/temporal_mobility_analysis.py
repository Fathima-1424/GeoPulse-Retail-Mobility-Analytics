
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "geopulse_cleaned_pings.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load GPS dataset
df = pd.read_csv(INPUT_FILE)

# Validate required columns
required_columns = ["DeviceID", "Timestamp"]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

# Convert timestamp
df["Timestamp"] = pd.to_datetime(
    df["Timestamp"], errors="coerce"
)

df = df.dropna(subset=["Timestamp"]).copy()

# Extract time details
df["Hour"] = df["Timestamp"].dt.hour
df["Day"] = df["Timestamp"].dt.day_name()
df["Date"] = df["Timestamp"].dt.date

# Hour-wise mobility analysis
hourly = df.groupby("Hour").agg(
    Total_Records=("DeviceID", "count"),
    Active_Devices=("DeviceID", "nunique")
).reset_index()

# Day-wise mobility analysis
daily = df.groupby("Day").agg(
    Total_Records=("DeviceID", "count"),
    Active_Devices=("DeviceID", "nunique")
).reset_index()

# Date-wise mobility analysis
datewise = df.groupby("Date").agg(
    Total_Records=("DeviceID", "count"),
    Active_Devices=("DeviceID", "nunique")
).reset_index()

# Save results
hourly.to_csv(
    OUTPUT_DIR / "hourly_mobility_patterns.csv",
    index=False
)

daily.to_csv(
    OUTPUT_DIR / "daily_mobility_patterns.csv",
    index=False
)

datewise.to_csv(
    OUTPUT_DIR / "datewise_mobility_patterns.csv",
    index=False
)

# Identify peak periods
peak_hour = hourly.loc[hourly["Total_Records"].idxmax()]
peak_day = daily.loc[daily["Total_Records"].idxmax()]

# Generate report
report = f"""
GEOPULSE - TEMPORAL MOBILITY ANALYSIS
=====================================

Total GPS Records: {len(df)}
Unique Devices: {df['DeviceID'].nunique()}

Peak Movement Hour: {int(peak_hour['Hour'])}:00
Peak Hour Records: {int(peak_hour['Total_Records'])}

Most Active Day: {peak_day['Day']}
Most Active Day Records: {int(peak_day['Total_Records'])}

Analysis:
Hourly and daily movement patterns were
analysed using GPS timestamp data.

Generated using Python and Pandas.
"""

with open(
    REPORT_DIR / "temporal_mobility_report.txt",
    "w",
    encoding="utf-8"
) as file:
    file.write(report)

print("TEMPORAL MOBILITY ANALYSIS COMPLETED!")
print(report)
print("Output files saved successfully.")
