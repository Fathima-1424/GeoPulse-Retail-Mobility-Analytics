# GeoPulse - Store Visit and Cannibalization Analysis

## 1. Objective
To develop a GPS-based store geofence mapping
process and identify devices visiting multiple
store locations.

## 2. Activities
- Implemented Haversine distance calculation.
- Prepared GPS-to-store geofence mapping.
- Identified device-store visit records.
- Calculated unique stores visited by each device.
- Prepared store overlap analysis.
- Generated analysis reports.

## 3. Tools Used
- Python
- Pandas
- NumPy
- GPS Data
- VS Code

## 4. Scripts
- store_visit_mapping.py
- cannibalization_analysis.py

## 5. Expected Outputs
- gps_store_geofence_matches.csv
- device_store_visits.csv
- device_cannibalization_summary.csv
- store_overlap_summary.csv

## 6. Observation
Store coordinates are required to generate
actual GPS-to-store matches.

The analysis measures device overlap between
stores and does not independently prove sales
cannibalization.

## 7. Conclusion
Developed the initial geofence mapping and
multi-store device analysis workflow for
future cannibalization analysis.