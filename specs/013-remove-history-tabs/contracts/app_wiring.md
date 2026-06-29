# App Wiring Contract

## Feature: 013-remove-history-tabs

This document captures the public wiring contract for `src/app.py` before and after the change.
These are the only surfaces that change — no new modules, no new tests.

---

## `_build_app()` Signature

### Before
```python
def _build_app(page: ft.Page, svc, store, fd_client) -> None:
```

### After
```python
def _build_app(page: ft.Page, svc, fd_client) -> None:
```

---

## `page.render()` Call in `main()`

### Before
```python
page.render(_build_app, page, svc, store, fd_client)
```

### After
```python
page.render(_build_app, page, svc, fd_client)
```

---

## `store` Variable in `main()`

### Before
```python
store = get_data_store()
```

### After
*(removed entirely)*

---

## `tab_bodies` List

### Before (7 entries)
| Index | Variable            | Tab Label  |
|-------|---------------------|------------|
| 0     | `map_tab_content`   | 2026 Map   |
| 1     | `osm_content`       | Venues     |
| 2     | `schedule_content`  | Schedule   |
| 3     | `tournament_content`| History    |
| 4     | `teams_content`     | Teams      |
| 5     | `matches_content`   | Matches    |
| 6     | `records_content`   | Records    |

### After (3 entries)
| Index | Variable            | Tab Label  |
|-------|---------------------|------------|
| 0     | `map_tab_content`   | 2026 Map   |
| 1     | `osm_content`       | Venues     |
| 2     | `schedule_content`  | Schedule   |

---

## `nav.destinations` List

### Before (7 destinations)
```
Icon.MAP         — 2026 Map
Icon.PLACE       — Venues
Icon.CALENDAR_TODAY — Schedule
Icon.HISTORY     — History
Icon.GROUPS      — Teams
Icon.SPORTS_SOCCER — Matches
Icon.LEADERBOARD — Records
```

### After (3 destinations)
```
Icon.MAP         — 2026 Map
Icon.PLACE       — Venues
Icon.CALENDAR_TODAY — Schedule
```

---

## Removed Imports

```python
from src.core.store import get_data_store          # removed
from src.features.tournament.views.tournament_view import build_tournament_view  # removed
from src.features.teams.views.teams_view import build_teams_view  # removed
from src.features.matches.views.matches_view import build_matches_view  # removed
from src.features.records.views.records_view import build_records_view  # removed
```

---

## Invariants

- `tab_bodies[selected_index]` must always resolve to a valid Flet control — satisfied with 3-entry list.
- `on_change` in `NavigationBar` maps `e.control.selected_index` to `tab_bodies` — same logic, no change required.
- Removed source files (`tournament_view.py`, `teams_view.py`, `matches_view.py`, `records_view.py`) remain on disk; only their imports from `app.py` are removed.
