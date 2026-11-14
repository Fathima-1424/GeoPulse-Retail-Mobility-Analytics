
select
    device_id,
    event_timestamp,
    count(*) as record_count
from {{ ref('stg_gps_pings') }}
group by
    device_id,
    event_timestamp
having count(*) > 1
