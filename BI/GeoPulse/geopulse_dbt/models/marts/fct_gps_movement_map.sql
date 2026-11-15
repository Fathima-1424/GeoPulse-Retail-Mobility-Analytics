
{{ config(
    materialized = 'view'
) }}

WITH movement AS (

    SELECT *
    FROM {{ ref('int_gps_movement') }}

),

final AS (

    SELECT
        device_id,

        latitude,
        longitude,

        previous_latitude,
        previous_longitude,

        event_timestamp,
        previous_event_timestamp,

        distance_meters,
        time_difference_seconds,

        speed_meters_per_second,
        speed_kmh,

        loaded_at

    FROM movement

)

SELECT *
FROM final
WHERE latitude IS NOT NULL
  AND longitude IS NOT NULL
