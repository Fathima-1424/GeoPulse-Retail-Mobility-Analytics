
import pandas as pd
from pathlib import Path

# =====================================
# GEOPULSE - DAY 2 DATASET PROFILING
# =====================================

# 1. File paths
BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = BASE_DIR / "data" / "geopulse_cleaned_pings.csv"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)

# 2. Read GPS dataset
df = pd.read_csv(CSV_PATH, parse_dates=["Timestamp"])

# 3. Dataset overview
total_records = len(df)
total_columns = len(df.columns)
unique_devices = df["DeviceID"].nunique()

first_10 = df.head(10).to_string(index=False)
last_5 = df.tail(5).to_string(index=False)

# 4. Column and datatype analysis
column_info = df.dtypes.to_string()
column_names = list(df.columns)

# 5. Device analysis
device_counts = df.groupby("DeviceID").size()

avg_pings = device_counts.mean()
min_pings = device_counts.min()
max_pings = device_counts.max()

top_10_devices = (
    device_counts.sort_values(ascending=False)
    .head(10).to_string()
)

# 6. Latitude and Longitude analysis
lat_min = df["Latitude"].min()
lat_max = df["Latitude"].max()
lat_avg = df["Latitude"].mean()

long_min = df["Longitude"].min()
long_max = df["Longitude"].max()
long_avg = df["Longitude"].mean()

lat_summary = df["Latitude"].describe().to_string()
long_summary = df["Longitude"].describe().to_string()

# 7. Timestamp analysis
first_time = df["Timestamp"].min()
last_time = df["Timestamp"].max()

unique_dates = df["Timestamp"].dt.date.nunique()

date_wise_count = (
    df.groupby(df["Timestamp"].dt.date)
    .size().to_string()
)

duration = last_time - first_time

# 8. Dataset memory usage
memory_mb = (
    df.memory_usage(deep=True).sum() / (1024 * 1024)
)

# 9. Create detailed report
report = f"""
====================================================
       GEOPULSE - DAY 2 DATA PROFILE REPORT
====================================================

PROJECT:
GeoPulse - Hyper-Local Retail Mobility Analytics

TASK:
GPS Dataset Inspection and Profiling

----------------------------------------------------
1. DATASET OVERVIEW
----------------------------------------------------

Total Records       : {total_records}
Total Columns       : {total_columns}
Unique Devices      : {unique_devices}
Memory Usage        : {memory_mb:.2f} MB

----------------------------------------------------
2. COLUMN INFORMATION
----------------------------------------------------

Column Names:
{column_names}

Column Data Types:
{column_info}

----------------------------------------------------
3. DATASET SAMPLE
----------------------------------------------------

First 10 Records:
{first_10}

Last 5 Records:
{last_5}

----------------------------------------------------
4. DEVICE INFORMATION
----------------------------------------------------

Total Unique Devices: {unique_devices}

Average Pings Per Device: {avg_pings:.2f}
Minimum Pings Per Device: {min_pings}
Maximum Pings Per Device: {max_pings}

Top 10 Devices by Ping Count:
{top_10_devices}

----------------------------------------------------
5. GPS LOCATION ANALYSIS
----------------------------------------------------

LATITUDE:

Minimum Latitude: {lat_min}
Maximum Latitude: {lat_max}
Average Latitude: {lat_avg}

Latitude Statistical Summary:
{lat_summary}

LONGITUDE:

Minimum Longitude: {long_min}
Maximum Longitude: {long_max}
Average Longitude: {long_avg}

Longitude Statistical Summary:
{long_summary}

----------------------------------------------------
6. TIMESTAMP ANALYSIS
----------------------------------------------------

First Recorded Timestamp: {first_time}
Last Recorded Timestamp : {last_time}

Unique Dates: {unique_dates}
Total Time Duration: {duration}

Date-wise GPS Ping Count:
{date_wise_count}

----------------------------------------------------
7. DAY 2 FINDINGS
----------------------------------------------------

1. The GPS dataset was successfully loaded
   using the Pandas library.

2. Dataset records, columns and datatypes
   were inspected.

3. Unique device identifiers and device-wise
   ping distribution were analysed.

4. Minimum, maximum and average GPS
   coordinates were calculated.

5. Timestamp coverage and date-wise
   record distribution were examined.

6. Numerical statistics and dataset
   memory usage were calculated.

----------------------------------------------------
8. CONCLUSION
----------------------------------------------------

Dataset profiling provides a clear understanding
of the structure and characteristics of the
synthetic GPS mobility dataset.

The analysis prepares the dataset for the next
stages of data quality validation and mobility
pattern analysis.

STATUS: DAY 2 PROFILING COMPLETED

====================================================
"""

# 10. Save report
report_path = REPORT_DIR / "data_profile_report.txt"

report_path.write_text(report, encoding="utf-8")

print(report)
print("\nDay 2 profiling completed successfully!")
print(f"Report saved at: {report_path}")
