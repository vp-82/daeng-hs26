# Tutorial: one question, one data set, and the tools that keep the answer right

**The question: how many trips does each route run per day?**

You will answer it with a small timetable data set. First you will get two different answers and find out which one is right. Then the data set changes, and you will see what it takes for the answer to stay right.

The tutorial has seven parts. Each part takes 15 to 25 minutes. You can stop after any part and continue later. Every step looks the same:

- **Type this** – one command or one query
- **You should see** – the output, so you know you are on track
- **What it means** – a few sentences
- **Check** – one question you can answer from the output

Two windows are used throughout: a **terminal** (Mac: the app Terminal, Windows: PowerShell) and a **browser** with the notebook. The tutorial says which one to use.

---

## Part 1. Setup

### Step 1.1 Install uv

uv is a program that installs Python and everything a project needs. You install it once.

**Type this, in the terminal**

Mac:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then close the terminal, open a new one, and type:

```
uv --version
```

**You should see** a version number, for example `uv 0.9.4`.

**What it means** uv is installed. If you see "command not found", close the terminal, open a new one, and try again.

### Step 1.2 Get the course repository

**Type this**

```
git clone https://github.com/vp-82/daeng-hs26.git
cd daeng-hs26
```

**You should see** a few lines ending with something like `Receiving objects: 100%`. The second command prints nothing.

**What it means** The first command downloads the folder `daeng-hs26` from GitHub. The second moves you into it. From now on every command in this tutorial is typed from inside this folder. If you are unsure where you are, type `pwd` and the terminal prints the folder.

If git is not installed on your Mac, the first command offers to install it. Say yes, then run the command again. On Windows, install git from git-scm.com.

### Step 1.3 Install what the project needs

**Type this**

```
uv sync
```

**You should see** a list of packages being installed, ending without a red error. It takes about a minute the first time.

**What it means** The file `pyproject.toml` lists what the project needs. The file `uv.lock` pins the exact versions. uv installs all of it into a hidden folder `.venv` inside the project. Because of the lockfile, the project works the same on your laptop as on everyone else's.

### Step 1.4 Open the notebook

**Type this**

```
uv run marimo edit notebooks/01_first_look.py
```

**You should see** a browser tab with the notebook. In the terminal, a line with an address like `http://localhost:2718`. If the browser does not open by itself, copy that address into it.

**What it means** `uv run` means "run this program with the Python of this project". marimo is the notebook. The first cell loads four data files as tables named `routes`, `trips`, `stop_times` and `calendar`. Leave the terminal open, it is what keeps the notebook running. To stop the notebook later, press Ctrl+C in the terminal.

**Check** Does the notebook show the heading "Tutorial notebook"?

---

## Part 2. Look at the data

The folder `raw/` contains five text files. Together they are a timetable in the GTFS format, the format that public transport companies use to publish their schedules. Every query in this part teaches one SQL idea on these files.

| File | One row is | Important columns |
|---|---|---|
| routes.txt | one line, such as IC 1 or S 3 | route_id, route_short_name |
| trips.txt | one journey of one line | trip_id, route_id, service_id |
| stop_times.txt | one stop of one journey | trip_id, stop_sequence, departure_time |
| calendar.txt | one service pattern: which weekdays, from which date to which date | service_id, monday … sunday, start_date, end_date |
| stops.txt | one station | stop_id, stop_name |

The files connect through their id columns. A trip belongs to a route (route_id) and to a service pattern (service_id). A stop time belongs to a trip (trip_id).

**How to run a cell** Click into the cell, press Ctrl+Enter (Mac: Cmd+Enter). The result appears under the cell. All cells in this part are already written. Run them and read the output.

### Step 2.1 A whole table

**Run this cell**

```sql
SELECT * FROM routes
```

**You should see**

```
route_id route_short_name                 route_long_name  route_type
     IC1             IC 1        Zurich HB - Olten - Bern           2
    IR75            IR 75        Zurich HB - Zug - Luzern           2
      S3              S 3             Zurich HB - Thalwil           2
      S5              S 5 Zurich HB - Uster - Wetzikon ZH           2
      S7              S 7          Zurich HB - Winterthur           2
     S15             S 15          Zurich HB - Rapperswil           2
```

**What it means** `SELECT *` means "all columns", `FROM routes` says which table. Six lines in this data set. `route_id` is the technical key, `route_short_name` is the name people use.

**Check** What is the route_id of the S 15?

### Step 2.2 The first rows of a big table

**Run this cell**

```sql
SELECT * FROM trips LIMIT 5
```

**You should see**

```
route_id service_id trip_id trip_headsign  direction_id
     IC1   TAEGLICH IC1.001          Bern             0
     IC1   TAEGLICH IC1.002          Bern             0
     IC1   TAEGLICH IC1.003          Bern             0
     IC1   TAEGLICH IC1.004          Bern             0
     IC1   TAEGLICH IC1.005          Bern             0
```

**What it means** `LIMIT 5` shows only the first five rows. One row is one journey: trip IC1.001 belongs to route IC1 and runs on the days that the service pattern TAEGLICH says. The trip itself does not know its date.

**Check** Which column would you look at to find out on which days IC1.001 runs? (You cannot answer it from this table alone. That is the point of Part 4.)

### Step 2.3 Only the rows you want

**Run this cell**

```sql
SELECT *
FROM stop_times
WHERE trip_id = 'IC1.001'
ORDER BY stop_sequence
```

**You should see**

```
trip_id arrival_time departure_time  stop_id  stop_sequence
IC1.001     06:07:00       06:07:00  8503000              1
IC1.001     06:21:00       06:22:00  8500120              2
IC1.001     06:37:00       06:38:00  8500218              3
IC1.001     06:51:00       06:52:00  8507000              4
```

**What it means** `WHERE` keeps only the rows where the condition is true. `ORDER BY` sorts them. This is one journey, IC1.001, and it has **four rows**, one per stop. Remember this. It is the most important thing in the tutorial.

**Check** At which stop_id does IC1.001 start? (Look it up in `raw/stops.txt` if you want the name.)

### Step 2.4 How many rows

**Run this cell**

```sql
SELECT COUNT(*) AS rows FROM trips
```

**You should see**

```
 rows
  160
```

**What it means** `COUNT(*)` counts rows. `AS rows` gives the column a name. There are 160 journeys in this data set.

**Check** Without running anything: would `SELECT COUNT(*) FROM stop_times` give a bigger or a smaller number? Why?

### Step 2.5 How many rows per group

**Run this cell**

```sql
SELECT route_id, COUNT(*) AS rows
FROM trips
GROUP BY route_id
ORDER BY route_id
```

**You should see**

```
route_id  rows
     IC1    16
    IR75    17
     S15    11
      S3    38
      S5    38
      S7    40
```

**What it means** `GROUP BY route_id` makes one group per route and `COUNT(*)` counts within each group. This is how "per route" is done in SQL. Every "per something" in this tutorial is a GROUP BY.

**Check** Do the six numbers add up to 160?

### Step 2.6 Two tables together

**Run this cell**

```sql
SELECT t.trip_id, t.route_id, r.route_short_name
FROM trips t
JOIN routes r ON r.route_id = t.route_id
LIMIT 5
```

**You should see**

```
trip_id route_id route_short_name
IC1.001      IC1             IC 1
IC1.002      IC1             IC 1
IC1.003      IC1             IC 1
IC1.004      IC1             IC 1
IC1.005      IC1             IC 1
```

**What it means** `JOIN routes r ON r.route_id = t.route_id` attaches to every trip the row from routes that has the same route_id. `t` and `r` are short names for the two tables, so that `t.route_id` and `r.route_id` can be told apart. After the join, every trip carries its readable name.

**Check** How many rows would this query return without `LIMIT 5`? (Hint: a trip has exactly one route.)

That is all the SQL you need: SELECT, WHERE, COUNT, GROUP BY, JOIN.

There are four kinds of JOIN. The one above, plain `JOIN`, keeps only rows that have a match in both tables. Appendix A at the end shows the other three on a table small enough to see every row. Read it now or after Part 4, both work.

---

## Part 3. Two answers to one question

Now the question: how many trips does each route run? Two ways to write it. Both run. They give different numbers.

### Step 3.1 Count with stop_times

The times are in stop_times, so it feels natural to start there.

**Run this cell**

```sql
SELECT r.route_short_name AS route, COUNT(*) AS trips
FROM stop_times st
JOIN trips t  ON t.trip_id = st.trip_id
JOIN routes r ON r.route_id = t.route_id
GROUP BY route
ORDER BY route
```

**You should see**

```
route  trips
 IC 1     64
IR 75     85
 S 15     44
  S 3     76
  S 5    152
  S 7    120
```

**What it means** Three tables joined, grouped by route, counted. The column is called `trips`. The query ran without error. IC 1: 64.

### Step 3.2 Count with trips only

**Run this cell**

```sql
SELECT r.route_short_name AS route, COUNT(*) AS trips
FROM trips t
JOIN routes r ON r.route_id = t.route_id
GROUP BY route
ORDER BY route
```

**You should see**

```
route  trips
 IC 1     16
IR 75     17
 S 15     11
  S 3     38
  S 5     38
  S 7     40
```

**What it means** Same shape, one table less. IC 1: 16.

### Step 3.3 Which one is right?

Go back to Step 2.3. One trip, IC1.001, has four rows in stop_times, one per stop. Every IC 1 trip has four stops. 16 trips × 4 stops = 64 rows.

Step 3.1 counted rows of stop_times and called them trips. It counted stops. Step 3.2 counted rows of trips, and one row of trips is one trip. Step 3.2 is right.

Nothing in the output of 3.1 tells you it is wrong. The column is named `trips`, the number is plausible, the query ran. The only way to know was to look at one trip first and ask: what is one row in the table I am counting?

**Write down one sentence** for each of the two queries, starting with "One row of this result is …". If you cannot finish the sentence for a query, you do not know what it counted.

**Rule 1 of this data set:** stop_times has one row per stop, not per trip. Count trips in trips.txt.

---

## Part 4. Per day

Step 3.2 gives trips per route, but the question says per day. S 15 shows 11 trips. On which day? The trips table cannot say, it has no date.

### Step 4.1 The only file with dates

**Run this cell** (it just shows the calendar table)

**You should see**

```
service_id  monday  tuesday  wednesday  thursday  friday  saturday  sunday  start_date  end_date
  TAEGLICH       1        1          1         1       1         1       1    20260914  20260915
   WERKTAG       1        1          1         1       1         0       0    20260914  20260915
WOCHENENDE       0        0          0         0       0         1       1    20260914  20260915
```

**What it means** Three service patterns. A 1 under a weekday means the pattern runs that day. `start_date` and `end_date` say between which dates. This data set covers 14 and 15 September 2026, a Monday and a Tuesday. WOCHENENDE runs on no day in that range.

**Rule 2 of this data set:** only calendar.txt knows the date. A trip's service_id points to it.

**Check** Every S 15 trip has service_id WOCHENENDE. How many S 15 trips run on Monday 14 September?

### Step 4.2 One row per service and date

The next cell turns the three calendar rows into one row per pattern and date. Its code is hidden on purpose. You do not need to read it, only to know that a table `service_days` now exists.

**Run this cell**

**You should see**

```
service_id service_day
  TAEGLICH  2026-09-14
   WERKTAG  2026-09-14
  TAEGLICH  2026-09-15
   WERKTAG  2026-09-15
```

**What it means** Four rows. Each says: this pattern runs on this date. WOCHENENDE is not there, because there is no weekend in the data. That is correct, not missing data.

### Step 4.3 The answer

**Run this cell**

```sql
SELECT sd.service_day, r.route_short_name AS route, COUNT(*) AS trips
FROM trips t
JOIN routes r        ON r.route_id = t.route_id
JOIN service_days sd ON sd.service_id = t.service_id
GROUP BY sd.service_day, route
ORDER BY sd.service_day, route
```

**You should see**

```
service_day route  trips
 2026-09-14  IC 1     16
 2026-09-14 IR 75     17
 2026-09-14   S 3     38
 2026-09-14   S 5     38
 2026-09-14   S 7     40
 2026-09-15  IC 1     16
 2026-09-15 IR 75     17
 2026-09-15   S 3     38
 2026-09-15   S 5     38
 2026-09-15   S 7     40
```

**What it means** This is Step 3.2 with one more join, to service_days, and one more column in the GROUP BY. One row is now one route on one day. S 15 is gone, because it runs on no day in the data. stop_times is not in the query at all.

**Remember: IR 75 = 17.** This number will change in Part 6.

**Check** Why does the result have 10 rows and not 12?

**One more thing about this data set.** Some departure times in stop_times are written as 24:17:00. That means 17 minutes past midnight, on the day the journey started, so that a late train stays on its own day. These values are text, not clock times. **Rule 3:** do not convert them to a time type, it fails.

The three rules are also in the file `CLAUDE.md` in the repository. That file is written for AI assistants. If you ask an assistant to write a query on this data, give it that file first.

---

## Part 5. The same three steps as a pipeline

You just did three things: build service_days from calendar (4.2), attach route names to trips (2.6), join and count (4.3). In the notebook the results live in memory. Close it and they are gone.

dbt does the same three steps, but each step is a file, each result is a real table in a database, and after each table it runs checks. This part uses the terminal.

### Step 5.1 Look at the three files

**Type this** (Mac) or open the files in any editor

```
cat dbt/models/stg_trips.sql
```

**You should see**

```sql
-- Grain: one row = one trip.
-- Trips come from trips.txt. stop_times.txt has one row per stop and is not
-- touched here. The unique test on trip_id in schema.yml guards this grain.

select
    t.trip_id,
    t.route_id,
    r.route_short_name as route,
    t.service_id
from {{ source('gtfs', 'trips') }} t
join {{ source('gtfs', 'routes') }} r on r.route_id = t.route_id
```

**What it means** This is Step 2.6 as a file. `{{ source('gtfs', 'trips') }}` is dbt's way of saying "the file trips.txt in raw/". The other two files in `dbt/models/` are `stg_service_days.sql` (Step 4.2) and `trips_per_route_day.sql` (Step 4.3). A fourth file, `schema.yml`, lists the checks: for example that `trip_id` in stg_trips must be unique and never empty.

### Step 5.2 Build everything

**Type this**

```
uv run --directory dbt dbt build
```

**You should see** about 30 lines. The important ones:

```
Found 3 models, 8 data tests, 4 sources
1 of 11 OK created sql table model main.stg_service_days
2 of 11 OK created sql table model main.stg_trips
3 of 11 PASS not_null_stg_service_days_service_day
...
6 of 11 PASS unique_stg_trips_trip_id
7 of 11 OK created sql table model main.trips_per_route_day
...
11 of 11 PASS one_row_per_route_and_day

Done. PASS=11 WARN=0 ERROR=0 SKIP=0
```

**What it means** `--directory dbt` means "work inside the dbt folder". dbt read the three SQL files, worked out the order from which file uses which, created three tables in the database file `daeng.duckdb`, and ran eight checks. Every line is one thing it did. `OK created` is a table, `PASS` is a check. The last line is the summary.

**Check** Which table was created last, and why does it have to be last?

### Step 5.3 Break it on purpose

The folder `dbt/demo/` contains a version of stg_trips that is built from stop_times, the mistake from Step 3.1. Put it in place of the real one and build again.

**Type this**

```
cp dbt/demo/stg_trips_from_stop_times.sql dbt/models/stg_trips.sql
uv run --directory dbt dbt build
```

**You should see**

```
6 of 11 FAIL 160 unique_stg_trips_trip_id
7 of 11 SKIP relation main.trips_per_route_day
8 of 11 SKIP test not_null_trips_per_route_day_route
...
  Got 160 results, configured to fail if != 0

Done. PASS=5 WARN=0 ERROR=1 SKIP=5
```

**What it means** The check "trip_id is unique" found 160 trip_ids that appear more than once, because every trip now has one row per stop. dbt marked it FAIL, and then it **skipped** the final table. The wrong number from Step 3.1 was never produced. Nobody read any SQL. The check did the reading.

**Check** Why 160 and not 64?

### Step 5.4 Restore

**Type this**

```
git checkout dbt/models/stg_trips.sql
uv run --directory dbt dbt build
```

**You should see** `Updated 1 path from the index`, then the build from 5.2 again, ending in `PASS=11`.

**What it means** `git checkout <file>` puts the file back to the last committed version. Everything is green again.

> **Bigger data.** The real Swiss timetable has 35 million rows in stop_times and 2.2 million trips. The same "how many rows, how many trips" question takes 18.6 seconds in pandas, 1.0 second with DuckDB on the text file, and 0.1 seconds with DuckDB on a Parquet file. The text file is 3 GB, the Parquet file 69 MB. Same SQL, no change. You do not need to run this, it is here so you know that what you did on 160 trips is what people do on 2 million.

---

## Part 6. The data changes

Timetables get re-published. Your lecturer has put a new version on the server, on a branch called `feat/day-three`. Bring it in and see what happens to your answer.

### Step 6.1 Ask the server what is new

**Type this**

```
git fetch origin
```

**You should see** a few lines, among them `* [new branch] feat/day-three -> origin/feat/day-three`. If you see nothing at all, the branch is not published yet, ask your lecturer.

**What it means** git asked the server for everything it has and downloaded it, without changing any of your files yet.

### Step 6.2 Bring the new files in

**Type this**

```
git merge origin/feat/day-three
```

**You should see**

```
Updating xxxxxxx..yyyyyyy
Fast-forward
 raw/calendar.txt   | 6 +++---
 raw/stop_times.txt | 5 +++++
 raw/trips.txt      | 1 +
 3 files changed, 9 insertions(+), 3 deletions(-)
```

**What it means** Three files in `raw/` were replaced by the new version. Nothing else changed. No code, no notebook.

### Step 6.3 Rerun the answer

**In the notebook**, run the first cell again (it reloads the four files), then the cell of Step 4.3.

**You should see** three days instead of two, and:

```
2026-09-14 IR 75     18
2026-09-15 IR 75     18
2026-09-16 IR 75     18
```

**What it means** IR 75 was 17. It is 18 now, on all days, including Monday and Tuesday, which were already published before. Nobody changed a query. The data changed under it.

### Step 6.4 See exactly what changed

**Run the two cells of Part 6 in the notebook.** They compare the new files with the old ones (the old ones are kept in `out/main/`) and show only the rows that are new.

**You should see**

```
route_id service_id  trip_id trip_headsign  direction_id
    IR75   TAEGLICH IR75.909        Luzern             0
```

and

```
service_id  monday  tuesday  wednesday  thursday  friday  saturday  sunday  start_date  end_date
  TAEGLICH       1        1          1         1       1         1       1    20260914  20260916
   WERKTAG       1        1          1         1       1         0       0    20260914  20260916
WOCHENENDE       0        0          0         0       0         1       1    20260914  20260916
```

**What it means** `EXCEPT` returns rows of the first table that are not in the second. One new trip, IR75.909, running daily. And the calendar now ends on the 16th instead of the 15th. That is the whole change, and it explains both things you saw: 17 became 18, and a third day appeared.

**Check** Why did IR 75 change on Monday, a day that was already published?

### Step 6.5 Rebuild only what depends on it

**Type this**

```
uv run --directory dbt dbt build --select stg_service_days+
```

**You should see** eight lines instead of eleven, ending in `PASS=8`.

**What it means** `--select stg_service_days+` means "stg_service_days and everything that depends on it". stg_trips was not rebuilt, it does not depend on the calendar. All checks pass. The pipeline absorbed the change.

---

## Part 7. Why the notebook is a marimo notebook

You have used the notebook for an hour. One last experiment shows why it is this notebook and not the more common Jupyter.

### Step 7.1 A notebook that remembers too much

**Type this** in the terminal (stop marimo first with Ctrl+C, or use a second terminal)

```
uv run jupyter lab notebooks/00_hidden_state.ipynb
```

Run the three code cells top to bottom with Shift+Enter. The last one prints `trips per day: 80`. Now click into the cell with `* 2` and run it again, then run the print cell again. It prints 160. Now delete the `* 2` cell entirely (click it, then press D twice) and run the print cell again.

**You should see** still 160.

**What it means** The cell doubled a number. Running it twice doubled it twice. Deleting the cell did not undo it, the value stays in memory. The notebook on screen no longer shows how the number was produced. Close JupyterLab with Ctrl+C in the terminal.

### Step 7.2 A notebook that refuses

**Type this**

```
uv run marimo edit notebooks/00_hidden_state_marimo.py
```

In the empty last cell, type `trips_per_day = trips_per_day * 2` and run it.

**You should see** an error saying the name is already defined in another cell.

**What it means** marimo tracks which cell defines which name. Two cells cannot define the same thing, so the situation from 7.1 cannot happen. And when you change a cell, every cell that uses its result runs again by itself. That is why in Step 6.3 you only had to rerun two cells and the rest followed.

When you are done, close the notebook and put the two files back:

```
git checkout notebooks/
```

---

## What you did

| Part | You saw | The tool that made it possible |
|---|---|---|
| 2, 3 | one trip is four rows, so counting the wrong table gives 64 instead of 16 | SQL on files, without a database server (DuckDB) |
| 4 | "per day" needs calendar.txt and nothing else | the same |
| 5 | a check turns the mistake from Part 3 into a red line before any result is built | dbt |
| 6 | the data changes, the number changes, and you can show exactly which rows are new | git, then SQL again |
| 7 | a notebook that cannot silently keep old values | marimo |
| 1 | all of it ran on your laptop from one lockfile | uv |

**The habit:** before you count anything, say what one row of the table is.

---

## Appendix A. The four joins

Open the notebook `notebooks/03_joins.py`:

```
uv run marimo edit notebooks/03_joins.py
```

### Step A.1 Two small tables

**Run the first two cells**

**You should see**

```
line
IC 1
 S 3
S 15
```

```
line journey
IC 1      j1
IC 1      j2
 S 3      j3
S 99      j4
```

**What it means** `lines` has three lines. `journeys` has four journeys, each with the line it belongs to. Two things are deliberately wrong: S 15 has no journey, and journey j4 belongs to a line S 99 that does not exist in `lines`. Every join below treats these two cases differently. In the outputs, an empty cell means NULL: no match on that side.

### Step A.2 INNER JOIN

**Run this cell**

```sql
SELECT l.line, j.journey
FROM lines l
INNER JOIN journeys j ON j.line = l.line
```

**You should see**

```
line journey
IC 1      j1
IC 1      j2
 S 3      j3
```

**What it means** Only rows with a match on both sides. S 15 is gone (no journey), j4 is gone (no line). Plain `JOIN` means `INNER JOIN`. This is what Step 2.6, 3.2 and 4.3 use.

### Step A.3 LEFT JOIN

**Run this cell**

```sql
SELECT l.line, j.journey
FROM lines l
LEFT JOIN journeys j ON j.line = l.line
```

**You should see**

```
line journey
IC 1      j1
IC 1      j2
S 15
 S 3      j3
```

**What it means** Every row of the left table (`lines`) is kept. Where there is a match, the journey is attached. Where there is none, the journey column is empty. S 15 is back, with nothing next to it. j4 is still gone, it is on the right side and has no match.

**Check** Which side is "left"? (The table named after `FROM`.)

### Step A.4 RIGHT JOIN

**Run this cell**

```sql
SELECT l.line, j.line AS journey_line, j.journey
FROM lines l
RIGHT JOIN journeys j ON j.line = l.line
```

**You should see**

```
line journey_line journey
IC 1         IC 1      j1
IC 1         IC 1      j2
 S 3          S 3      j3
             S 99      j4
```

**What it means** The mirror image. Every row of the right table (`journeys`) is kept. j4 is back, with an empty `line` because S 99 is not in `lines`. S 15 is gone. In practice people write the table they want to keep on the left and use LEFT JOIN, RIGHT JOIN is rare.

### Step A.5 FULL OUTER JOIN

**Run this cell**

```sql
SELECT l.line, j.line AS journey_line, j.journey
FROM lines l
FULL OUTER JOIN journeys j ON j.line = l.line
```

**You should see**

```
line journey_line journey
IC 1         IC 1      j1
IC 1         IC 1      j2
S 15
 S 3          S 3      j3
             S 99      j4
```

**What it means** Everything from both sides. S 15 with no journey, j4 with no line, and the three matches. Useful when you want to find what is missing on either side.

Summary of A.2 to A.5:

| Join | Keeps | Rows here |
|---|---|---|
| INNER | only matches | 3 |
| LEFT | all of the left table, plus matches | 4 |
| RIGHT | all of the right table, plus matches | 4 |
| FULL OUTER | all of both | 5 |

### Step A.6 The trap: counting after a LEFT JOIN

**Run this cell**

```sql
SELECT l.line, COUNT(*) AS count_star, COUNT(j.journey) AS count_journeys
FROM lines l
LEFT JOIN journeys j ON j.line = l.line
GROUP BY l.line
```

**You should see**

```
line  count_star  count_journeys
IC 1           2               2
S 15           1               0
 S 3           1               1
```

**What it means** S 15 has no journeys, but `COUNT(*)` says 1. The LEFT JOIN produced one row for S 15 with an empty journey, and `COUNT(*)` counts rows, empty or not. `COUNT(j.journey)` counts only rows where that column is filled, and says 0. After a LEFT JOIN, count the column from the right table, not `*`.

### Step A.7 On the real data

**Run the last two cells.** The hidden one rebuilds `service_days` from Step 4.2. The visible one is:

```sql
SELECT r.route_short_name AS route, t.service_id,
       COUNT(*) AS rows_after_join,
       COUNT(sd.service_day) AS rows_with_a_day
FROM trips t
JOIN routes r ON r.route_id = t.route_id
LEFT JOIN service_days sd ON sd.service_id = t.service_id
GROUP BY route, t.service_id
```

**You should see**

```
route service_id  rows_after_join  rows_with_a_day
 IC 1   TAEGLICH               32               32
IR 75   TAEGLICH               34               34
 S 15 WOCHENENDE               11                0
  S 3    WERKTAG               76               76
  S 5    WERKTAG               76               76
  S 7   TAEGLICH               80               80
```

**What it means** Two things to read here. First, IC 1 has 16 trips but 32 rows after the join, because service_days has two days and every trip matches both. That is what "per day" does, and Step 4.3 then groups by day to get 16 and 16. Second, S 15 survives the LEFT JOIN with its 11 trips, but not one of them has a day. With the plain `JOIN` of Step 4.3 these 11 rows vanish, which is right: the question is per day, and S 15 has no day in this data.

**Check** Step 4.3 uses `JOIN service_days`. What would the result look like with `LEFT JOIN service_days` and `COUNT(*)`?
