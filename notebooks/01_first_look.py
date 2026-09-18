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

    def sql(query):
        return con.execute(query).df()
    return ROOT, calendar, mo, routes, sql, stop_times, trips


@app.cell
def _(mo):
    mo.md("""
    # Tutorial notebook

    This notebook belongs to `TUTORIAL.md` in the repository. The step numbers are the same.

    The cell above loads the four files in `raw/` as tables called `routes`, `trips`,
    `stop_times` and `calendar`, and defines `sql(...)`, which runs a query and shows the result.

    To run a cell: click into it and press **Ctrl+Enter** (Mac: **Cmd+Enter**).
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    # Part 2. Look at the data
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 2.1  A whole table
    """)
    return


@app.cell
def _(sql):
    sql("SELECT * FROM routes")
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 2.2  The first rows of a big table
    """)
    return


@app.cell
def _(sql):
    sql("SELECT * FROM trips LIMIT 5")
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 2.3  Only the rows you want
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT *
        FROM stop_times
        WHERE trip_id = 'IC1.001'
        ORDER BY stop_sequence
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 2.4  How many rows
    """)
    return


@app.cell
def _(sql):
    sql("SELECT COUNT(*) AS rows FROM trips")
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 2.5  How many rows per group
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT route_id, COUNT(*) AS rows
        FROM trips
        GROUP BY route_id
        ORDER BY route_id
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 2.6  Two tables together
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT t.trip_id, t.route_id, r.route_short_name
        FROM trips t
        JOIN routes r ON r.route_id = t.route_id
        LIMIT 5
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    # Part 3. Two answers to one question
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 3.1  Count with stop_times
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT r.route_short_name AS route, COUNT(*) AS trips
        FROM stop_times st
        JOIN trips t  ON t.trip_id = st.trip_id
        JOIN routes r ON r.route_id = t.route_id
        GROUP BY route
        ORDER BY route
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 3.2  Count with trips only
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT r.route_short_name AS route, COUNT(*) AS trips
        FROM trips t
        JOIN routes r ON r.route_id = t.route_id
        GROUP BY route
        ORDER BY route
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 3.3  Which one is right?

    Go back to Step 2.3. One trip, four rows. Now look at IC 1 in 3.1 and 3.2.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    # Part 4. Per day
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 4.1  The only file with dates
    """)
    return


@app.cell
def _(calendar):
    calendar
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step 4.2  One row per service and date

    The next cell turns `calendar` into a table `service_days`. Its code is hidden.
    You do not need to read it, only to know that the table exists.
    """)
    return


@app.cell(hide_code=True)
def _(calendar, sql):
    _ = calendar
    service_days = sql("""
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
    """)
    service_days
    return (service_days,)


@app.cell
def _(mo):
    mo.md("""
    ### Step 4.3  The answer
    """)
    return


@app.cell
def _(service_days, sql):
    _ = service_days
    sql("""
        SELECT sd.service_day, r.route_short_name AS route, COUNT(*) AS trips
        FROM trips t
        JOIN routes r        ON r.route_id = t.route_id
        JOIN service_days sd ON sd.service_id = t.service_id
        GROUP BY sd.service_day, route
        ORDER BY sd.service_day, route
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    # Part 6. The data changes

    Run these two cells only after Step 6.2 in the tutorial (`git merge`).
    Before the merge they are empty.
    """)
    return


@app.cell
def _(ROOT, sql):
    sql(f"""
        SELECT * FROM trips
        EXCEPT
        SELECT * FROM read_csv('{ROOT}/out/main/trips.txt', header=true)
    """)
    return


@app.cell
def _(ROOT, sql):
    sql(f"""
        SELECT * FROM calendar
        EXCEPT
        SELECT * FROM read_csv('{ROOT}/out/main/calendar.txt', header=true)
    """)
    return


if __name__ == "__main__":
    app.run()
