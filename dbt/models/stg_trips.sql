-- Grain: one row = one trip.
-- Trips come from trips.txt. stop_times.txt has one row per stop and is not
-- touched here. The unique test on trip_id in schema.yml guards this grain.

select
    t.trip_id,
    t.route_id,
    r.route_short_name as route,
    t.service_id
from {{ source('gtfs', 'trips') }} t
join {{ source('gtfs', 'routes') }} r on r.route_id = t.route_id
