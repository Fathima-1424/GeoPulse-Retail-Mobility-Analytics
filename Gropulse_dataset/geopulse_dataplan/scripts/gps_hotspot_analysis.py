
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "geopulse_dataplan" / "data" / "geopulse_cleaned_pings.csv"
OUTPUT_DIR = BASE_DIR / "geopulse_dataplan" / "outputs"
REPORT_DIR = BASE_DIR / "geopulse_dataplan" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load GPS data
df = pd.read_csv(INPUT_FILE)

# Validate required columns
required_columns = ["DeviceID", "Latitude", "Longitude", "Timestamp"]

if not all(col in df.columns for col in required_columns):
    raise ValueError("Required GPS columns are missing.")

# Clean coordinate values
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df = df.dropna(subset=["Latitude", "Longitude"])

# Group nearby GPS coordinates
df["Latitude_Grid"] = df["Latitude"].round(3)
df["Longitude_Grid"] = df["Longitude"].round(3)

# Identify hotspots
hotspots = (
    df.groupby(["Latitude_Grid", "Longitude_Grid"])
    .agg(
        Total_Pings=("DeviceID", "count"),
        Unique_Devices=("DeviceID", "nunique")
    )
    .reset_index()
)

hotspots = hotspots.sort_values(
    by="Total_Pings", ascending=False
).reset_index(drop=True)

hotspots.insert(0, "Hotspot_Rank", range(1, len(hotspots) + 1))

# Save all hotspot results
hotspots.to_csv(
    OUTPUT_DIR / "gps_hotspot_summary.csv",
    index=False
)

# Save top 10 hotspots
top_10 = hotspots.head(10)
top_10.to_csv(
    OUTPUT_DIR / "top_10_gps_hotspots.csv",
    index=False
)

# Generate report
total_records = len(df)
total_devices = df["DeviceID"].nunique()
total_hotspots = len(hotspots)

with open(REPORT_DIR / "gps_hotspot_report.txt", "w") as report:
    report.write("GEOPULSE GPS HOTSPOT ANALYSIS REPORT\n")
    report.write("=" * 45 + "\n\n")
    report.write(f"Total GPS Records: {total_records}\n")
    report.write(f"Total Unique Devices: {total_devices}\n")
    report.write(f"Total Identified Hotspots: {total_hotspots}\n\n")
    report.write("TOP 10 GPS HOTSPOTS\n")
    report.write("-" * 45 + "\n")
    report.write(top_10.to_string(index=False))
    report.write("\n\nAnalysis Method:\n")
    report.write(
        "GPS coordinates were rounded to 3 decimal places "
        "and grouped to identify frequently recorded locations.\n"
    )
    report.write(
        "Ping counts represent GPS recording frequency, "
        "not confirmed customer footfall.\n"
    )

print("GPS HOTSPOT ANALYSIS COMPLETED!")
print("Total Records:", total_records)
print("Unique Devices:", total_devices)
print("Total Hotspots:", total_hotspots)
print("\nTop 10 Hotspots:")
print(top_10.to_string(index=False))
print("\nOutput files saved successfully.")
