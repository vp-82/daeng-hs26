import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import pathlib

    ROOT = pathlib.Path(__file__).resolve().parent.parent
    RAW = ROOT / "raw"
    con = duckdb.connect()

    def table(name):
        return con.execute(f"SELECT * FROM read_csv('{RAW}/{name}.txt', header=true)").df()

    routes = table("routes")
    trips = table("trips")
    stop_times = table("stop_times")
    calendar = table("calendar")
    return ROOT, calendar, con, mo, routes, stop_times, trips


@app.cell
def _(mo):
    mo.md("""
    # How many trips does each route run per day?

    The cell above loads the four files in `raw/` as tables named
    `routes`, `trips`, `stop_times` and `calendar`. Every query below uses these names.

    Before counting anything, look at what one row is.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. One trip in stop_times
    """)
    return


@app.cell
def _(con, stop_times):
    con.execute("""
        SELECT trip_id, stop_sequence, departure_time, stop_id
        FROM stop_times
        WHERE trip_id = 'IC1.001'
        ORDER BY stop_sequence
    """).df()
    return


@app.cell
def _(mo):
    mo.md("""
    Four rows, one trip. `stop_times` has **one row per stop**. Counting its rows
    counts stops, not trips.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Where the day comes from
    """)
    return


@app.cell
def _(calendar):
    calendar
    return


@app.cell
def _(mo):
    mo.md("""
    This is the only place in the feed with a date. A trip has a `service_id`, and
    `calendar` says on which weekdays that service runs, between `start_date` and `end_date`.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Times that are not clock times
    """)
    return


@app.cell
def _(con, stop_times):
    con.execute("""
        SELECT trip_id, stop_sequence, departure_time
        FROM stop_times
        WHERE departure_time >= '24:'
        ORDER BY trip_id, stop_sequence
    """).df()
    return


@app.cell
def _(mo):
    mo.md("""
    24:17:00 means 17 minutes past midnight, on the service day that started the
    evening before. These values are text. Converting them to a clock time fails.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. One row per service and day

    The next cell turns `calendar` into a table `service_days` with one row per
    `service_id` and each date it runs. The code is hidden, you do not need to read it.
    """)
    return


@app.cell(hide_code=True)
def _(calendar, con):
    service_days = con.execute("""
        SELECT c.service_id, strftime(d.day, '%Y-%m-%d') AS service_day
        FROM calendar c,
             LATERAL (
               SELECT unnest(generate_series(
                 strptime(c.start_date::VARCHAR, '%Y%m%d'),
                 strptime(c.end_date::VARCHAR,   '%Y%m%d'),
                 INTERVAL 1 DAY))::DATE AS day
             ) d
        WHERE CASE dayofweek(d.day)
                WHEN 0 THEN c.sunday
                WHEN 1 THEN c.monday
                WHEN 2 THEN c.tuesday
                WHEN 3 THEN c.wednesday
                WHEN 4 THEN c.thursday
                WHEN 5 THEN c.friday
                ELSE c.saturday
              END = 1
        ORDER BY service_day, service_id
    """).df()
    service_days
    return (service_days,)


@app.cell
def _(mo):
    mo.md("""
    WOCHENENDE is missing. The feed covers weekdays only, so a weekend-only service
    runs on no day in it. That is correct, not missing data.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. The answer

    One row = one route on one day. Trips are counted in `trips`. `stop_times` is not used.
    """)
    return


@app.cell
def _(con, routes, service_days, trips):
    answer = con.execute("""
        SELECT sd.service_day, r.route_short_name AS route, COUNT(*) AS trips
        FROM trips t
        JOIN routes r        ON r.route_id = t.route_id
        JOIN service_days sd ON sd.service_id = t.service_id
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).df()
    answer
    return (answer,)


@app.cell
def _(answer, mo):
    mo.md(f"""
    **{len(answer)} rows. Routes present: {', '.join(sorted(answer['route'].unique()))}.**

    IR 75 is 17 on every day. Remember that number.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. What changed in the feed

    Run this after `git merge origin/feat/day-three`. The folder `out/main/` still
    holds the feed as it was before the merge. EXCEPT returns the rows that are new.
    """)
    return


@app.cell
def _(ROOT, con, trips):
    con.execute(f"""
        SELECT * FROM trips
        EXCEPT
        SELECT * FROM read_csv('{ROOT}/out/main/trips.txt', header=true)
    """).df()
    return


@app.cell
def _(ROOT, calendar, con):
    con.execute(f"""
        SELECT * FROM calendar
        EXCEPT
        SELECT * FROM read_csv('{ROOT}/out/main/calendar.txt', header=true)
    """).df()
    return


@app.cell
def _(mo):
    mo.md("""
    Before the merge both tables are empty. After it: one new trip on IR 75, and
    the calendar now ends on Wednesday instead of Tuesday. That is the whole change.
    """)
    return


if __name__ == "__main__":
    app.run()
