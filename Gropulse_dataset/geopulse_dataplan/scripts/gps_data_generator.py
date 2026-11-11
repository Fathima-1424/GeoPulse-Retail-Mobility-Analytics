import pandas as pd
import numpy as np
from pathlib import Path

# GeoPulse Week 1: synthetic GPS mobility data generator.
# This creates MOCK data only; it is not real person/device tracking.

rng = np.random.default_rng(42)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

NUM_DEVICES = 1000
PINGS_PER_DEVICE = 100

# Illustrative Chennai-area coordinate centers.
zones = np.array([
    [13.0827, 80.2707],
    [13.0604, 80.2496],
    [13.0475, 80.2090],
    [13.0108, 80.2337],
    [13.0358, 80.2615],
    [13.1067, 80.2206],
    [12.9915, 80.2180],
])

rows = []
base_date = pd.Timestamp("2026-11-01 06:00:00")

for device_num in range(1, NUM_DEVICES + 1):
    device_id = f"D{device_num:06d}"
    start = zones[rng.integers(0, len(zones))]
    end = zones[rng.integers(0, len(zones))]
    start_time = base_date + pd.Timedelta(minutes=int(rng.integers(0, 720)))

    for ping_num in range(PINGS_PER_DEVICE):
        progress = ping_num / (PINGS_PER_DEVICE - 1)
        latitude = start[0] + (end[0] - start[0]) * progress
        longitude = start[1] + (end[1] - start[1]) * progress
        latitude += rng.normal(0, 0.0012)
        longitude += rng.normal(0, 0.0012)
        timestamp = start_time + pd.Timedelta(minutes=5 * ping_num)
        rows.append([
            device_id,
            round(float(latitude), 6),
            round(float(longitude), 6),
            timestamp
        ])

df = pd.DataFrame(
    rows,
    columns=["DeviceID", "Latitude", "Longitude", "Timestamp"]
)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df = df.dropna().drop_duplicates()
df = df[
    df["Latitude"].between(-90, 90) &
    df["Longitude"].between(-180, 180)
]
df = df.sort_values(["DeviceID", "Timestamp"]).reset_index(drop=True)

csv_path = DATA_DIR / "geopulse_cleaned_pings.csv"
df.to_csv(csv_path, index=False, date_format="%Y-%m-%d %H:%M:%S")

report = f"""GEOPULSE - DATA VALIDATION REPORT
Data type: Synthetic / Mock GPS data (not real device tracking)

Total records: {len(df)}
Unique devices: {df['DeviceID'].nunique()}
Missing values: {int(df.isnull().sum().sum())}
Duplicate records: {int(df.duplicated().sum())}
Invalid latitude values: {int((~df['Latitude'].between(-90, 90)).sum())}
Invalid longitude values: {int((~df['Longitude'].between(-180, 180)).sum())}

Columns: {', '.join(df.columns)}
Status: Validation completed.
"""
(REPORT_DIR / "data_validation_report.txt").write_text(report, encoding="utf-8")
print(report)
print(f"CSV saved to: {csv_path}")
