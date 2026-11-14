
WITH source AS (

    SELECT *
    FROM {{ source('geopulse_raw', 'gps_pings') }}

),

renamed AS (

    SELECT

        NULLIF(TRIM(device_id), '') AS device_id,

        latitude,

        longitude,

        event_timestamp,

        location,

        loaded_at

    FROM source

)

SELECT *
FROM renamed
