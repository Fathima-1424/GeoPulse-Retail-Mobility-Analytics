
SELECT *
FROM {{ ref('int_gps_movement') }}
WHERE time_difference_seconds < 0