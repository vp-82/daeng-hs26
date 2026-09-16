"""Download the full Swiss GTFS feed and write stop_times as Parquet.

Lecturer only. Run once before class, from the repo root:

    uv run python tools/prepare_full_feed.py
    uv run python tools/prepare_full_feed.py --url <newer zip url>

The current zip is linked from
https://data.opentransportdata.swiss/en/dataset/timetable-2026-gtfs2020
The feed is re-published weekly, so the file name changes. Copy the newest
link from that page if the default below has gone stale.

Output goes to data/full/, which is gitignored. Students never need it.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import time
import urllib.request
import zipfile

import duckdb

DEFAULT_URL = (
    "https://data.opentransportdata.swiss/dataset/"
    "3d2c18f9-9ef1-463f-a249-5c67604efd74/resource/"
    "940f970d-1ab6-4320-9c7e-f8dc5a2af48d/download/gtfs_fp2026_20260729.zip"
)
FILES = ["stop_times.txt", "trips.txt", "routes.txt", "calendar.txt", "stops.txt"]

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "full"


def mb(path: pathlib.Path) -> str:
    return f"{path.stat().st_size / 1e6:,.0f} MB"


def download(url: str, target: pathlib.Path) -> None:
    if target.exists():
        print(f"zip already present: {target} ({mb(target)})")
        return
    print(f"downloading {url}")

    def report(blocks, block_size, total):
        done = blocks * block_size / 1e6
        sys.stdout.write(f"\r  {done:,.0f} MB" + (f" of {total / 1e6:,.0f} MB" if total > 0 else ""))
        sys.stdout.flush()

    urllib.request.urlretrieve(url, target, reporthook=report)
    print(f"\n  saved {target} ({mb(target)})")


def extract(zip_path: pathlib.Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        names = set(z.namelist())
        for name in FILES:
            if name not in names:
                print(f"  {name} not in zip, skipped")
                continue
            target = OUT / name
            if target.exists():
                print(f"  {name} already extracted ({mb(target)})")
                continue
            z.extract(name, OUT)
            print(f"  {name} ({mb(target)})")


def to_parquet() -> None:
    src = OUT / "stop_times.txt"
    dst = OUT / "stop_times.parquet"
    if dst.exists():
        print(f"parquet already present: {dst} ({mb(dst)})")
        return
    print("converting stop_times.txt to Parquet")
    t0 = time.perf_counter()
    con = duckdb.connect()
    con.execute(
        f"""
        COPY (
          SELECT * FROM read_csv('{src}', header=true, all_varchar=true)
        ) TO '{dst}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    rows = con.execute(f"SELECT COUNT(*) FROM '{dst}'").fetchone()[0]
    print(f"  {rows:,} rows, {mb(src)} as text, {mb(dst)} as Parquet, {time.perf_counter() - t0:.1f}s")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    zip_path = OUT / "gtfs.zip"
    download(args.url, zip_path)
    print("extracting")
    extract(zip_path)
    to_parquet()
    print(f"\ndone. Open the scale demo with: uv run marimo edit notebooks/02_scale.py")


if __name__ == "__main__":
    main()
