from pathlib import Path
from itertools import product
import pandas as pd
import numpy as np

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

GPS_FILE = BASE_DIR / "data" / "geopulse_cleaned_pings.csv"
STORE_FILE = BASE_DIR / "cannibalization" / "data" / "store_locations.csv"

OUTPUT_DIR = BASE_DIR / "cannibalization" / "outputs"
REPORT_DIR = BASE_DIR / "cannibalization" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MATCH_FILE = OUTPUT_DIR / "gps_store_geofence_matches.csv"
VISIT_FILE = OUTPUT_DIR / "device_store_visits.csv"
REPORT_FILE = REPORT_DIR / "store_visit_mapping_report.txt"

MATCH_COLUMNS = [
    "DeviceID", "StoreID", "StoreName", "Timestamp",
    "DistanceMeters", "GeofenceRadiusMeters"
]

VISIT_COLUMNS = [
    "DeviceID", "StoreID", "StoreName",
    "FirstVisit", "LastVisit", "PingCount"
]

# Check input files
if not GPS_FILE.exists():
    raise FileNotFoundError(f"GPS file not found: {GPS_FILE}")

if not STORE_FILE.exists():
    raise FileNotFoundError(f"Store file not found: {STORE_FILE}")

gps = pd.read_csv(GPS_FILE)
stores = pd.read_csv(STORE_FILE)

# Validate GPS columns
gps_required = ["DeviceID", "Latitude", "Longitude", "Timestamp"]
store_required = [
    "StoreID", "StoreName", "Latitude",
    "Longitude", "GeofenceRadiusMeters"
]

for column in gps_required:
    if column not in gps.columns:
        raise ValueError(f"GPS column missing: {column}")

for column in store_required:
    if column not in stores.columns:
        raise ValueError(f"Store column missing: {column}")

# Prepare GPS data
gps["Latitude"] = pd.to_numeric(gps["Latitude"], errors="coerce")
gps["Longitude"] = pd.to_numeric(gps["Longitude"], errors="coerce")
gps["Timestamp"] = pd.to_datetime(gps["Timestamp"], errors="coerce")

gps = gps.dropna(subset=[
    "DeviceID", "Latitude", "Longitude", "Timestamp"
]).copy()

# Prepare store data
for column in ["Latitude", "Longitude", "GeofenceRadiusMeters"]:
    stores[column] = pd.to_numeric(stores[column], errors="coerce")

stores = stores.dropna(subset=store_required).copy()

stores = stores[
    stores["Latitude"].between(-90, 90)
    & stores["Longitude"].between(-180, 180)
    & stores["GeofenceRadiusMeters"].gt(0)
]

# Create empty result first
matches = pd.DataFrame(columns=MATCH_COLUMNS)

# Haversine distance calculation
def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371000

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    return 2 * earth_radius * np.arcsin(np.sqrt(a))


if not stores.empty:
    gps_lat = gps["Latitude"].to_numpy()
    gps_lon = gps["Longitude"].to_numpy()

    best_distance = np.full(len(gps), np.inf)
    best_store_index = np.full(len(gps), -1, dtype=int)

    # Find the nearest store within its geofence
    for store_index, store in enumerate(stores.itertuples(index=False)):
        distances = haversine(
            gps_lat,
            gps_lon,
            store.Latitude,
            store.Longitude
        )

        inside = (
            (distances <= store.GeofenceRadiusMeters)
            & (distances < best_distance)
        )

        best_distance[inside] = distances[inside]
        best_store_index[inside] = store_index

    matched_positions = np.where(best_store_index >= 0)[0]

    if len(matched_positions) > 0:
        matched_gps = gps.iloc[matched_positions].copy()
        matched_stores = stores.iloc[
            best_store_index[matched_positions]
        ].reset_index(drop=True)

        matches = pd.DataFrame({
            "DeviceID": matched_gps["DeviceID"].to_numpy(),
            "StoreID": matched_stores["StoreID"].to_numpy(),
            "StoreName": matched_stores["StoreName"].to_numpy(),
            "Timestamp": matched_gps["Timestamp"].to_numpy(),
            "DistanceMeters": best_distance[matched_positions],
            "GeofenceRadiusMeters":
                matched_stores["GeofenceRadiusMeters"].to_numpy()
        })

# Save GPS-to-store matches
matches.to_csv(MATCH_FILE, index=False)

# Aggregate repeated GPS pings into device-store visits
if matches.empty:
    visits = pd.DataFrame(columns=VISIT_COLUMNS)
else:
    visits = (
        matches.groupby(
            ["DeviceID", "StoreID", "StoreName"],
            as_index=False
        )
        .agg(
            FirstVisit=("Timestamp", "min"),
            LastVisit=("Timestamp", "max"),
            PingCount=("Timestamp", "count")
        )
    )

visits.to_csv(VISIT_FILE, index=False)

# Generate report
with open(REPORT_FILE, "w", encoding="utf-8") as report:
    report.write("STORE VISIT MAPPING REPORT\n")
    report.write("==========================\n\n")
    report.write(f"GPS records checked: {len(gps)}\n")
    report.write(f"Valid store records: {len(stores)}\n")
    report.write(f"GPS pings matched to stores: {len(matches)}\n")
    report.write(f"Unique device-store visits: {len(visits)}\n\n")

    if stores.empty:
        report.write(
            "Store coordinates are not available yet.\n"
            "No real GPS-to-store mapping was performed.\n"
        )
    else:
        report.write(
            "GPS pings were matched to the nearest store "
            "within its configured geofence radius.\n"
        )

print("Store visit mapping completed.")
print(f"GPS-store matches: {MATCH_FILE}")
print(f"Device-store visits: {VISIT_FILE}")
print(f"Report: {REPORT_FILE}")