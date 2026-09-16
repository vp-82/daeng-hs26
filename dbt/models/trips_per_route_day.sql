-- Grain: one row = one route x one service day.
-- count(*) is correct here only because stg_trips is one row per trip,
-- and a test guarantees that.

select
    sd.service_day,
    t.route,
    count(*) as trips
from {{ ref('stg_trips') }} t
join {{ ref('stg_service_days') }} sd on sd.service_id = t.service_id
group by 1, 2
