# Quickstart: Schedule Group Stage Display

**Feature**: 012-schedule-group-display

---

## Prerequisites

```bash
cd /path/to/football-impl-flet-2026
uv sync
cp .env.example .env          # add your FOOTBALL_DATA_API_KEY
```

## Run the app

```bash
uv run flet run --web src/main.py
```

Open the **Schedule** tab. Group chips (All, A–L) appear above the match list. Click any chip to filter.

## Run tests

```bash
uv run pytest tests/unit/test_schedule_group_display.py -v
uv run pytest tests/                                       # full suite
```

## Manual acceptance test (no API key)

1. Remove `FOOTBALL_DATA_API_KEY` from `.env`.
2. Open the Schedule tab.
3. **Expected**: Group chips render. Match area shows "Set FOOTBALL_DATA_API_KEY to load the live schedule." No error thrown.

## Manual acceptance test (with API key)

1. Set a valid `FOOTBALL_DATA_API_KEY`.
2. Open the Schedule tab.
3. After load notice, click **Group C**.
4. **Expected**: Only Group C matches visible, sorted by matchday then time.
5. Click **All**.
6. **Expected**: All 48 matches visible.
7. Find a finished match. **Expected**: Score shows "X – Y" in bold amber; status shows "FT".
8. Find an upcoming match. **Expected**: Score shows "vs"; date, time (labelled UTC), and full stadium name visible.
