# Tasks: Declarative Observable State — Map & Interaction Layer

**Input**: Design documents from `specs/008-declarative-observables/`
**Prerequisites**: plan.md ✅, spec.md ✅
**API check**: `ft.observable` ✅ `ft.component` ✅ `ft.use_state` ✅ (flet==0.84.0)

## Format

- `[P]` — can run in parallel with other `[P]` tasks in the same phase (different files, no shared edits)
- Tasks within a phase must all be complete before the next phase begins
- After every task that touches source files: run `uv run pytest tests/ -q` and confirm 44 passed

---

## Phase 1 — Observable model

**Goal**: Make `MapRenderState` reactive. No view files change yet; all existing tests must still pass.

- [ ] T001 **Verify API availability** — run `uv run python3 -c "import flet as ft; print(hasattr(ft, 'observable'))"` and confirm `True`. (Already confirmed above; record result.)

- [ ] T002 **Add `@ft.observable` to `MapRenderState`** — `src/features/map/models.py`
  - Add `import flet as ft` if not already present at top of file.
  - Stack `@ft.observable` above the existing `@dataclass` decorator on `MapRenderState`.
  - Do **not** change `ParticipatingCountry` or `FIFAGroup` — they are frozen value objects and must not be observable.
  - Run: `uv run pytest tests/unit/test_models.py -q` → 4 passed.

- [ ] T003 **Add observable reactivity test** — `tests/unit/test_models.py`
  - Add `import flet as ft` to test file imports.
  - Add test `test_map_render_state_is_observable` that asserts `MapRenderState` carries the observable marker (e.g. `hasattr(MapRenderState, "__ft_observable__")` or checks `ft.observable` was applied by verifying field mutation triggers the observable protocol).
  - Run: `uv run pytest tests/unit/test_models.py -q` → 5 passed.

---

## Phase 2 — `GroupFilter` component

**Goal**: Replace `build_group_filter` (imperative, mutates chip controls + calls `.update()`) with `@ft.component def GroupFilter(groups, state)` (declarative, derives chip colours from state on each render).

- [ ] T004 **Rewrite `group_filter.py`** — `src/features/map/views/group_filter.py`
  - Replace the module with a single `@ft.component` function `GroupFilter(groups: list[FIFAGroup], state: MapRenderState) -> ft.Control`.
  - Import `MapRenderState` from `features.map.models`.
  - Handler body: `state.active_group_filter = None if state.active_group_filter == group_name else group_name` — single assignment, no `.update()`.
  - Chip `bgcolor` and `label.color` are derived inline from `state.active_group_filter == g.name`; no `_refresh_chips()` function.
  - No `on_filter_change` parameter.
  - Keep module-level colour constants (`_CHIP_ACTIVE_BG`, etc.) unchanged.
  - Run: `uv run pytest tests/ -q` → 44 passed.

- [ ] T005 **Update `app.py` for `GroupFilter`** — `src/app.py`
  - Change import: `from features.map.views.group_filter import GroupFilter` (replacing `build_group_filter`).
  - Create `map_state = MapRenderState(canvas_width=800.0, canvas_height=400.0)` **before** all component construction (this line will be shared by T005, T007, T009 — add it once here).
  - Replace `build_group_filter(svc.get_groups(), map_state, on_filter_change)` with `GroupFilter(groups=svc.get_groups(), state=map_state)`.
  - Remove the `on_filter_change` closure entirely.
  - Run: `uv run pytest tests/ -q` → 44 passed.

---

## Phase 3 — `InfoPanel` component

**Goal**: Replace `build_info_panel()` (returns `(container, update_fn)` tuple; `update_fn` mutates 5 controls) with `@ft.component def InfoPanel(state)` (reads `state.selected_country` on each render; returns a single control).

- [ ] T006 **Rewrite `info_panel.py`** — `src/features/map/views/info_panel.py`
  - Replace the module with a single `@ft.component` function `InfoPanel(state: MapRenderState) -> ft.Control`.
  - Import `MapRenderState` from `features.map.models`; remove the `ParticipatingCountry` import from function signature (it is accessed via `state.selected_country`).
  - Derive all display values (`flag`, `name`, `group_txt`, `appear_txt`, `badge_visible`) from `state.selected_country` at the top of the function body.
  - Return a plain `ft.Container` (not a tuple); no `_set()` function; no `.update()` calls.
  - Module-level colour constants (`_PANEL_BG`, `_ACCENT`) unchanged.
  - Run: `uv run pytest tests/ -q` → 44 passed.

- [ ] T007 **Update `app.py` for `InfoPanel`** — `src/app.py`
  - Change import: `from features.map.views.info_panel import InfoPanel` (replacing `build_info_panel`).
  - Replace:
    ```python
    info_panel, update_info = build_info_panel()
    def on_country_selected(country): update_info(country)
    ```
    with:
    ```python
    info_control = InfoPanel(state=map_state)
    ```
  - Rename every reference to `info_panel` in `_build_map_body` to `info_control`.
  - Remove `on_country_selected` closure and any `update_info` references.
  - Run: `uv run pytest tests/ -q` → 44 passed.

---

## Phase 4 — `MapView` component

**Goal**: Replace `build_map_view(…) → (ft.Column, MapRenderState, refresh_map)` (returns a 3-tuple; `_refresh_map()` manually rebuilds polygons and calls `polygon_layer.update()`) with `@ft.component def MapView(page, svc, state)` (returns a single control; polygon list is rebuilt from state on each render; `on_tap` assigns to `state.selected_country` — no explicit refresh).

- [ ] T008 **Rewrite `map_view.py`** — `src/features/map/views/map_view.py`
  - Replace `build_map_view(page, svc, on_country_selected, on_group_filter_changed)` with `@ft.component def MapView(page: ft.Page, svc: WorldCupDataService, state: MapRenderState) -> ft.Control`.
  - Import `MapRenderState` from `features.map.models`.
  - `_on_map_tap`:
    ```python
    def _on_map_tap(e: ftm.MapTapEvent) -> None:
        iso = geo_hit_test(e.coordinates.longitude, e.coordinates.latitude, features)
        state.selected_country = svc.get_team(iso) if iso else None
    ```
    No `refresh_map()` call; no `on_country_selected(country)` call.
  - Construct `polygon_layer = ftm.PolygonLayer(polygons=_build_polygons(state, svc, features), ...)` fresh on each render — no `_refresh_map()` closure.
  - Return `ft.Column([...title..., ft.Container(content=osm_map, ...)], ...)` — not a tuple.
  - Remove `_refresh_map`, `on_country_selected`, `on_group_filter_changed` entirely.
  - All module-level colour constants and `_poly_colours`, `_build_polygons` helpers remain unchanged.
  - Run: `uv run pytest tests/ -q` → 44 passed.

- [ ] T009 **Update `app.py` for `MapView`** — `src/app.py`
  - Change import: `from features.map.views.map_view import MapView` (replacing `build_map_view`).
  - Replace:
    ```python
    map_column, map_state, refresh_map = build_map_view(
        page, svc, on_country_selected=on_country_selected
    )
    ```
    with:
    ```python
    map_control = MapView(page=page, svc=svc, state=map_state)
    ```
    (`map_state` was created in T005.)
  - In `_build_map_body`, replace `map_column` with `map_control`.
  - Remove all remaining references to `refresh_map`, `on_filter_change`, `on_country_selected`.
  - Run: `uv run pytest tests/ -q` → 44 passed.
  - Manual smoke: `uv run flet run src/main.py` — map renders, chips highlight on click, info panel updates on country tap.

---

## Phase 5 — Cleanup & acceptance

**Goal**: Confirm zero imperative `.update()` calls remain in the three view files; update spec acceptance criteria.

- [ ] T010 **[P] Grep check** — run:
  ```bash
  grep -n "\.update()" src/features/map/views/group_filter.py \
                        src/features/map/views/info_panel.py \
                        src/features/map/views/map_view.py
  ```
  Expected: no matches. If any are found, remove them and re-run tests.

- [ ] T011 **[P] Remove dead imports** — in each of the three view files, remove any imports that are no longer referenced after the rewrite (e.g. `Callable` from `collections.abc`, removed callback type annotations).

- [ ] T012 **Final test run** — `uv run pytest tests/ -q` → **44 passed, 0 failed, 0 errors**.

- [ ] T013 **Update spec acceptance criteria** — mark all checkboxes in `specs/008-declarative-observables/spec.md` as `✅`.
