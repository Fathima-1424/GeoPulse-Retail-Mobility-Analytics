GeoPulse Week 1 - Synthetic GPS Dataset

This folder contains mock GPS mobility records for development and testing.

 Files
- `scripts/gps_data_generator.py`: Python script to regenerate the dataset.
- `data/geopulse_cleaned_pings.csv`: 100,000 synthetic GPS pings.
- `reports/data_validation_report.txt`: validation summary.

 Schema
- `DeviceID`: anonymous synthetic device identifier
- `Latitude`: latitude in decimal degrees
- `Longitude`: longitude in decimal degrees
- `Timestamp`: timestamp in `YYYY-MM-DD HH:MM:SS` format

Dataset size
- 1,000 synthetic device IDs
- 100 pings per device
- 100,000 total records

Important
This is entirely synthetic/mock data. Coordinates are illustrative Chennai-like sample coordinates.
It does not represent real people, actual mobile-device tracking, or verified retail footfall.
