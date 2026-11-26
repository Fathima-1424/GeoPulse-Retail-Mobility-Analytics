
{{ config(materialized = 'table') }}

WITH device_segments AS (
    SELECT
        DEVICE_ID,
        TOTAL_DISTANCE_KM,
        AVG_SPEED_KMH,
        MAX_SPEED_KMH,
        TOTAL_GPS_PINGS,

        NTILE(4) OVER (
            ORDER BY TOTAL_DISTANCE_KM
        ) AS DISTANCE_QUARTILE

    FROM {{ ref('fct_mobility_kpis') }}
),

final AS (
    SELECT
        DEVICE_ID,
        TOTAL_DISTANCE_KM,
        AVG_SPEED_KMH,
        MAX_SPEED_KMH,
        TOTAL_GPS_PINGS,
        DISTANCE_QUARTILE,

        CASE DISTANCE_QUARTILE
            WHEN 1 THEN 'Q1 - Low Mobility'
            WHEN 2 THEN 'Q2 - Moderate-Low Mobility'
            WHEN 3 THEN 'Q3 - Moderate-High Mobility'
            WHEN 4 THEN 'Q4 - High Mobility'
        END AS MOBILITY_SEGMENT

    FROM device_segments
)

SELECT *
FROM final
