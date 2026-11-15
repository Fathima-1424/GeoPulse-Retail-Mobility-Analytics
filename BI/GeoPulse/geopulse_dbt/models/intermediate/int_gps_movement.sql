
WITH gps_with_previous AS (

    SELECT
        device_id,
        latitude,
        longitude,
        event_timestamp,
        location,
        loaded_at,

        LAG(event_timestamp) OVER (
            PARTITION BY device_id
            ORDER BY event_timestamp
        ) AS previous_event_timestamp,

        LAG(latitude) OVER (
            PARTITION BY device_id
            ORDER BY event_timestamp
        ) AS previous_latitude,

        LAG(longitude) OVER (
            PARTITION BY device_id
            ORDER BY event_timestamp
        ) AS previous_longitude

    FROM {{ ref('stg_gps_pings') }}

),

movement_calculations AS (

    SELECT
        device_id,
        latitude,
        longitude,
        event_timestamp,
        location,
        loaded_at,

        previous_event_timestamp,
        previous_latitude,
        previous_longitude,

        CASE
            WHEN previous_latitude IS NOT NULL
                 AND previous_longitude IS NOT NULL
            THEN ST_MAKEPOINT(
                previous_longitude,
                previous_latitude
            )
        END AS previous_location,

        CASE
            WHEN previous_latitude IS NOT NULL
                 AND previous_longitude IS NOT NULL
            THEN ST_DISTANCE(
                location,
                ST_MAKEPOINT(
                    previous_longitude,
                    previous_latitude
                )
            )
        END AS distance_meters,

        CASE
            WHEN previous_event_timestamp IS NOT NULL
            THEN DATEDIFF(
                'second',
                previous_event_timestamp,
                event_timestamp
            )
        END AS time_difference_seconds

    FROM gps_with_previous

),

final AS (

    SELECT
        *,

        CASE
            WHEN time_difference_seconds > 0
            THEN distance_meters / time_difference_seconds
        END AS speed_meters_per_second,

        CASE
            WHEN time_difference_seconds > 0
            THEN (distance_meters / time_difference_seconds) * 3.6
        END AS speed_kmh

    FROM movement_calculations

)

SELECT *
FROM final
