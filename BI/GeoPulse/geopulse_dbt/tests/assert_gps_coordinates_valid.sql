
select *
from {{ ref('stg_gps_pings') }}
where
    latitude < -90
    or latitude > 90
    or longitude < -180
    or longitude > 180
