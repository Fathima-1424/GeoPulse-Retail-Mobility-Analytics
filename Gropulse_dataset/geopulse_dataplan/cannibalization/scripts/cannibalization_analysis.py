from pathlib import Path
from itertools import combinations
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "cannibalization" / "outputs"
    / "device_store_visits.csv"
)

OUTPUT_DIR = BASE_DIR / "cannibalization" / "outputs"
REPORT_DIR = BASE_DIR / "cannibalization" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DEVICE_OUTPUT = OUTPUT_DIR / "device_cannibalization_summary.csv"
OVERLAP_OUTPUT = OUTPUT_DIR / "store_overlap_summary.csv"
REPORT_FILE = REPORT_DIR / "cannibalization_analysis_report.txt"

required = ["DeviceID", "StoreID", "StoreName"]

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Run store_visit_mapping.py first."
    )

visits = pd.read_csv(INPUT_FILE)

for column in required:
    if column not in visits.columns:
        raise ValueError(f"Required column missing: {column}")

if visits.empty:
    device_summary = pd.DataFrame(columns=[
        "DeviceID", "UniqueStoresVisited", "VisitedMultipleStores"
    ])
    overlap_summary = pd.DataFrame(columns=[
        "StoreA", "StoreB", "SharedDevices"
    ])
else:
    # Count unique stores visited by each device
    device_summary = (
        visits.groupby("DeviceID")["StoreID"]
        .nunique()
        .reset_index(name="UniqueStoresVisited")
    )

    device_summary["VisitedMultipleStores"] = (
        device_summary["UniqueStoresVisited"] > 1
    )

    # Find pairs of stores visited by the same device
    device_store_sets = (
        visits.groupby("DeviceID")["StoreID"]
        .apply(lambda values: sorted(set(values)))
    )

    pair_counts = {}

    for store_list in device_store_sets:
        for store_a, store_b in combinations(store_list, 2):
            pair = (store_a, store_b)
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    overlap_summary = pd.DataFrame([
        {
            "StoreA": pair[0],
            "StoreB": pair[1],
            "SharedDevices": count
        }
        for pair, count in pair_counts.items()
    ], columns=["StoreA", "StoreB", "SharedDevices"])

# Save outputs
device_summary.to_csv(DEVICE_OUTPUT, index=False)
overlap_summary.to_csv(OVERLAP_OUTPUT, index=False)

total_devices = len(device_summary)

if total_devices:
    multiple_store_devices = int(
        device_summary["VisitedMultipleStores"].sum()
    )
    percentage = (
        multiple_store_devices / total_devices
    ) * 100
else:
    multiple_store_devices = 0
    percentage = 0.0

# Generate report
with open(REPORT_FILE, "w", encoding="utf-8") as report:
    report.write("CANNIBALIZATION ANALYSIS REPORT\n")
    report.write("===============================\n\n")
    report.write(f"Devices mapped to stores: {total_devices}\n")
    report.write(
        f"Devices visiting multiple stores: "
        f"{multiple_store_devices}\n"
    )
    report.write(
        f"Multiple-store device percentage: {percentage:.2f}%\n"
    )
    report.write(
        f"Store pairs with shared devices: {len(overlap_summary)}\n\n"
    )

    if visits.empty:
        report.write(
            "No store visit records are available.\n"
            "Add real store coordinates and run the mapping script "
            "before interpreting cannibalization results.\n"
        )
    else:
        report.write(
            "This analysis measures device overlap between stores.\n"
            "It is a mobility-based overlap indicator, not proof "
            "of sales cannibalization.\n"
        )

print("Cannibalization analysis completed.")
print(f"Device summary: {DEVICE_OUTPUT}")
print(f"Store overlap: {OVERLAP_OUTPUT}")
print(f"Report: {REPORT_FILE}")