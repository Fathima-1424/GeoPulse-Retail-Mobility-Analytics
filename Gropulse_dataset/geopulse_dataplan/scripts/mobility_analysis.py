
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project folders
BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "geopulse_cleaned_pings.csv"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load GPS dataset
df = pd.read_csv(CSV_PATH)

# Convert timestamp
df["Timestamp"] = pd.to_datetime(
    df["Timestamp"], errors="coerce"
)

# Remove invalid timestamps for analysis
df = df.dropna(subset=["Timestamp"]).copy()

# Sort records
df = df.sort_values(["DeviceID", "Timestamp"])

# 1. Basic statistics
total_records = len(df)
total_devices = df["DeviceID"].nunique()

start_time = df["Timestamp"].min()
end_time = df["Timestamp"].max()

# 2. Device-wise analysis
device_counts = df.groupby("DeviceID").size()

avg_pings = device_counts.mean()
max_pings = device_counts.max()
min_pings = device_counts.min()

top_devices = device_counts.sort_values(
    ascending=False
).head(10)

# 3. Hourly analysis
df["Hour"] = df["Timestamp"].dt.hour

hourly_counts = (
    df.groupby("Hour")
    .size()
    .reindex(range(24), fill_value=0)
)

busiest_hour = hourly_counts.idxmax()
busiest_hour_count = hourly_counts.max()

# 4. Daily analysis
df["Date"] = df["Timestamp"].dt.date

daily_counts = df.groupby("Date").size()

# 5. Location analysis
latitude = pd.to_numeric(df["Latitude"], errors="coerce")
longitude = pd.to_numeric(df["Longitude"], errors="coerce")

# 6. Generate text report
report = f"""
GEOPULSE - MOBILITY ANALYSIS REPORT
===================================

1. DATASET OVERVIEW

Total GPS Records: {total_records}
Total Unique Devices: {total_devices}

2. TIME PERIOD

Start Time: {start_time}
End Time: {end_time}

3. DEVICE-WISE ANALYSIS

Average Pings per Device: {avg_pings:.2f}
Maximum Pings by a Device: {max_pings}
Minimum Pings by a Device: {min_pings}

Top 10 Active Devices:
{top_devices.to_string()}

4. HOURLY PING ANALYSIS

Busiest Hour: {busiest_hour}:00
Pings During Busiest Hour: {busiest_hour_count}

Hourly Ping Counts:
{hourly_counts.to_string()}

5. DAILY PING ANALYSIS

Daily Ping Counts:
{daily_counts.to_string()}

6. LOCATION SUMMARY

Latitude Minimum: {latitude.min()}
Latitude Maximum: {latitude.max()}

Longitude Minimum: {longitude.min()}
Longitude Maximum: {longitude.max()}

7. OVERALL SUMMARY

GPS mobility analysis completed successfully.
"""

report_path = REPORT_DIR / "mobility_analysis_report.txt"
report_path.write_text(report, encoding="utf-8")

# 7. Hourly chart
plt.figure(figsize=(10, 5))
hourly_counts.plot(kind="bar")
plt.title("GPS Pings by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Number of GPS Pings")
plt.tight_layout()
plt.savefig(REPORT_DIR / "hourly_ping_counts.png")
plt.close()

# 8. Top devices chart
plt.figure(figsize=(10, 5))
top_devices.sort_values().plot(kind="barh")
plt.title("Top 10 Active Devices")
plt.xlabel("Number of GPS Pings")
plt.ylabel("Device ID")
plt.tight_layout()
plt.savefig(REPORT_DIR / "top_active_devices.png")
plt.close()

print(report)
print("\nMobility analysis completed successfully!")
print("Report and charts generated in the reports folder.")
