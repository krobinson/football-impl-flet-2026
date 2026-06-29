# Quickstart — 013-remove-history-tabs

## Running the App

```bash
uv run flet run --web src/main.py
```

Open `http://localhost:8550` (or the port shown in the terminal).

## Verifying the Change

1. The bottom navigation bar shows **exactly 3 destinations**:
   - 2026 Map
   - Venues
   - Schedule
2. No History, Teams, Matches, or Records tab is visible.
3. Each tab loads without error.
4. No console errors referencing `store`, `get_data_store`, `tournament_view`, `teams_view`, `matches_view`, or `records_view`.

## Running Tests

```bash
uv run pytest tests/ -q
```

Expected: **all tests pass** (no new tests added, no tests removed).

The existing 143 tests cover the three remaining features and core utilities — none of them depended on the removed `store` parameter.
