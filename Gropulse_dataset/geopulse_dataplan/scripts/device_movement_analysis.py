
import pandas as pd
import numpy as np
import os

# ==========================================
# STEP 1: LOAD DATASET
# ==========================================

file_path = "geopulse_dataplan/data/geopulse_cleaned_pings.csv"

df = pd.read_csv(file_path)

print("GPS Dataset Loaded Successfully!")
print("Total Records:", len(df))


# ==========================================
# STEP 2: DATA CLEANING AND SORTING
# ==========================================

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"], errors="coerce"
)

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

df = df.dropna(
    subset=["DeviceID", "Latitude", "Longitude", "Timestamp"]
)

df = df[
    df["Latitude"].between(-90, 90) &
    df["Longitude"].between(-180, 180)
].copy()

df = df.sort_values(
    by=["DeviceID", "Timestamp"]
).reset_index(drop=True)

print("Cleaned Records:", len(df))
print("Unique Devices:", df["DeviceID"].nunique())


# ==========================================
# STEP 3: IDENTIFY PREVIOUS GPS LOCATIONS
# ==========================================

df["Previous_Latitude"] = (
    df.groupby("DeviceID")["Latitude"].shift(1)
)

df["Previous_Longitude"] = (
    df.groupby("DeviceID")["Longitude"].shift(1)
)

df["Previous_Timestamp"] = (
    df.groupby("DeviceID")["Timestamp"].shift(1)
)


# ==========================================
# STEP 4: HAVERSINE DISTANCE CALCULATION
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    return earth_radius * c


df["Distance_km"] = calculate_distance(
    df["Previous_Latitude"],
    df["Previous_Longitude"],
    df["Latitude"],
    df["Longitude"]
)

# First record of each device has no previous point
df.loc[df["Previous_Timestamp"].isna(), "Distance_km"] = np.nan


# ==========================================
# STEP 5: TIME DIFFERENCE CALCULATION
# ==========================================

df["Time_Difference_Minutes"] = (
    df["Timestamp"] - df["Previous_Timestamp"]
).dt.total_seconds() / 60


# ==========================================
# STEP 6: SPEED CALCULATION
# ==========================================

df["Speed_kmh"] = (
    df["Distance_km"] /
    (df["Time_Difference_Minutes"] / 60)
)

# Invalid or non-positive time gaps cannot produce valid speed
df.loc[
    df["Time_Difference_Minutes"] <= 0,
    "Speed_kmh"
] = np.nan

df.replace([np.inf, -np.inf], np.nan, inplace=True)


# ==========================================
# STEP 7: IDENTIFY HIGH-SPEED RECORDS
# ==========================================

# 120 km/h is used as an exploratory screening threshold,
# not a verified travel-speed limit.
df["Possible_High_Speed"] = df["Speed_kmh"] > 120

high_speed_count = int(df["Possible_High_Speed"].sum())


# ==========================================
# STEP 8: DEVICE-WISE MOVEMENT SUMMARY
# ==========================================

summary = df.groupby("DeviceID").agg(
    Total_Pings=("DeviceID", "size"),
    Total_Distance_km=("Distance_km", "sum"),
    Average_Speed_kmh=("Speed_kmh", "mean"),
    Maximum_Speed_kmh=("Speed_kmh", "max"),
    Movement_Count=("Distance_km", "count"),
    High_Speed_Count=("Possible_High_Speed", "sum")
).reset_index()

summary = summary.round(3)


# ==========================================
# STEP 9: GENERATE OUTPUT FOLDERS
# ==========================================

output_folder = "geopulse_dataplan/outputs"
report_folder = "geopulse_dataplan/reports"

os.makedirs(output_folder, exist_ok=True)
os.makedirs(report_folder, exist_ok=True)


# ==========================================
# STEP 10: SAVE CSV FILES
# ==========================================

summary_file = os.path.join(
    output_folder,
    "device_movement_summary.csv"
)

details_file = os.path.join(
    output_folder,
    "device_movement_details.csv"
)

summary.to_csv(summary_file, index=False)

df.to_csv(details_file, index=False)


# ==========================================
# STEP 11: GENERATE TEXT REPORT
# ==========================================

valid_distances = df["Distance_km"].dropna()
valid_speeds = df["Speed_kmh"].dropna()

report_file = os.path.join(
    report_folder,
    "device_movement_report.txt"
)

with open(report_file, "w", encoding="utf-8") as report:

    report.write("GEOPULSE - DEVICE MOVEMENT ANALYSIS REPORT\n")
    report.write("=" * 50 + "\n\n")

    report.write(f"Total GPS Records: {len(df)}\n")
    report.write(f"Total Unique Devices: {df['DeviceID'].nunique()}\n")
    report.write(f"Valid Movement Records: {len(valid_distances)}\n")
    report.write(f"Invalid Time Gaps: {(df['Time_Difference_Minutes'] <= 0).sum()}\n\n")

    report.write("MOVEMENT STATISTICS\n")
    report.write("-" * 30 + "\n")

    report.write(
        f"Total Distance (km): {valid_distances.sum():.3f}\n"
    )

    report.write(
        f"Average Distance (km): {valid_distances.mean():.3f}\n"
    )

    report.write(
        f"Average Speed (km/h): {valid_speeds.mean():.3f}\n"
    )

    report.write(
        f"Maximum Speed (km/h): {valid_speeds.max():.3f}\n"
    )

    report.write(
        f"Possible High-Speed Records (>120 km/h): {high_speed_count}\n\n"
    )

    report.write("TOP 10 DEVICES BY TOTAL DISTANCE\n")
    report.write("-" * 40 + "\n")

    top_devices = summary.sort_values(
        by="Total_Distance_km",
        ascending=False
    ).head(10)

    report.write(top_devices.to_string(index=False))

    report.write("\n\nANALYSIS NOTES\n")
    report.write("-" * 30 + "\n")

    report.write(
        "Distance was calculated using the Haversine formula.\n"
    )

    report.write(
        "Speed was calculated using distance and time difference.\n"
    )

    report.write(
        "Speeds above 120 km/h are flagged for further review.\n"
    )

    report.write(
        "GPS distance represents straight-line distance between "
        "consecutive recorded points, not actual road distance.\n"
    )


# ==========================================
# STEP 12: DISPLAY RESULTS
# ==========================================

print("\nDEVICE MOVEMENT ANALYSIS COMPLETED!")
print("=" * 45)

print("\nMovement Statistics:")
print("Total Distance (km):", round(valid_distances.sum(), 3))
print("Average Speed (km/h):", round(valid_speeds.mean(), 3))
print("Maximum Speed (km/h):", round(valid_speeds.max(), 3))
print("Possible High-Speed Records:", high_speed_count)

print("\nTop 5 Devices by Distance:")
print(
    summary.sort_values(
        by="Total_Distance_km",
        ascending=False
    ).head(5).to_string(index=False)
)

print("\nGenerated Files:")
print(summary_file)
print(details_file)
print(report_file)
