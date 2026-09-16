import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import pathlib

    RAW = pathlib.Path(__file__).resolve().parent.parent / "raw"
    con = duckdb.connect()
    return RAW, con, mo


@app.cell
def _(mo):
    mo.md("""
    # How many trips does each route run per day?

    Before counting anything, look at what a row is. Every wrong number in this
    session comes from counting rows without knowing what one row means.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. One trip in stop_times.txt
    """)
    return


@app.cell
def _(RAW, con):
    one_trip = con.execute(
        f"""
        SELECT trip_id, stop_sequence, arrival_time, departure_time, stop_id
        FROM read_csv('{RAW}/stop_times.txt', header=true)
        WHERE trip_id = 'IC1.001'
        ORDER BY stop_sequence
        """
    ).df()
    one_trip
    return


@app.cell
def _(mo):
    mo.md("""
    Four rows, one trip. stop_times has **one row per stop**. Anything that joins
    stop_times and counts rows will count stops and call them trips.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Where the day comes from
    """)
    return


@app.cell
def _(RAW, con):
    calendar = con.execute(
        f"SELECT * FROM read_csv('{RAW}/calendar.txt', header=true)"
    ).df()
    calendar
    return


@app.cell
def _(mo):
    mo.md("""
    This is the only place in the feed with a date. A trip does not know when it
    runs. Its service_id does. A service is a set of weekday flags between a
    start and an end date. Nothing runs on a date that is not covered here.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Times that are not clock times
    """)
    return


@app.cell
def _(RAW, con):
    past_midnight = con.execute(
        f"""
        SELECT trip_id, stop_sequence, departure_time
        FROM read_csv('{RAW}/stop_times.txt', header=true)
        WHERE CAST(split_part(departure_time, ':', 1) AS INTEGER) >= 24
        ORDER BY trip_id, stop_sequence
        """
    ).df()
    past_midnight
    return


@app.cell
def _(mo):
    mo.md("""
    24:17:00 is 17 minutes past midnight, published so that the journey stays on
    the service day it started. These are text. Casting them to TIME fails.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Service days: one row per service_id and date
    """)
    return


@app.cell
def _(RAW, con):
    service_days = con.execute(
        f"""
        SELECT c.service_id, d.day::DATE AS service_day
        FROM read_csv('{RAW}/calendar.txt', header=true) c,
             LATERAL (
               SELECT unnest(generate_series(
                 strptime(c.start_date::VARCHAR, '%Y%m%d'),
                 strptime(c.end_date::VARCHAR,   '%Y%m%d'),
                 INTERVAL 1 DAY)) ::DATE AS day
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
        """
    ).df()
    service_days
    return


@app.cell
def _(mo):
    mo.md("""
    WOCHENENDE does not appear. The feed covers weekdays only, so weekend-only
    services run on no day in it. That is correct, not missing data.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. The answer

    One row = one route on one service day. Trips are counted from trips.txt.
    stop_times.txt is not in this query at all.
    """)
    return


@app.cell
def _(RAW, con):
    answer = con.execute(
        f"""
        WITH service_days AS (
          SELECT c.service_id, d.day::DATE AS service_day
          FROM read_csv('{RAW}/calendar.txt', header=true) c,
               LATERAL (
                 SELECT unnest(generate_series(
                   strptime(c.start_date::VARCHAR, '%Y%m%d'),
                   strptime(c.end_date::VARCHAR,   '%Y%m%d'),
                   INTERVAL 1 DAY)) ::DATE AS day
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
        )
        SELECT sd.service_day,
               r.route_short_name AS route,
               COUNT(*) AS trips
        FROM read_csv('{RAW}/trips.txt', header=true) t
        JOIN read_csv('{RAW}/routes.txt', header=true) r
          ON r.route_id = t.route_id
        JOIN service_days sd
          ON sd.service_id = t.service_id
        GROUP BY 1, 2
        ORDER BY 1, 2
        """
    ).df()
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
    ## 6. Your cells

    Übung, steps 1 and 3. Keep both queries here.
    """)
    return


@app.cell
def _():
    # Your own query. Predict the number for one route before you run it.
    return


@app.cell
def _():
    # The query the assistant wrote for you (with CLAUDE.md as context).
    return


if __name__ == "__main__":
    app.run()
