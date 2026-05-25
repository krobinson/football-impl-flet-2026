# Implementation Plan: Declarative Observable State — Map & Interaction Layer

**Branch**: `008-declarative-observables` | **Date**: 2026-05-24 | **Spec**: [spec.md](spec.md)

---

## Summary

Migrate the three map-layer views from Flet's imperative style (direct control mutation +
`.update()`) to the declarative style (`@ft.observable` state + `@ft.component` rendering).
The core idea is **UI = f(state)**: `MapRenderState` becomes the single reactive source
of truth; `GroupFilter`, `InfoPanel`, and `MapView` become pure rendering functions that
Flet re-runs automatically whenever the state they read changes.

---

## Technical Context

| Item | Value |
|------|-------|
| Language | Python 3.13 |
| Flet version | `flet==0.84.0` (ships `@ft.observable`, `@ft.component`, `ft.use_state`) |
| flet-map | `flet-map==0.84.0` |
| Runner | `uv run flet run src/main.py` |
| Tests | `uv run pytest tests/ -q` → must stay 44 passed |
| Entry point | `src/main.py` → `src/app.py::main` |
| State object | `src/features/map/models.py::MapRenderState` |
| Target views | `features/map/views/group_filter.py`, `info_panel.py`, `map_view.py` |
| Caller | `src/app.py` (sole consumer of all three views) |

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Flet-First UI | ✅ PASS | All rendering via Flet components; no JS/Tkinter |
| Feature-Module Separation | ✅ PASS | Changes confined to `features/map/`; no cross-feature imports added |
| Test-First | ✅ PASS | New observable/component tests written before implementation in Phase 2 |
| API-Backed Data Layer | ✅ PASS | `WorldCupDataService` unchanged; components receive it as a prop |
| Simplicity & YAGNI | ✅ PASS | Only the three views with a shared state object are migrated; history tabs stay imperative |

---

## Project Structure

### Documentation (this feature)

```
specs/008-declarative-observables/
├── plan.md        ← this file
└── spec.md        ← requirements & API contract
```

### Source Files Changed

```
src/
├── app.py                                  ← wiring updated (create MapRenderState once)
├── features/
│   └── map/
│       ├── models.py                       ← @ft.observable added to MapRenderState
│       └── views/
│           ├── group_filter.py             ← build_group_filter → GroupFilter component
│           ├── info_panel.py               ← build_info_panel → InfoPanel component
│           └── map_view.py                 ← build_map_view → MapView component
tests/
└── unit/
    └── test_models.py                      ← existing + new observable reactivity tests
```

---

## Phase 0 — Research (done, documented in spec)

Key findings already captured in spec.md:

- `flet==0.84.0` ships `@ft.observable`, `@ft.component`, `ft.use_state`. No version bump needed.
- `@ft.observable` wraps a dataclass: field assignments trigger re-renders in subscribed components.
- `@ft.component` turns a plain function into a rendering unit; it re-runs when any observable it read changes.
- `PolygonLayer.polygons` assignment inside a component is fine — Flet batches the delta per frame.
- `ftm.Map.on_tap` handler assigns to `state.selected_country` (observable write) — no `.update()` needed.
- Only `app.py` calls the three `build_*` functions; no other subscribers to break.

---

## Phase 1 — Design

### Data flow (before → after)

**Before** (imperative):
```
on_tap → _on_map_tap() → state.selected_country = c → on_country_selected(c) → update_info(c) → 5× ctrl.update()
chip click → _on_chip_click() → state.active_group_filter = g → on_filter_change(g) → refresh_map() → polygon_layer.update()
```

**After** (declarative):
```
on_tap → state.selected_country = c    ← Flet re-renders InfoPanel + MapView automatically
chip click → state.active_group_filter = g    ← Flet re-renders GroupFilter + MapView automatically
```

### `MapRenderState` decorated as observable

```python
# features/map/models.py
import flet as ft

@ft.observable       # NEW — field assignments now trigger component re-renders
@dataclass
class MapRenderState:
    canvas_width: float = 800.0
    canvas_height: float = 400.0
    active_group_filter: str | None = None
    selected_country: ParticipatingCountry | None = None
    pan_x: float = 0.0
    pan_y: float = 0.0
    zoom: float = 1.0

    def reset_view(self) -> None:
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.zoom = 1.0
```

`reset_view()` still works — each attribute assignment triggers a re-render; three
consecutive assignments are batched by Flet into a single repaint.

### `GroupFilter` component

```python
# features/map/views/group_filter.py
@ft.component
def GroupFilter(groups: list[FIFAGroup], state: MapRenderState) -> ft.Control:
    def _on_click(group_name: str) -> None:
        state.active_group_filter = (
            None if state.active_group_filter == group_name else group_name
        )

    chips = [
        ft.Container(
            content=ft.Text(
                f"Group {g.name}",
                size=12,
                weight=ft.FontWeight.W_500,
                color=_CHIP_TEXT_ACTIVE if state.active_group_filter == g.name
                      else _CHIP_TEXT_INACTIVE,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=20,
            bgcolor=_CHIP_ACTIVE_BG if state.active_group_filter == g.name
                    else _CHIP_INACTIVE_BG,
            on_click=lambda e, name=g.name: _on_click(name),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )
        for g in groups
    ]
    return ft.Row(controls=chips, wrap=True, spacing=6, run_spacing=6)
```

Key differences from imperative version:
- No mutable `chips` list saved across calls; each render builds fresh chips from state.
- No `_refresh_chips()` loop; colour is derived inline from `state.active_group_filter`.
- No `chip.update()`.
- `on_filter_change` callback parameter removed.

### `InfoPanel` component

```python
# features/map/views/info_panel.py
@ft.component
def InfoPanel(state: MapRenderState) -> ft.Control:
    country = state.selected_country
    if country is None:
        flag, name, group_txt, appear_txt, badge_visible = "🌍", "Select a country", "", "", False
    else:
        flag = country.flag_emoji
        name = country.name
        group_txt = f"Group {country.group}"
        appear_txt = f"World Cup appearances: {country.appearances}"
        badge_visible = True

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(flag, size=48),
                ft.Text(name, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(group_txt, size=14, color=ft.Colors.GREY_300),
                ft.Text(appear_txt, size=13, color=ft.Colors.GREY_400),
                ft.Container(
                    content=ft.Text("✓ FIFA WC 2026", size=12, color=_ACCENT,
                                    weight=ft.FontWeight.BOLD),
                    visible=badge_visible,
                ),
            ],
            spacing=4,
        ),
        padding=16,
        bgcolor=_PANEL_BG,
        border_radius=8,
        width=280,
    )
```

Key differences:
- No `initial_country` parameter; state is always read from `MapRenderState`.
- Returns a plain `ft.Container` (not a tuple).
- No `_set()` update function; no 5× `.update()`.

### `MapView` component

```python
# features/map/views/map_view.py
@ft.component
def MapView(page: ft.Page, svc: WorldCupDataService, state: MapRenderState) -> ft.Control:
    features = svc.get_geo_features()

    polygon_layer = ftm.PolygonLayer(
        polygons=_build_polygons(state, svc, features),
        polygon_culling=True,
        simplification_tolerance=0.5,
    )

    def _on_map_tap(e: ftm.MapTapEvent) -> None:
        iso = geo_hit_test(e.coordinates.longitude, e.coordinates.latitude, features)
        state.selected_country = svc.get_team(iso) if iso else None
        # No refresh_map() call — observable assignment triggers re-render

    osm_map = ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(20.0, 10.0),
        initial_zoom=2.0,
        interaction_configuration=ftm.InteractionConfiguration(
            flags=ftm.InteractionFlag.ALL,
        ),
        on_tap=_on_map_tap,
        layers=[
            ftm.TileLayer(...),
            polygon_layer,
            ftm.SimpleAttribution(...),
        ],
    )
    return ft.Column(controls=[...title..., osm_map], spacing=8, expand=True)
```

Key differences:
- No `_refresh_map()` closure.
- No `polygon_layer.update()`.
- No `on_country_selected` or `on_group_filter_changed` callback parameters.
- Returns a single `ft.Control`, not a 3-tuple.

> **Note on PolygonLayer**: `PolygonLayer` is a flet-map type, not a Flet observable.
> When `MapView` re-renders (triggered by `state` changes), it constructs a fresh
> `PolygonLayer` with the updated polygon list. Flet diffs the control tree and
> patches only what changed.

### `app.py` wiring changes

```python
# Old (three separate build calls + callback chain)
info_panel, update_info = build_info_panel()
def on_country_selected(country): update_info(country)
map_column, map_state, refresh_map = build_map_view(
    page, svc, on_country_selected=on_country_selected
)
def on_filter_change(group_name): map_state.active_group_filter = group_name; refresh_map()
filter_row = build_group_filter(svc.get_groups(), map_state, on_filter_change)

# New (one state object, three components)
map_state = MapRenderState(canvas_width=800.0, canvas_height=400.0)
filter_row   = GroupFilter(groups=svc.get_groups(), state=map_state)
map_control  = MapView(page=page, svc=svc, state=map_state)
info_control = InfoPanel(state=map_state)
```

`_build_map_body()` replaces `map_column` with `map_control` and `info_panel` with
`info_control`. `on_resized` remains — it only adjusts layout geometry (heights, widths),
not state. The `page.render(AppView)` pattern from the docs is **not** used here;
`app.py::main` is a standard `ft.Page` callback (required by `[tool.flet.app]`), so
components are placed via the existing `ft.Stack` / `ft.Column` layout.

---

## Phase 2 — Implementation Order

Each step is independently runnable; tests must be green after each step.

### Step 1 · Add `@ft.observable` to `MapRenderState`

**File**: `src/features/map/models.py`

Change:
```python
# before
@dataclass
class MapRenderState:
```
```python
# after
@ft.observable
@dataclass
class MapRenderState:
```

Add `import flet as ft` (already present via existing `ft` usage — confirm).

Run: `uv run pytest tests/unit/test_models.py -q` — must pass unchanged (4 tests).

Add new test to `tests/unit/test_models.py`:
```python
def test_map_render_state_is_observable() -> None:
    """MapRenderState carries the Flet observable marker."""
    assert hasattr(MapRenderState, "__ft_observable__") or callable(
        getattr(ft, "observable", None)
    )
```

---

### Step 2 · Rewrite `GroupFilter` as `@ft.component`

**File**: `src/features/map/views/group_filter.py`

- Replace `build_group_filter(groups, state, on_filter_change)` with
  `@ft.component def GroupFilter(groups, state)`.
- Derive chip colours from `state.active_group_filter` inline (no `_refresh_chips`).
- Handler body: single assignment to `state.active_group_filter`.
- Keep old `build_group_filter` as a one-line alias (or remove immediately — only
  `app.py` calls it).

**File**: `src/app.py`

- Replace `build_group_filter(svc.get_groups(), map_state, on_filter_change)` with
  `GroupFilter(groups=svc.get_groups(), state=map_state)`.
- Remove the `on_filter_change` closure.

Run: `uv run pytest tests/ -q` — 44 passed.

---

### Step 3 · Rewrite `InfoPanel` as `@ft.component`

**File**: `src/features/map/views/info_panel.py`

- Replace `build_info_panel(initial_country?)` with
  `@ft.component def InfoPanel(state: MapRenderState)`.
- Panel is built from `state.selected_country`; no `_set()`.
- Returns a plain `ft.Container`.

**File**: `src/app.py`

- Replace:
  ```python
  info_panel, update_info = build_info_panel()
  def on_country_selected(country): update_info(country)
  ```
  with:
  ```python
  info_control = InfoPanel(state=map_state)
  ```
- `on_country_selected` callback removed entirely (or kept as `state.selected_country = country`
  if needed elsewhere — in practice the callback is no longer required).
- Rename `info_panel` references in `_build_map_body` to `info_control`.

Run: `uv run pytest tests/ -q` — 44 passed.

---

### Step 4 · Rewrite `MapView` as `@ft.component`

**File**: `src/features/map/views/map_view.py`

- Replace `build_map_view(page, svc, …)` with
  `@ft.component def MapView(page, svc, state)`.
- `_on_map_tap` assigns `state.selected_country` — no `refresh_map()` call.
- No `_refresh_map` closure; `PolygonLayer` built from `state` on each render.
- Returns `ft.Column` (not a 3-tuple).

**File**: `src/app.py`

- Replace:
  ```python
  map_column, map_state, refresh_map = build_map_view(page, svc, on_country_selected=…)
  def on_filter_change(g): map_state.active_group_filter = g; refresh_map()
  ```
  with:
  ```python
  map_control = MapView(page=page, svc=svc, state=map_state)
  ```
- Remove all remaining references to `refresh_map`, `on_filter_change`, `on_country_selected`.
- `_build_map_body` uses `map_control` in place of `map_column`.

Run: `uv run pytest tests/ -q` — 44 passed.
Manual smoke test: `flet run src/main.py` — map renders, group chips highlight, info panel updates on tap.

---

### Step 5 · Cleanup & final checks

- Confirm zero `ctrl.update()` or `page.update()` calls remain in the three view files
  (grep check).
- Remove any now-unused imports.
- Run full test suite once more.
- Update spec.md acceptance criteria checkboxes to ✅.

---

## Execution Checklist

```
[ ] Step 1 · models.py — @ft.observable on MapRenderState + new test
[ ] Step 2 · group_filter.py — GroupFilter component + app.py update
[ ] Step 3 · info_panel.py — InfoPanel component + app.py update
[ ] Step 4 · map_view.py — MapView component + app.py update
[ ] Step 5 · cleanup, grep check, final test run
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| `@ft.observable` not available in `flet==0.84.0` | Low | High | Verify with `python -c "import flet as ft; print(hasattr(ft, 'observable'))"` before Step 1 |
| `@ft.component` re-creates `ftm.Map` on every state change (expensive) | Medium | Medium | Cache `ftm.Map` instance with `ft.use_state` if re-mount flicker observed |
| `PolygonLayer` throws if polygons list is mutated from background thread | Low | Low | `on_tap` fires on the main Flet thread; no threading concern |
| `app.py` mobile layout (`_build_map_body`) still references old `map_column` | Medium | Low | Steps 3–4 explicitly rename to `map_control`; grep confirms no stale refs |
| Removing callback chain breaks a future caller | n/a | n/a | Only `app.py` calls these functions; centralised in single file |
