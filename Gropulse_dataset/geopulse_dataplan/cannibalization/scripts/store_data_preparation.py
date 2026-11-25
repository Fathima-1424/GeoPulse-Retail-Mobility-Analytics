from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "cannibalization" / "data" / "store_locations.csv"
)

OUTPUT_DIR = BASE_DIR / "cannibalization" / "outputs"
REPORT_DIR = BASE_DIR / "cannibalization" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

required = [
    "StoreID",
    "StoreName",
    "Latitude",
    "Longitude",
    "GeofenceRadiusMeters"
]

missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

if df.empty:
    result = pd.DataFrame(columns=required + ["ValidationStatus"])

    report_text = (
        "STORE LOCATION VALIDATION REPORT\n"
        "================================\n\n"
        "Store CSV template exists.\n"
        "No real store records have been added yet.\n"
        "Store coordinates are required for future analysis.\n"
    )

else:
    for col in ["Latitude", "Longitude", "GeofenceRadiusMeters"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    valid = (
        df["StoreID"].notna()
        & df["StoreName"].notna()
        & df["Latitude"].between(-90, 90)
        & df["Longitude"].between(-180, 180)
        & df["GeofenceRadiusMeters"].gt(0)
    )

    df["ValidationStatus"] = "Invalid"
    df.loc[valid, "ValidationStatus"] = "Valid"

    result = df

    report_text = (
        "STORE LOCATION VALIDATION REPORT\n"
        "================================\n\n"
        f"Total stores: {len(df)}\n"
        f"Valid stores: {int(valid.sum())}\n"
        f"Invalid stores: {int((~valid).sum())}\n"
    )

result.to_csv(
    OUTPUT_DIR / "store_location_validation.csv",
    index=False
)

with open(
    REPORT_DIR / "store_location_report.txt",
    "w",
    encoding="utf-8"
) as report:
    report.write(report_text)

print("Store data preparation completed!")
print("Store validation output and report generated.")