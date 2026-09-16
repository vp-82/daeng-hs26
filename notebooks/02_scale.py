import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import pathlib
    import time

    FULL = pathlib.Path(__file__).resolve().parent.parent / "data" / "full"
    TXT = FULL / "stop_times.txt"
    PQ = FULL / "stop_times.parquet"
    con = duckdb.connect()

    def mb(p):
        return f"{p.stat().st_size / 1e6:,.0f} MB"
    return FULL, PQ, TXT, con, mb, mo, time


@app.cell
def _(PQ, TXT, mb, mo):
    mo.md(f"""
    # Lecturer only: the same question on the whole of Switzerland

    Files come from `tools/prepare_full_feed.py`.

    | file | size |
    |---|---|
    | stop_times.txt | {mb(TXT) if TXT.exists() else "missing, run the script"} |
    | stop_times.parquet | {mb(PQ) if PQ.exists() else "missing, run the script"} |

    The question at this scale: how many rows does stop_times have, and how many
    trips is that? Same grain lesson, 30 million rows instead of 540.
    """)
    return


@app.cell
def _(mo):
    run_pandas = mo.ui.run_button(label="Run the pandas version (expect tens of seconds and a few GB of RAM)")
    run_pandas
    return (run_pandas,)


@app.cell
def _(TXT, mo, run_pandas, time):
    mo.stop(not run_pandas.value, mo.md("*pandas has not run yet.*"))
    import pandas as pd

    _t0 = time.perf_counter()
    _df = pd.read_csv(TXT)
    _rows = len(_df)
    _trips = _df["trip_id"].nunique()
    _seconds = time.perf_counter() - _t0
    mo.md(f"**pandas:** {_rows:,} rows, {_trips:,} trips, **{_seconds:.1f} s**")
    return


@app.cell
def _(TXT, con, mo, time):
    _t0 = time.perf_counter()
    _r = con.execute(
        f"SELECT COUNT(*) AS rows, COUNT(DISTINCT trip_id) AS trips FROM read_csv('{TXT}', header=true)"
    ).fetchone()
    _seconds = time.perf_counter() - _t0
    mo.md(f"**DuckDB on the .txt:** {_r[0]:,} rows, {_r[1]:,} trips, **{_seconds:.1f} s**")
    return


@app.cell
def _(PQ, con, mo, time):
    _t0 = time.perf_counter()
    _r = con.execute(
        f"SELECT COUNT(*) AS rows, COUNT(DISTINCT trip_id) AS trips FROM '{PQ}'"
    ).fetchone()
    _seconds = time.perf_counter() - _t0
    mo.md(f"**DuckDB on Parquet:** {_r[0]:,} rows, {_r[1]:,} trips, **{_seconds:.1f} s**")
    return


@app.cell
def _(mo):
    mo.md("""
    ## Types survive in Parquet, and 24:17:00 is still text
    """)
    return


@app.cell
def _(PQ, con):
    con.execute(
        f"""
        SELECT trip_id, stop_sequence, departure_time
        FROM '{PQ}'
        WHERE departure_time >= '24:'
        ORDER BY departure_time DESC
        LIMIT 5
        """
    ).df()
    return


@app.cell
def _(FULL, con, mo):
    mo.md("## Trips per route per day, whole country, same query as the slice")
    _q = f"""
    WITH service_days AS (
      SELECT c.service_id, d.day::DATE AS service_day
      FROM read_csv('{FULL}/calendar.txt', header=true) c,
           LATERAL (SELECT unnest(generate_series(
             strptime(c.start_date::VARCHAR, '%Y%m%d'),
             strptime(c.end_date::VARCHAR,   '%Y%m%d'),
             INTERVAL 1 DAY))::DATE AS day) d
      WHERE CASE dayofweek(d.day)
              WHEN 0 THEN c.sunday WHEN 1 THEN c.monday WHEN 2 THEN c.tuesday
              WHEN 3 THEN c.wednesday WHEN 4 THEN c.thursday WHEN 5 THEN c.friday
              ELSE c.saturday END = 1
        AND d.day = DATE '2026-09-14'
    )
    SELECT r.route_short_name AS route, COUNT(*) AS trips
    FROM read_csv('{FULL}/trips.txt', header=true) t
    JOIN read_csv('{FULL}/routes.txt', header=true) r ON r.route_id = t.route_id
    JOIN service_days sd ON sd.service_id = t.service_id
    WHERE r.route_short_name IN ('IC1', 'IC 1', 'IR75', 'IR 75')
    GROUP BY 1 ORDER BY 1
    """
    con.execute(_q).df()
    return


if __name__ == "__main__":
    app.run()
