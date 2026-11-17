
import pandas as pd
from pathlib import Path
import sys

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Check dataset path
if len(sys.argv) < 2:
    print("Usage: python scripts/geographic_analysis.py <dataset_path>")
    sys.exit(1)

INPUT_FILE = Path(sys.argv[1])

if not INPUT_FILE.is_absolute():
    INPUT_FILE = (Path.cwd() / INPUT_FILE).resolve()

if not INPUT_FILE.exists():
    print("ERROR: Dataset file not found:", INPUT_FILE)
    sys.exit(1)

# Output folders
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

print("Loading GPS dataset...")

df = pd.read_csv(INPUT_FILE)

# Standardize column names
df.columns = df.columns.str.strip().str.lower()

required_columns = [
    "deviceid",
    "latitude",
    "longitude",
    "timestamp"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("Missing columns:", missing_columns)
    sys.exit(1)

# Original record count
total_records = len(df)

# Convert coordinates to numeric
df["latitude"] = pd.to_numeric(
    df["latitude"], errors="coerce"
)

df["longitude"] = pd.to_numeric(
    df["longitude"], errors="coerce"
)

# Convert timestamp
df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)

# Identify invalid records
invalid_coordinates = (
    df["latitude"].isna()
    | df["longitude"].isna()
    | ~df["latitude"].between(-90, 90)
    | ~df["longitude"].between(-180, 180)
)

invalid_timestamps = df["timestamp"].isna()

# Keep valid geographical records
valid_df = df.loc[~invalid_coordinates].copy()

# Remove records without valid device IDs
valid_df = valid_df.dropna(subset=["deviceid"])

# Round coordinates to group nearby GPS points
valid_df["latitude_group"] = (
    valid_df["latitude"].round(3)
)

valid_df["longitude_group"] = (
    valid_df["longitude"].round(3)
)

# Group locations
location_summary = (
    valid_df.groupby(
        ["latitude_group", "longitude_group"]
    )
    .agg(
        total_pings=("deviceid", "size"),
        unique_devices=("deviceid", "nunique")
    )
    .reset_index()
)

# Rank locations by GPS activity
location_summary = location_summary.sort_values(
    "total_pings",
    ascending=False
)

location_summary.insert(
    0,
    "location_rank",
    range(1, len(location_summary) + 1)
)

# Save CSV
csv_output = OUTPUT_DIR / "location_summary.csv"

location_summary.to_csv(
    csv_output,
    index=False
)

# Geographic statistics
latitude_min = valid_df["latitude"].min()
latitude_max = valid_df["latitude"].max()

longitude_min = valid_df["longitude"].min()
longitude_max = valid_df["longitude"].max()

latitude_center = valid_df["latitude"].mean()
longitude_center = valid_df["longitude"].mean()

unique_devices = valid_df["deviceid"].nunique()

# Top 10 locations
top_locations = location_summary.head(10)

# Generate report
report = []

report.append("GEOPULSE - GEOGRAPHICAL ANALYSIS REPORT")
report.append("=" * 50)

report.append(f"Total GPS records: {total_records}")
report.append(f"Valid geographical records: {len(valid_df)}")
report.append(
    f"Invalid coordinate records: {invalid_coordinates.sum()}"
)
report.append(
    f"Invalid timestamp records: {invalid_timestamps.sum()}"
)

report.append(f"Unique devices: {unique_devices}")
report.append(
    f"Unique grouped locations: {len(location_summary)}"
)

report.append("\nGEOGRAPHICAL BOUNDARIES")
report.append("-" * 50)

report.append(f"Minimum Latitude: {latitude_min}")
report.append(f"Maximum Latitude: {latitude_max}")
report.append(f"Minimum Longitude: {longitude_min}")
report.append(f"Maximum Longitude: {longitude_max}")

report.append("\nAVERAGE LOCATION")
report.append("-" * 50)

report.append(f"Average Latitude: {latitude_center}")
report.append(f"Average Longitude: {longitude_center}")

report.append("\nTOP 10 ACTIVE LOCATIONS")
report.append("-" * 50)

report.append(
    top_locations.to_string(index=False)
)

report.append("\nANALYSIS NOTES")
report.append("-" * 50)

report.append(
    "Nearby GPS coordinates are grouped using "
    "3-decimal-place rounding."
)

report.append(
    "Location activity is measured using GPS ping counts."
)

report.append(
    "These results represent synthetic GPS activity, "
    "not confirmed retail footfall."
)

# Save report
report_output = (
    REPORT_DIR / "geographic_analysis_report.txt"
)

report_output.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("\nGeographical analysis completed!")

print("Valid GPS records:", len(valid_df))
print("Unique devices:", unique_devices)

print("\nTop 5 active locations:")
print(top_locations.head().to_string(index=False))

print("\nFiles generated:")
print(csv_output)
print(report_output)

