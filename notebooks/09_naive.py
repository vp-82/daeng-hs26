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
    # Lecturer only: the two numbers that usually appear on the board

    Do not demo these. Use them to recognise what students produced.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A. Joined stop_times and counted rows (stops, not trips)
    """)
    return


@app.cell
def _(RAW, con):
    counted_stops = con.execute(
        f"""
        SELECT r.route_short_name AS route, COUNT(*) AS trips
        FROM read_csv('{RAW}/stop_times.txt', header=true) st
        JOIN read_csv('{RAW}/trips.txt', header=true) t ON t.trip_id = st.trip_id
        JOIN read_csv('{RAW}/routes.txt', header=true) r ON r.route_id = t.route_id
        GROUP BY 1 ORDER BY 1
        """
    ).df()
    counted_stops
    return


@app.cell
def _(mo):
    mo.md("""
    ## B. Counted trips.txt and ignored the day (S 15 shows 11, it runs on no day in the feed)
    """)
    return


@app.cell
def _(RAW, con):
    ignored_day = con.execute(
        f"""
        SELECT r.route_short_name AS route, COUNT(*) AS trips
        FROM read_csv('{RAW}/trips.txt', header=true) t
        JOIN read_csv('{RAW}/routes.txt', header=true) r ON r.route_id = t.route_id
        GROUP BY 1 ORDER BY 1
        """
    ).df()
    ignored_day
    return


if __name__ == "__main__":
    app.run()
