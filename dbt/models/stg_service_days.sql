-- One row per service_id and the date it actually runs.
-- The date is not invented. It is declared in calendar.txt.

select
    c.service_id,
    d.day::date as service_day
from {{ source('gtfs', 'calendar') }} c,
lateral (
    select unnest(generate_series(
        strptime(c.start_date::varchar, '%Y%m%d'),
        strptime(c.end_date::varchar,   '%Y%m%d'),
        interval 1 day))::date as day
) d
where case dayofweek(d.day)
        when 0 then c.sunday
        when 1 then c.monday
        when 2 then c.tuesday
        when 3 then c.wednesday
        when 4 then c.thursday
        when 5 then c.friday
        else c.saturday
      end = 1
