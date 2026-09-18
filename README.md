# DAENG HS26 — Session 1

**How many trips does each route run per day?**

One question, one feed, and the tools that let an answer survive four things:
the full data, a second person, a change in the data, and not having written
the query yourself.

## Start here

Work through `TUTORIAL.md`. It starts with the setup below and ends with the changed feed, in seven parts.

## Setup

Install uv once (it installs Python for you), then:

```
git clone <course-repo-url>
cd daeng-hs26
uv sync
```

Or open the repo in a GitHub Codespace. Everything runs in the browser.

## Run

```
uv run marimo edit notebooks/01_first_look.py     # the notebook
uv run --directory dbt dbt build                  # models and tests
uv run --directory dbt dbt docs generate          # then: dbt docs serve
git fetch origin && git merge origin/feat/day-three   # the re-published feed
```

## Layout

```
raw/         the GTFS slice. Small, synthetic, in the shape of the real feed. Never edited by hand.
notebooks/   01_first_look.py is the tutorial notebook, 03_joins.py its appendix on joins. 00_* is the hidden-state pair. 02_* and 09_* are lecturer only.
dbt/         the same query as a model DAG with tests. dbt/demo/ holds the deliberately wrong grain.
tools/       build_slice.py regenerates raw/. prepare_full_feed.py fetches the real feed (lecturer).
CLAUDE.md    the three rules of this feed, as context for any coding assistant.
```

## The three rules

Read `CLAUDE.md`. Every one of them produces a wrong number if ignored.
