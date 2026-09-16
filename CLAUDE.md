# Working with the GTFS feed in raw/

Three facts about this feed. Every one of them produces a wrong number if ignored.

1. stop_times.txt has one row per stop, not per trip. A trip with 4 stops
   contributes 4 rows. Count trips from trips.txt, never from stop_times.txt.

2. The operating date is declared in calendar.txt: weekday flags plus a
   start_date and an end_date. Nothing else in the feed carries a date.
   Do not invent one and do not derive one from a time column.

3. Times pass 24:00:00 for journeys that continue after midnight. 24:17:00 is
   17 minutes past midnight on the service day that started. These are text,
   not clock times. Do not cast them to TIME.

Before you show a number, state in one sentence what one row of the result
means. If you cannot, the query is not finished.
