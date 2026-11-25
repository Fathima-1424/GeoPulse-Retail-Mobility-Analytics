from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "geopulse_cleaned_pings.csv"
OUTPUT_DIR = BASE_DIR / "cannibalization" / "outputs"
REPORT_DIR = BASE_DIR / "cannibalization" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

required = ["DeviceID", "Latitude", "Longitude", "Timestamp"]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

valid = (
    df["DeviceID"].notna()
    & df["Latitude"].between(-90, 90)
    & df["Longitude"].between(-180, 180)
    & df["Timestamp"].notna()
)

summary = pd.DataFrame([{
    "total_records": len(df),
    "valid_records": int(valid.sum()),
    "invalid_records": int((~valid).sum()),
    "unique_devices": df.loc[valid, "DeviceID"].nunique(),
    "duplicate_records": int(df.duplicated().sum()),
    "invalid_latitudes": int(
        (~df["Latitude"].between(-90, 90)).sum()
    ),
    "invalid_longitudes": int(
        (~df["Longitude"].between(-180, 180)).sum()
    )
}])

summary.to_csv(
    OUTPUT_DIR / "gps_coordinate_summary.csv",
    index=False
)

with open(
    REPORT_DIR / "gps_data_readiness_report.txt",
    "w",
    encoding="utf-8"
) as report:
    report.write("GPS DATA READINESS REPORT\n")
    report.write("=========================\n\n")
    report.write(summary.to_string(index=False))

print("GPS validation completed!")
print("Summary and report generated successfully.")