# Implementation Plan: Per-Feature `components/` Directories

**Branch**: `010-feature-components` | **Date**: 2026-05-24
**Input**: /speckit.analyse output — "put a component directory in each feature directory"

---

## Summary

Pull every self-contained UI unit out of the monolithic `views/*.py` builders
and into a `components/` package within the same feature directory.
The `views/` file becomes a thin page-builder that imports from `components/`.

Rule: `views/` = page entry-points called by `app.py`.  
`components/` = reusable sub-widgets used *by* the view builder.

**Tests must stay at 45 passed throughout.**

---

## Technical Context

| Item | Value |
|------|-------|
| Language | Python 3.13 |
| Flet | `flet==0.84.0` |
| Runner | `uv run flet run src/main.py` |
| Tests | `uv run pytest tests/ -q` → 45 passed |
| Callers of views | `src/app.py` only |
| pyproject pythonpath | `[".", "src"]` — bare module names work |

---

## Target Layout

```
src/features/
├── map/
│   ├── components/
│   │   ├── __init__.py        # re-exports GroupFilter, InfoPanel, MapView
│   │   ├── group_filter.py    # MOVED from views/
│   │   ├── info_panel.py      # MOVED from views/
│   │   └── map_view.py        # MOVED from views/
│   └── views/
│       └── __init__.py        # empty (views/ kept for consistency)
│
├── schedule/
│   ├── components/
│   │   ├── __init__.py        # re-exports match_row, header_row
│   │   └── match_row.py       # MOVED: _match_row, _header_row + private helpers
│   └── views/
│       └── schedule_view.py   # imports from components/
│
├── teams/
│   ├── components/
│   │   ├── __init__.py        # re-exports team_stats_row
│   │   └── team_stats_row.py  # EXTRACTED from nested fn in teams_view.py
│   └── views/
│       └── teams_view.py      # imports from components/
│
├── matches/
│   ├── components/
│   │   ├── __init__.py        # re-exports match_detail
│   │   └── match_detail.py    # EXTRACTED from _on_match_select body
│   └── views/
│       └── matches_view.py    # imports from components/
│
├── records/
│   ├── components/
│   │   ├── __init__.py        # re-exports mode_toggle, ModeToggle
│   │   └── mode_toggle.py     # EXTRACTED btn_goals/btn_app + _set_mode
│   └── views/
│       └── records_view.py    # imports from components/
│
├── venues/
│   ├── components/
│   │   ├── __init__.py        # re-exports venue_marker
│   │   └── venue_marker.py    # EXTRACTED inline Marker construction
│   └── views/
│       └── osm_map_view.py    # imports from components/
│
└── tournament/
    └── views/
        └── tournament_view.py # no distinct sub-widget — no components/ dir
```

---

## Component API Designs

### `features/map/components/` — move only, no API change

`GroupFilter`, `InfoPanel`, `MapView` are `@ft.component` functions.
Files are moved verbatim; only the import path changes.

---

### `features/schedule/components/match_row.py`

Move module-level private functions out of `schedule_view.py`.  
Public surface (called by `schedule_view`):

```python
def match_row(match: dict, row_idx: int) -> ft.Container: ...
def header_row() -> ft.Container: ...
```

Private helpers stay in the same file:
`_group_colour`, `_fmt_utc`, `_score_text`, `_STATUS_LABEL`, `_GROUP_COLOURS`.

---

### `features/teams/components/team_stats_row.py`

Extract the nested `_summary_stats(team, df)` closure into a module-level function.

```python
def team_stats_row(team: str, df) -> ft.Row:
    """Row of stat_badge widgets for a team's all-time World Cup record."""
    ...
```

The function already has no side-effects; extraction is mechanical.
`_team_stats(team)` stays as a closure in the view (it queries `store`).

---

### `features/matches/components/match_detail.py`

Extract the body of `_on_match_select` that builds the detail panel controls
into a pure builder function:

```python
def match_detail(match: dict, events) -> ft.Column:
    """Return a ft.Column describing one match: teams, score, goalscorers."""
    ...
```

`_on_match_select` becomes:
```python
def _on_match_select(idx: int) -> None:
    ...
    detail_container.controls = [match_detail(m, events)]
    detail_container.update()
```

Imports needed: `section_title`, `ACCENT`, `TEXT_PRIMARY`, `TEXT_SECONDARY`
from `core.ui_helpers`.

---

### `features/records/components/mode_toggle.py`

Extract the two toggle buttons and their `_set_mode` handler:

```python
from dataclasses import dataclass

@dataclass
class ModeToggle:
    btn_goals: ft.Button
    btn_app:   ft.Button
    row:       ft.Row        # ft.Row([btn_goals, btn_app], spacing=12)

def mode_toggle(on_mode_change: Callable[[str], None]) -> ModeToggle:
    """Create a goals / appearances toggle button pair.

    Args:
        on_mode_change: called with "goals" or "appearances" when a button is clicked.
    """
    ...
```

`records_view.py` calls `mt = mode_toggle(_set_mode)` and uses
`mt.btn_goals`, `mt.btn_app`, `mt.row`.  The `_set_mode` closure
(which updates `table_container`, etc.) stays in the view; the toggle
calls it via the callback.

---

### `features/venues/components/venue_marker.py`

Extract the inline `ftm.Marker(…)` construction from the list comprehension:

```python
def venue_marker(venue: dict, on_tap: Callable[[dict], None]) -> ftm.Marker:
    """Build a styled stadium icon Marker for a host venue."""
    ...
```

`osm_map_view.py` list comprehension becomes:
```python
markers = [venue_marker(v, _on_marker_tap) for v in _VENUES]
```

---

## Phases

### Phase 1 — `features/map/` (move, no logic change)

**Step 1.1** — Create `src/features/map/components/` with `__init__.py`.  
Copy (then delete) `group_filter.py`, `info_panel.py`, `map_view.py` from `views/` to `components/`.  
`__init__.py` re-exports `GroupFilter`, `InfoPanel`, `MapView`.

**Step 1.2** — Update `src/app.py` imports:
```python
# before
from features.map.views.group_filter import GroupFilter
from features.map.views.info_panel   import InfoPanel
from features.map.views.map_view     import MapView
# after
from features.map.components import GroupFilter, InfoPanel, MapView
```

**Step 1.3** — Delete vacated `views/group_filter.py`, `views/info_panel.py`,
`views/map_view.py`; leave `views/__init__.py` (empty).

Run: `uv run pytest tests/ -q` → 45 passed.

---

### Phase 2 — `features/schedule/` (move module-level functions)

**Step 2.1** — Create `src/features/schedule/components/match_row.py`.  
Move `_STATUS_LABEL`, `_GROUP_COLOURS`, `_group_colour`, `_fmt_utc`,
`_score_text`, `_match_row`, `_header_row` from `schedule_view.py` into it.  
Rename `_match_row` → `match_row`, `_header_row` → `header_row` (public).

**Step 2.2** — Create `__init__.py` re-exporting `match_row`, `header_row`.

**Step 2.3** — Update `schedule_view.py`:
```python
from features.schedule.components import match_row, header_row
```
Replace the two call sites `_header_row()` → `header_row()` and
`_match_row(m, i)` → `match_row(m, i)`.

Run: `uv run pytest tests/ -q` → 45 passed.

---

### Phase 3 — `features/teams/`, `features/venues/` (extract independent helpers) [parallel]

Both steps touch different files — execute together.

**Step 3.1** — Create `src/features/teams/components/team_stats_row.py`.  
Lift the nested `_summary_stats(team, df)` closure to module level as
`team_stats_row(team, df)`.  Add necessary imports (`stat_badge`,
`TEXT_SECONDARY`, `TEXT_PRIMARY` from `core.ui_helpers`).  
Update `teams_view.py` to `from features.teams.components import team_stats_row`
and replace `_summary_stats(team1, df1)` → `team_stats_row(team1, df1)`.

**Step 3.2** — Create `src/features/venues/components/venue_marker.py`.  
Extract the `ftm.Marker(…ft.GestureDetector…)` construction into
`venue_marker(venue, on_tap)`.  Update `osm_map_view.py` list comprehension.

Run: `uv run pytest tests/ -q` → 45 passed.

---

### Phase 4 — `features/matches/`, `features/records/` (extract with callback interface) [parallel]

**Step 4.1** — Create `src/features/matches/components/match_detail.py`.  
Extract the body of `_on_match_select` (lines 198–232) that builds the
detail controls into `match_detail(match, events) -> ft.Column`.  
Update `_on_match_select` to call it:
```python
detail_container.controls = [match_detail(m, events)]
detail_container.update()
```

**Step 4.2** — Create `src/features/records/components/mode_toggle.py`.  
Extract `btn_goals`, `btn_app` construction + `_set_mode` visual-update logic
into `mode_toggle(on_mode_change) -> ModeToggle`.  
View's own `_set_mode` calls `on_mode_change(mode)` and uses
`mt.btn_goals`/`mt.btn_app` refs for `bgcolor` updates (or delegates
entirely to the component — see design above).

Run: `uv run pytest tests/ -q` → 45 passed.

---

### Phase 5 — Tests & verification

**Step 5.1** — Add `tests/unit/test_feature_components.py` with import smoke
tests:
```python
from features.map.components import GroupFilter, InfoPanel, MapView
from features.schedule.components import match_row, header_row
from features.teams.components import team_stats_row
from features.matches.components import match_detail
from features.records.components import mode_toggle
from features.venues.components import venue_marker
```
Each import must succeed (no runtime execution needed — 6 tests).

Run: `uv run pytest tests/ -q` → **51 passed**.

**Step 5.2** — Manual smoke: `flet run --web src/main.py` — exercise all 7 tabs.

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| `app.py` three map imports break | Low | Update in Step 1.2 before deleting old files |
| `schedule_view.py` local imports of moved private helpers | Low | All helpers travel together into `match_row.py`; rename `_match_row`→`match_row` at move time |
| `teams_view.py` `_summary_stats` uses `stat_badge` from `core.ui_helpers` | Low | Add import to `team_stats_row.py` at extraction |
| `records` mode_toggle: `_set_mode` references `btn_goals`/`btn_app`/`table_container` (view locals) | Medium | Callback pattern (`on_mode_change`) decouples visual toggle from table logic; view retains table refs |
| `match_detail` uses `section_title`, `ACCENT`, `TEXT_*` from `core.ui_helpers` — must add imports | Low | Add imports at extraction time |

---

## Definition of Done

- [ ] 6 `features/*/components/` packages created (tournament excluded)
- [ ] `features/map/views/` vacated of the 3 component files; `app.py` updated
- [ ] Each `components/__init__.py` re-exports its public symbols
- [ ] Each parent `views/*.py` updated to import from `components/`
- [ ] `tests/unit/test_feature_components.py` with 6 import smoke tests
- [ ] `uv run pytest tests/ -q` → **51 passed**
- [ ] All 7 tabs render correctly in `flet run --web src/main.py`
