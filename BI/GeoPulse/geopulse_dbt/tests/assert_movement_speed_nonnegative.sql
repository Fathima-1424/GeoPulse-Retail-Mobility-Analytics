
SELECT *
FROM {{ ref('int_gps_movement') }}
WHERE speed_meters_per_second < 0
   OR speed_kmh < 0