
SELECT *
FROM {{ ref('int_gps_movement') }}
WHERE
    (
        previous_event_timestamp IS NULL
        AND (
            previous_latitude IS NOT NULL
            OR previous_longitude IS NOT NULL
            OR previous_location IS NOT NULL
            OR distance_meters IS NOT NULL
            OR time_difference_seconds IS NOT NULL
            OR speed_kmh IS NOT NULL
        )
    )
    OR
    (
        previous_event_timestamp IS NOT NULL
        AND (
            previous_latitude IS NULL
            OR previous_longitude IS NULL
            OR previous_location IS NULL
            OR distance_meters IS NULL
            OR time_difference_seconds IS NULL
        )
    )