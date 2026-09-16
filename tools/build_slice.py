"""Build the frozen GTFS teaching slice.

Two outputs:
  out/main/        the feed that lives on `main`   (Mon + Tue)
  out/day_three/   the feed that arrives via `feat/day-three` (Mon-Wed, one duplicated journey)

Run:  uv run python tools/build_slice.py
"""

from __future__ import annotations

import csv
import pathlib
import random

SEED = 20260914
random.seed(SEED)

OUT = pathlib.Path(__file__).resolve().parent.parent / "out"

STOPS = [
    ("8503000", "Zurich HB", 47.378177, 8.540192),
    ("8503006", "Zurich Oerlikon", 47.411526, 8.544115),
    ("8506000", "Winterthur", 47.500366, 8.723876),
    ("8503016", "Uster", 47.352528, 8.717516),
    ("8503060", "Wetzikon ZH", 47.326159, 8.797302),
    ("8503202", "Rapperswil", 47.225670, 8.816401),
    ("8502113", "Thalwil", 47.294510, 8.564341),
    ("8502204", "Zug", 47.174060, 8.515232),
    ("8502207", "Baar", 47.195595, 8.529395),
    ("8505000", "Luzern", 47.050170, 8.310180),
    ("8500218", "Olten", 47.351935, 7.907707),
    ("8500120", "Aarau", 47.391361, 8.051253),
    ("8507000", "Bern", 46.948832, 7.439122),
]

# route_id, short_name, long_name, route_type (2 = rail)
ROUTES = [
    ("IC1", "IC 1", "Zurich HB - Olten - Bern", "2"),
    ("IR75", "IR 75", "Zurich HB - Zug - Luzern", "2"),
    ("S3", "S 3", "Zurich HB - Thalwil", "2"),
    ("S5", "S 5", "Zurich HB - Uster - Wetzikon ZH", "2"),
    ("S7", "S 7", "Zurich HB - Winterthur", "2"),
    ("S15", "S 15", "Zurich HB - Rapperswil", "2"),
]

# route_id -> ordered stop_ids
PATTERNS = {
    "IC1": ["8503000", "8500120", "8500218", "8507000"],
    "IR75": ["8503000", "8502113", "8502207", "8502204", "8505000"],
    "S3": ["8503000", "8502113"],
    "S5": ["8503000", "8503006", "8503016", "8503060"],
    "S7": ["8503000", "8503006", "8506000"],
    "S15": ["8503000", "8503016", "8503060", "8503202"],
}

# route_id -> (service_id, first departure hour, last departure hour, trips per hour)
#   WERKTAG  runs Mon-Fri
#   TAEGLICH runs every day
#   WOCHENENDE runs Sat+Sun only  -> zero trips on Mon-Wed, the trap for "every trip runs every day"
SERVICE = {
    "IC1": ("TAEGLICH", 6, 21, 1),
    "IR75": ("TAEGLICH", 6, 22, 1),
    "S3": ("WERKTAG", 5, 23, 2),
    "S5": ("WERKTAG", 5, 23, 2),
    "S7": ("TAEGLICH", 5, 24, 2),  # last departure crosses midnight -> 24:xx times
    "S15": ("WOCHENENDE", 8, 18, 1),
}

CALENDAR_MAIN = [
    # service_id, mon..sun, start_date, end_date
    ("TAEGLICH", 1, 1, 1, 1, 1, 1, 1, "20260914", "20260915"),
    ("WERKTAG", 1, 1, 1, 1, 1, 0, 0, "20260914", "20260915"),
    ("WOCHENENDE", 0, 0, 0, 0, 0, 1, 1, "20260914", "20260915"),
]

CALENDAR_DAY_THREE = [
    ("TAEGLICH", 1, 1, 1, 1, 1, 1, 1, "20260914", "20260916"),
    ("WERKTAG", 1, 1, 1, 1, 1, 0, 0, "20260914", "20260916"),
    ("WOCHENENDE", 0, 0, 0, 0, 0, 1, 1, "20260914", "20260916"),
]


def hhmmss(total_minutes: int) -> str:
    """GTFS time. Hours may exceed 24 for journeys past midnight."""
    h, m = divmod(total_minutes, 60)
    return f"{h:02d}:{m:02d}:00"


def build_trips_and_times():
    trips, stop_times = [], []
    for route_id, _short, _long, _rtype in ROUTES:
        service_id, first_h, last_h, per_hour = SERVICE[route_id]
        pattern = PATTERNS[route_id]
        headsign = next(n for sid, n, _la, _lo in STOPS if sid == pattern[-1])
        n = 0
        for hour in range(first_h, last_h + 1):
            for slot in range(per_hour):
                n += 1
                trip_id = f"{route_id}.{n:03d}"
                depart = hour * 60 + slot * (60 // per_hour) + 7
                trips.append(
                    {
                        "route_id": route_id,
                        "service_id": service_id,
                        "trip_id": trip_id,
                        "trip_headsign": headsign,
                        "direction_id": "0",
                    }
                )
                t = depart
                for seq, stop_id in enumerate(pattern, start=1):
                    stop_times.append(
                        {
                            "trip_id": trip_id,
                            "arrival_time": hhmmss(t),
                            "departure_time": hhmmss(t if seq == 1 else t + 1),
                            "stop_id": stop_id,
                            "stop_sequence": str(seq),
                        }
                    )
                    t += random.choice([9, 11, 12, 14, 16])
    return trips, stop_times


def duplicate_journey(trips, stop_times, source_trip_id, new_trip_id):
    """Republish one journey under a fresh trip_id. Same route, same times, same headsign.

    This is the Session 1 surprise: the feed is not wrong row by row, but any
    aggregation that trusts trip_id as the identity of a journey now counts it twice.
    """
    src = next(t for t in trips if t["trip_id"] == source_trip_id)
    trips.append({**src, "trip_id": new_trip_id})
    for row in [r for r in stop_times if r["trip_id"] == source_trip_id]:
        stop_times.append({**row, "trip_id": new_trip_id})
    return trips, stop_times


def write_feed(folder: pathlib.Path, calendar_rows, trips, stop_times):
    folder.mkdir(parents=True, exist_ok=True)

    def dump(name, header, rows):
        with open(folder / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)

    dump(
        "stops.txt",
        ["stop_id", "stop_name", "stop_lat", "stop_lon"],
        [[s, n, f"{la:.6f}", f"{lo:.6f}"] for s, n, la, lo in STOPS],
    )
    dump(
        "routes.txt",
        ["route_id", "route_short_name", "route_long_name", "route_type"],
        [list(r) for r in ROUTES],
    )
    dump(
        "calendar.txt",
        [
            "service_id", "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday", "start_date", "end_date",
        ],
        [list(r) for r in calendar_rows],
    )
    dump(
        "trips.txt",
        ["route_id", "service_id", "trip_id", "trip_headsign", "direction_id"],
        [[t["route_id"], t["service_id"], t["trip_id"], t["trip_headsign"], t["direction_id"]] for t in trips],
    )
    dump(
        "stop_times.txt",
        ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"],
        [
            [r["trip_id"], r["arrival_time"], r["departure_time"], r["stop_id"], r["stop_sequence"]]
            for r in stop_times
        ],
    )
    print(f"{folder.name:12s} trips={len(trips):4d}  stop_times={len(stop_times):5d}")


def main():
    trips, stop_times = build_trips_and_times()

    write_feed(OUT / "main", CALENDAR_MAIN, list(trips), list(stop_times))

    d_trips, d_times = duplicate_journey(
        list(trips), list(stop_times), source_trip_id="IR75.009", new_trip_id="IR75.909"
    )
    write_feed(OUT / "day_three", CALENDAR_DAY_THREE, d_trips, d_times)


if __name__ == "__main__":
    main()
