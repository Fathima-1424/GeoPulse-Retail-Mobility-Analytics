
SELECT *
FROM {{ ref('int_gps_movement') }}
WHERE distance_meters < 0