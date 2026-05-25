# Tasks: Per-Feature `components/` Directories

**Input**: `specs/010-feature-components/plan.md`
**Test baseline**: `uv run pytest tests/ -q` → 45 passed

## Format

- `[P]` — can run in parallel with other `[P]` tasks in the same phase (different files)
- Run `uv run pytest tests/ -q` after every phase and confirm the expected count
- Test count grows by 6 at Phase 5 (51 total)

---

## Phase 1 — Move `features/map/` components

**Goal**: Relocate the three `@ft.component` files from `views/` to `components/`
and update `app.py`. No logic changes.

- [ ] **T001** Create `src/features/map/components/__init__.py`

  Content:
  ```python
  """Public surface of features.map.components."""
  from features.map.components.group_filter import GroupFilter
  from features.map.components.info_panel import InfoPanel
  from features.map.components.map_view import MapView

  __all__ = ["GroupFilter", "InfoPanel", "MapView"]
  ```

- [ ] **T002** Copy `src/features/map/views/group_filter.py` →
  `src/features/map/components/group_filter.py` (content identical).

- [ ] **T003** Copy `src/features/map/views/info_panel.py` →
  `src/features/map/components/info_panel.py` (content identical).

- [ ] **T004** Copy `src/features/map/views/map_view.py` →
  `src/features/map/components/map_view.py` (content identical).

- [ ] **T005** Update `src/app.py` — replace the three map imports:

  Old:
  ```python
  from features.map.views.group_filter import GroupFilter
  from features.map.views.info_panel import InfoPanel
  from features.map.views.map_view import MapView
  from features.map.models import MapRenderState
  ```
  New:
  ```python
  from features.map.components import GroupFilter, InfoPanel, MapView
  from features.map.models import MapRenderState
  ```

- [ ] **T006** Delete the three now-vacated view files:
  - `src/features/map/views/group_filter.py`
  - `src/features/map/views/info_panel.py`
  - `src/features/map/views/map_view.py`

  Leave `src/features/map/views/__init__.py` in place (empty).

  Run: `uv run pytest tests/ -q` → **45 passed**.

---

## Phase 2 — Move `features/schedule/` row builders

**Goal**: Extract the five module-level helper functions and two widget builders
from `schedule_view.py` into `components/match_row.py`.

- [ ] **T007** Create `src/features/schedule/components/match_row.py`

  Move from `schedule_view.py` (lines 21–178):
  - Constants: `_STATUS_LABEL`, `_GROUP_COLOURS`
  - Private helpers: `_group_colour`, `_fmt_utc`, `_score_text`
  - Widget builders — rename to public: `_match_row` → `match_row`,
    `_header_row` → `header_row`

  Required imports at top of new file:
  ```python
  from __future__ import annotations
  import flet as ft
  from core.ui_helpers import ACCENT, TEXT_PRIMARY, TEXT_SECONDARY
  ```

- [ ] **T008** Create `src/features/schedule/components/__init__.py`

  ```python
  from features.schedule.components.match_row import match_row, header_row
  __all__ = ["match_row", "header_row"]
  ```

- [ ] **T009** Update `src/features/schedule/views/schedule_view.py`

  - Remove the moved constants and functions (lines 21–178).
  - Add import: `from features.schedule.components import match_row, header_row`
  - Replace two call sites:
    - `[_header_row()]` → `[header_row()]`
    - `_match_row(m, i)` → `match_row(m, i)`

  Run: `uv run pytest tests/ -q` → **45 passed**.

---

## Phase 3 — Extract `features/teams/` and `features/venues/` helpers [parallel]

- [ ] **T010** [P] Create `src/features/teams/components/team_stats_row.py`

  Extract the nested `_summary_stats` closure from `teams_view.py` (lines 46–72)
  into a module-level function:

  ```python
  """Team summary statistics row widget."""
  from __future__ import annotations
  import flet as ft
  from core.ui_helpers import TEXT_SECONDARY, stat_badge

  def team_stats_row(team: str, df) -> ft.Row:
      """Row of stat_badge widgets for a team's all-time World Cup record.

      Args:
          team: Team name (used in the empty-state message).
          df:   DataFrame slice for this team from store.team_standings.
      """
      if df.empty:
          return ft.Row([ft.Text(f"No World Cup data for {team}.", color=TEXT_SECONDARY)])
      total_p  = int(df["played"].sum())
      total_w  = int(df["wins"].sum())
      total_d  = int(df["draws"].sum())
      total_l  = int(df["losses"].sum())
      total_gf = int(df["goals_for"].sum())
      total_ga = int(df["goals_against"].sum())
      editions = len(df)
      w_pct    = f"{total_w / total_p * 100:.0f}%" if total_p else "0%"
      return ft.Row(
          [
              stat_badge("World Cups",    str(editions)),
              stat_badge("Matches",       str(total_p)),
              stat_badge(f"Wins ({w_pct})", str(total_w), "#2ECC71"),
              stat_badge("Draws",         str(total_d), "#F39C12"),
              stat_badge("Losses",        str(total_l), "#E74C3C"),
              stat_badge("Goals For",     str(total_gf)),
              stat_badge("Goals Against", str(total_ga)),
              stat_badge("GD", f"{total_gf - total_ga:+d}",
                         "#2ECC71" if total_gf >= total_ga else "#E74C3C"),
          ],
          wrap=True, spacing=8,
      )
  ```

  Create `src/features/teams/components/__init__.py`:
  ```python
  from features.teams.components.team_stats_row import team_stats_row
  __all__ = ["team_stats_row"]
  ```

  Update `teams_view.py`:
  - Add: `from features.teams.components import team_stats_row`
  - Remove the `_summary_stats` closure.
  - Replace `_summary_stats(team1, df1)` → `team_stats_row(team1, df1)`.
  - Remove `stat_badge` from `core.ui_helpers` import if no longer used directly.

- [ ] **T011** [P] Create `src/features/venues/components/venue_marker.py`

  Extract the `ftm.Marker(…)` block from `osm_map_view.py` (lines 37–48):

  ```python
  """Venue marker widget for the OSM venues map."""
  from __future__ import annotations
  from collections.abc import Callable
  import flet as ft
  import flet_map as ftm

  _FLAG  = {"USA": "🇺🇸", "CAN": "🇨🇦", "MEX": "🇲🇽"}
  _COLOR = {
      "USA": ft.Colors.BLUE_700,
      "CAN": ft.Colors.RED_700,
      "MEX": ft.Colors.GREEN_700,
  }


  def venue_marker(
      venue: dict,
      on_tap: Callable[[dict], None],
  ) -> ftm.Marker:
      """Build a styled stadium icon Marker for a host venue.

      Args:
          venue:  Venue dict with keys: lat, lon, name, city, country.
          on_tap: Called with the venue dict when the marker is tapped.
      """
      return ftm.Marker(
          coordinates=ftm.MapLatitudeLongitude(venue["lat"], venue["lon"]),
          content=ft.GestureDetector(
              content=ft.Icon(
                  ft.Icons.STADIUM,
                  color=_COLOR.get(venue["country"], ft.Colors.YELLOW_700),
                  size=28,
                  tooltip=f"{venue['name']}\n{venue['city']}",
              ),
              on_tap=lambda e, v=venue: on_tap(v),
          ),
      )
  ```

  Create `src/features/venues/components/__init__.py`:
  ```python
  from features.venues.components.venue_marker import venue_marker
  __all__ = ["venue_marker"]
  ```

  Update `osm_map_view.py`:
  - Add: `from features.venues.components import venue_marker`
  - Remove the `_FLAG` and `_COLOR` module-level dicts (now in component).
  - Replace the list comprehension:
    ```python
    markers = [venue_marker(v, _on_marker_tap) for v in _VENUES]
    ```

  Run: `uv run pytest tests/ -q` → **45 passed**.

---

## Phase 4 — Extract `features/matches/` and `features/records/` [parallel]

- [ ] **T012** [P] Create `src/features/matches/components/match_detail.py`

  Extract the panel-building body of `_on_match_select` (lines 198–232)
  into a pure function:

  ```python
  """Match detail panel widget."""
  from __future__ import annotations
  import flet as ft
  from core.ui_helpers import ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, section_title


  def match_detail(match: dict, events) -> ft.Column:
      """Build a detail panel for one match.

      Args:
          match:  Match record dict (keys: home_team, away_team, home_score,
                  away_score, aet, date, stage, venue).
          events: DataFrame of goal events for this match (may be empty).

      Returns:
          ft.Column with title, score line, venue line, and goalscorer list.
      """
      home_score = int(match["home_score"])
      away_score = int(match["away_score"])
      score_str  = f"{home_score}–{away_score}"
      if match.get("aet"):
          score_str += " (AET)"

      controls: list[ft.Control] = [
          section_title("📋 Match Detail"),
          ft.Text(
              f"{match['home_team']}  {score_str}  {match['away_team']}",
              size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
          ),
          ft.Text(
              f"{match['date']}  •  {match['stage']}  •  {match['venue']}",
              size=12, color=TEXT_SECONDARY,
          ),
      ]

      if events.empty:
          controls.append(
              ft.Text("No goalscorer data available.", color=TEXT_SECONDARY, size=12)
          )
      else:
          goal_rows: list[ft.Control] = []
          for _, ev in events.iterrows():
              minute = (
                  f"{int(float(ev['minute']))}'"
                  if ev.get("minute") and str(ev["minute"]) not in ("nan", "", "None")
                  else ""
              )
              etype = {
                  "goal": "⚽", "own_goal": "🔴 OG", "penalty_goal": "⚽ (P)"
              }.get(ev["event_type"], "⚽")
              goal_rows.append(
                  ft.Text(f"{etype}  {ev['player']} ({ev['team']}) {minute}",
                          size=12, color=TEXT_PRIMARY)
              )
          controls += [
              ft.Text("Goalscorers:", size=13, color=ACCENT,
                      weight=ft.FontWeight.BOLD),
              *goal_rows,
          ]

      return ft.Column(controls, spacing=4)
  ```

  Create `src/features/matches/components/__init__.py`:
  ```python
  from features.matches.components.match_detail import match_detail
  __all__ = ["match_detail"]
  ```

  Update `matches_view.py`:
  - Add: `from features.matches.components import match_detail`
  - Rewrite `_on_match_select` after the `events =` line:
    ```python
    detail_container.controls = [match_detail(m, events)]
    try:
        detail_container.update()
    except Exception:
        pass
    ```
  - Remove the now-inlined control-building code from `_on_match_select`.

- [ ] **T013** [P] Create `src/features/records/components/mode_toggle.py`

  Extract the two toggle buttons and their visual-update logic:

  ```python
  """Mode toggle widget (Goals / Appearances) for the Records tab."""
  from __future__ import annotations
  from collections.abc import Callable
  from dataclasses import dataclass
  import flet as ft
  from core.ui_helpers import ACCENT, BG_CARD, TEXT_PRIMARY


  @dataclass
  class ModeToggle:
      btn_goals: ft.Button
      btn_app:   ft.Button
      row:       ft.Row


  def mode_toggle(on_mode_change: Callable[[str], None]) -> ModeToggle:
      """Create a goals / appearances toggle button pair.

      Handles its own visual state (active/inactive colours).
      Calls *on_mode_change* with "goals" or "appearances" so the view can
      update the table and chart.

      Args:
          on_mode_change: Callback invoked with the new mode string.
      """
      btn_goals = ft.Button(
          "⚽ Top Scorers",
          bgcolor=ACCENT, color="#000000",
          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
      )
      btn_app = ft.Button(
          "🏅 Most Appearances",
          bgcolor=BG_CARD, color=TEXT_PRIMARY,
          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
      )

      def _activate(mode: str) -> None:
          if mode == "goals":
              btn_goals.bgcolor, btn_goals.color = ACCENT, "#000000"
              btn_app.bgcolor,   btn_app.color   = BG_CARD, TEXT_PRIMARY
          else:
              btn_app.bgcolor,   btn_app.color   = ACCENT, "#000000"
              btn_goals.bgcolor, btn_goals.color = BG_CARD, TEXT_PRIMARY
          try:
              btn_goals.update()
              btn_app.update()
          except Exception:
              pass
          on_mode_change(mode)

      btn_goals.on_click = lambda _: _activate("goals")
      btn_app.on_click   = lambda _: _activate("appearances")

      return ModeToggle(
          btn_goals=btn_goals,
          btn_app=btn_app,
          row=ft.Row([btn_goals, btn_app], spacing=12),
      )
  ```

  Create `src/features/records/components/__init__.py`:
  ```python
  from features.records.components.mode_toggle import ModeToggle, mode_toggle
  __all__ = ["ModeToggle", "mode_toggle"]
  ```

  Update `records_view.py`:
  - Add: `from features.records.components import mode_toggle`
  - Remove `btn_goals`, `btn_app` construction and the `_set_mode` visual-update
    block (keep only the `_render_table(mode)` call inside a new `_set_mode`).
  - Replace with:
    ```python
    def _set_mode(mode: str) -> None:
        _state["mode"] = mode
        _state["selected_idx"] = None
        _render_table(mode)

    mt = mode_toggle(_set_mode)
    ```
  - Replace `ft.Row([btn_goals, btn_app], spacing=12)` in the return value
    with `mt.row`.

  Run: `uv run pytest tests/ -q` → **45 passed**.

---

## Phase 5 — Smoke tests & verification

- [ ] **T014** Create `tests/unit/test_feature_components.py`

  ```python
  """Import smoke tests for per-feature component packages."""
  from __future__ import annotations


  def test_map_components_importable() -> None:
      from features.map.components import GroupFilter, InfoPanel, MapView
      assert callable(GroupFilter)
      assert callable(InfoPanel)
      assert callable(MapView)


  def test_schedule_components_importable() -> None:
      from features.schedule.components import match_row, header_row
      assert callable(match_row)
      assert callable(header_row)


  def test_teams_components_importable() -> None:
      from features.teams.components import team_stats_row
      assert callable(team_stats_row)


  def test_matches_components_importable() -> None:
      from features.matches.components import match_detail
      assert callable(match_detail)


  def test_records_components_importable() -> None:
      from features.records.components import mode_toggle, ModeToggle
      assert callable(mode_toggle)
      assert ModeToggle is not None


  def test_venues_components_importable() -> None:
      from features.venues.components import venue_marker
      assert callable(venue_marker)
  ```

  Run: `uv run pytest tests/ -q` → **51 passed**.

- [ ] **T015** Manual smoke-check — `flet run --web src/main.py`:
  - Map tab: group chips toggle, country click updates info panel
  - Schedule tab: group filter, row colours, loading spinner
  - Teams tab: dropdown, stat badges, head-to-head chart
  - Matches tab: year/stage/group filters, row click → goalscorer detail
  - Records tab: Goals / Appearances toggle, row click → detail
  - Venues tab: map loads, marker tap shows venue name
  - History & Tournament tabs: unaffected, render normally
