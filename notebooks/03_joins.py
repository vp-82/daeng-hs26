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
    calendar = table("calendar")

    def sql(query):
        return con.execute(query).df()
    return calendar, mo, routes, sql, trips


@app.cell
def _(mo):
    mo.md("""
    # Joins

    Belongs to Appendix A of `TUTORIAL.md`. Same step numbers.

    Two small tables first, so that every row fits on the screen. Then the same joins on the real data.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.1  Two small tables

    `lines` has three lines. `journeys` has four journeys. IC 1 has two, S 3 has one,
    and one journey belongs to a line **S 99 that is not in `lines`**. And S 15 has
    **no journey**. That is on purpose.
    """)
    return


@app.cell
def _(sql):
    sql("""
        CREATE OR REPLACE TABLE lines AS
        SELECT * FROM (VALUES ('IC 1'), ('S 3'), ('S 15')) AS v(line);

        CREATE OR REPLACE TABLE journeys AS
        SELECT * FROM (VALUES ('IC 1', 'j1'), ('IC 1', 'j2'), ('S 3', 'j3'), ('S 99', 'j4')) AS v(line, journey);

        SELECT * FROM lines
    """)
    return


@app.cell
def _(sql):
    sql("SELECT * FROM journeys")
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.2  INNER JOIN: only what matches on both sides
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT l.line, j.journey
        FROM lines l
        INNER JOIN journeys j ON j.line = l.line
        ORDER BY l.line, j.journey
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.3  LEFT JOIN: everything from the left table, matches where they exist
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT l.line, j.journey
        FROM lines l
        LEFT JOIN journeys j ON j.line = l.line
        ORDER BY l.line, j.journey
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.4  RIGHT JOIN: everything from the right table
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT l.line, j.line AS journey_line, j.journey
        FROM lines l
        RIGHT JOIN journeys j ON j.line = l.line
        ORDER BY j.line, j.journey
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.5  FULL OUTER JOIN: everything from both
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT l.line, j.line AS journey_line, j.journey
        FROM lines l
        FULL OUTER JOIN journeys j ON j.line = l.line
        ORDER BY coalesce(l.line, j.line), j.journey
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.6  The trap: counting after a LEFT JOIN
    """)
    return


@app.cell
def _(sql):
    sql("""
        SELECT l.line, COUNT(*) AS count_star, COUNT(j.journey) AS count_journeys
        FROM lines l
        LEFT JOIN journeys j ON j.line = l.line
        GROUP BY l.line
        ORDER BY l.line
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Step A.7  On the real data: which trips have no day?

    `service_days` is the table from Step 4.2 of the tutorial (rebuilt here, code hidden).
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
def _(routes, service_days, sql, trips):
    _ = (routes, trips, service_days)
    sql("""
        SELECT r.route_short_name AS route, t.service_id,
               COUNT(*) AS rows_after_join,
               COUNT(sd.service_day) AS rows_with_a_day
        FROM trips t
        JOIN routes r ON r.route_id = t.route_id
        LEFT JOIN service_days sd ON sd.service_id = t.service_id
        GROUP BY route, t.service_id
        ORDER BY route
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    S 15 survives the LEFT JOIN with 11 rows, but none of them has a day. With the
    plain `JOIN` in Step 4.3 those 11 rows disappear, which is what we want: the
    question is "per day", and S 15 has no day in this data.
    """)
    return


if __name__ == "__main__":
    app.run()
