-- LECTURER DEMO. The wrong grain, on purpose.
-- Copy this over models/stg_trips.sql, run dbt build, watch the unique test fail.
-- Restore with: git checkout dbt/models/stg_trips.sql

select
    t.trip_id,
    t.route_id,
    r.route_short_name as route,
    t.service_id
from {{ source('gtfs', 'stop_times') }} st
join {{ source('gtfs', 'trips') }} t on t.trip_id = st.trip_id
join {{ source('gtfs', 'routes') }} r on r.route_id = t.route_id
