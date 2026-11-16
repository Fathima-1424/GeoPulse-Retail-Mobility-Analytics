
{{ config(
    materialized = 'table'
) }}

WITH movement AS (

    SELECT *
    FROM {{ ref('int_gps_movement') }}

),

device_kpis AS (

    SELECT

        DEVICE_ID,

        MIN(EVENT_TIMESTAMP) AS FIRST_PING_TIMESTAMP,

        MAX(EVENT_TIMESTAMP) AS LAST_PING_TIMESTAMP,

        COUNT(*) AS TOTAL_GPS_PINGS,

        COUNT(DISTANCE_METERS) AS VALID_DISTANCE_INTERVALS,

        COUNT(SPEED_KMH) AS VALID_SPEED_INTERVALS,

       
        SUM(DISTANCE_METERS) / 1000
            AS TOTAL_DISTANCE_KM,

        AVG(SPEED_KMH)
            AS AVG_SPEED_KMH,

        MAX(SPEED_KMH)
            AS MAX_SPEED_KMH,


        ROUND(
            SUM(TIME_DIFFERENCE_SECONDS) / 3600,
            2
        ) AS TOTAL_OBSERVED_INTERVAL_HOURS

    FROM movement

    GROUP BY DEVICE_ID

)

SELECT *
FROM device_kpis
