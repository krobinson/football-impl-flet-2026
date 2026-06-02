# Quickstart: Team Tournament Progression

## Pre-requisites

- Python 3.10+ with the project virtual environment activated:
  ```bash
  source .venv/bin/activate   # or: uv run ...
  ```
- No additional packages required — all dependencies already in `pyproject.toml`.

---

## Run the App

```bash
# Desktop
uv run flet run src/app.py

# Browser
uv run flet run --web src/app.py
```

Navigate to the **History** tab. Select an edition year and optionally select a
team from the new "Filter by Team" dropdown. The progression panel shows each
round the team played in, with match results.

---

## Run the Tests

```bash
uv run pytest tests/unit/test_tournament_progression.py -v
uv run pytest tests/unit/ -v          # full unit suite
uv run pytest                          # all tests
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/features/tournament/services.py` | New — pure `get_team_progression()` function |
| `src/features/tournament/views/tournament_view.py` | Modified — adds team filter dropdown and progression panel |
| `tests/unit/test_tournament_progression.py` | New — unit tests for `get_team_progression` |

---

## Manual Smoke Test Checklist

1. Open the **History** tab.
2. Select edition **2022** → progression panel appears below the summary badges.
3. Verify at least one match is visible in the "Group Stage – Matchday 1" section.
4. Select team **Argentina** → only Argentina's matches show across all rounds.
5. Confirm the Final entry shows Argentina vs France with AET/penalties noted.
6. Clear the team filter → all teams visible again.
7. Switch to edition **2018** → panel updates; Germany shows only 3 group-stage matches.
8. Select edition **1930** → only group/final-round matches shown (no Round of 16).
