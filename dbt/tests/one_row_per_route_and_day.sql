-- Fails if the final table has more than one row for a route on a day.
-- A passing test means "one row = one route x one day" is true, not assumed.

select service_day, route, count(*) as n
from {{ ref('trips_per_route_day') }}
group by 1, 2
having count(*) > 1
