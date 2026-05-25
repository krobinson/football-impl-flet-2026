# Feature Specification: Declarative Observable State — Map & Interaction Layer

**Feature Branch**: `008-declarative-observables`
**Created**: 2026-05-24
**Status**: Draft
**Input**: "please wire up the interaction between the dataclasses and the ui using observables as per https://flet.dev/docs/cookbook/declarative-vs-imperative-crud-app"

---

## Problem Statement

All interactive views in the app are written imperatively: event handlers directly mutate
`ft.Control` properties (`label.color`, `chip.bgcolor`, `text.value`, `container.visible`),
then call `.update()` on each affected control. This scatters rendering logic across
handler closures and makes the relationship between state and UI opaque.

Flet (≥ 0.24) ships a declarative model — `@ft.observable` marks a dataclass as reactive,
`@ft.component` turns a plain function into a rendering unit, and `ft.use_state` tracks
transient UI state across re-renders — eliminating all manual `.update()` calls and making
the UI a pure function of state: **UI = f(state)**.

The three map-related views are the best initial target because they share a single,
well-defined state object (`MapRenderState`) that is already the single source of truth for
the polygon map:

| View | Current style | State it reads |
|------|--------------|----------------|
| `group_filter.py` | Imperative — mutates `chip.bgcolor`/`label.color`, calls `.update()` per chip | `MapRenderState.active_group_filter` |
| `info_panel.py` | Imperative — mutates 5 controls, calls `.update()` per control | `MapRenderState.selected_country` |
| `map_view.py` | Imperative — rebuilds `polygon_layer.polygons`, calls `polygon_layer.update()` | `MapRenderState.selected_country` + `active_group_filter` |

---

## Goals

1. Add `@ft.observable` to `MapRenderState` so any attribute assignment
   (`state.selected_country = …`, `state.active_group_filter = …`) automatically
   schedules a re-render of all components subscribed to those fields.

2. Rewrite `build_group_filter`, `build_info_panel`, and `build_map_view` as
   `@ft.component` functions. Each component reads `MapRenderState` fields directly;
   no callbacks required to propagate state — the reactive re-render handles it.

3. Remove **all** manual `.update()` and `page.update()` calls from those three files.

4. Keep the public signatures compatible with `app.py` so no changes are needed there
   (or changes are trivial).

5. Preserve the 44-test green suite, adding unit tests for observable reactivity where
   practical.

---

## Non-Goals

- Migrating the history/data views (`tournament_view`, `teams_view`, `matches_view`,
  `records_view`, `schedule_view`) — they have no shared state objects; the payoff is low.
- Replacing `features/matches/services.py::DataStore` with an observable model.
- Any visual / UX changes.

---

## Patterns Used (from Flet docs)

### Observables

```python
from dataclasses import dataclass
import flet as ft

@ft.observable
@dataclass
class MapRenderState:
    active_group_filter: str | None = None
    selected_country: ParticipatingCountry | None = None
    # … other fields unchanged
```

Assigning `state.active_group_filter = "A"` now triggers a re-render of every
`@ft.component` that read that field during its last render — no `.update()` needed.

### Components

```python
@ft.component
def GroupFilter(
    groups: list[FIFAGroup],
    state: MapRenderState,
) -> ft.Control:
    def _on_click(group_name: str) -> None:
        state.active_group_filter = (
            None if state.active_group_filter == group_name else group_name
        )
    # return chips — colours derived from state, not mutated
    ...
```

### Hooks (transient UI state)

Not needed for map/group-filter — all state lives in `MapRenderState`.
Would be used if, for example, a tooltip "hover" flag were added to a chip.

---

## File-by-File Changes

### `src/features/map/models.py`

- Add `@ft.observable` decorator to `MapRenderState` (keep `@dataclass`).
- `ParticipatingCountry` and `FIFAGroup` stay frozen — they are value objects, not
  reactive containers; they are passed as props into components.

### `src/features/map/views/group_filter.py`

| Before | After |
|--------|-------|
| `build_group_filter(groups, state, on_filter_change) -> ft.Row` | `@ft.component` function `GroupFilter(groups, state) -> ft.Control` |
| Handler mutates `chip.bgcolor`, `label.color`, calls `chip.update()` | Handler sets `state.active_group_filter`; Flet re-renders |
| Caller must pass `on_filter_change` callback | No callback needed; callers that need to react subscribe to `state` |
| Returns bare `ft.Row` | Returns `ft.Row` constructed fresh on each render from current state |

The `on_filter_change` parameter is **removed** from the public signature. `app.py`
currently calls `on_filter_change` only to call `refresh_map()` — after this change,
`map_view` re-renders automatically when `state.active_group_filter` changes.

### `src/features/map/views/info_panel.py`

| Before | After |
|--------|-------|
| `build_info_panel(initial_country) -> (ft.Container, update_fn)` | `@ft.component` function `InfoPanel(state: MapRenderState) -> ft.Control` |
| Returns a tuple `(panel, update_fn)`; caller must hold `update_fn` | Returns a single control; caller passes `state` |
| `update_fn` mutates 5 controls and calls `.update()` on each | No `update_fn`; panel re-renders when `state.selected_country` changes |

`app.py` currently does:
```python
info_panel, update_info = build_info_panel()
def on_country_selected(country): update_info(country)
```
After this change, `on_country_selected` just assigns:
```python
def on_country_selected(country): state.selected_country = country
```
And `InfoPanel(state=state)` is placed in the layout — no callback chain.

### `src/features/map/views/map_view.py`

| Before | After |
|--------|-------|
| `build_map_view(page, svc, on_country_selected, on_group_filter_changed) -> (ft.Column, MapRenderState, refresh_map)` | `@ft.component` `MapView(page, svc, state) -> ft.Control` |
| `_refresh_map()` rebuilds polygon list, calls `polygon_layer.update()` | Polygon list is derived from `state` on each render; no explicit refresh |
| Returns 3-tuple; caller must thread `refresh_map` through callbacks | Returns a single control; caller holds `state` and mutates it |

### `src/app.py`

Minor surgery to use new component API:

```python
# Old
info_panel, update_info = build_info_panel()
map_column, map_state, refresh_map = build_map_view(page, svc, on_country_selected=…)
filter_row = build_group_filter(svc.get_groups(), map_state, on_filter_change)

# New
map_state = MapRenderState(canvas_width=800.0, canvas_height=400.0)
filter_row   = GroupFilter(groups=svc.get_groups(), state=map_state)
map_control  = MapView(page=page, svc=svc, state=map_state)
info_control = InfoPanel(state=map_state)
```

`on_resized` still runs but only adjusts layout geometry, not state.

---

## Public API Contract Changes (summary)

| Symbol | Old signature | New signature |
|--------|--------------|---------------|
| `build_group_filter` | `(groups, state, on_filter_change) → ft.Row` | replaced by `GroupFilter` component |
| `build_info_panel` | `(initial_country?) → (ft.Container, Callable)` | replaced by `InfoPanel` component |
| `build_map_view` | `(page, svc, on_country_selected?, on_group_filter_changed?) → tuple` | replaced by `MapView` component |
| `MapRenderState` | plain `@dataclass` | `@ft.observable @dataclass` |

> **Compatibility note**: old `build_*` names can remain as thin shim wrappers returning
> the component instances, giving downstream code a migration window. Alternatively they
> are removed immediately since all callers live in `app.py`.

---

## Test Plan

| Test | Approach |
|------|----------|
| `test_models.py` — `MapRenderState` still mutable | Existing tests pass unchanged |
| Observable reactivity | New test: create `MapRenderState`, attach a mock observer, assert re-render triggered on field assignment |
| `GroupFilter` renders correct chip colours | Snapshot / property test: `active_group_filter="A"` → chip A has `_CHIP_ACTIVE_BG` colour |
| `InfoPanel` renders correct country name | Property test: set `state.selected_country = some_country`, assert panel text |
| Integration: 44 existing tests remain green | `uv run pytest tests/ -q` |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `@ft.observable` / `@ft.component` / `ft.use_state` require Flet ≥ 0.24 | Check installed version; `flet==0.84.0` ✅ ships these APIs |
| `PolygonLayer` still requires imperative `layer.polygons = …` inside `@ft.component` | Acceptable — the layer itself is not an observable; the component re-runs and sets the attribute, then Flet batches the delta |
| flet-map `ftm.Map` `on_tap` still imperative | `_on_map_tap` assigns to `state.selected_country` (observable mutation); no `.update()` needed |
| Removing `on_filter_change` callback may break other subscribers | Audit shows only `app.py` uses it; no other subscriber |

---

## Acceptance Criteria

- [ ] `MapRenderState` is `@ft.observable`.
- [ ] `GroupFilter`, `InfoPanel`, `MapView` are `@ft.component` functions.
- [ ] Zero manual `.update()` or `page.update()` calls in those three files.
- [ ] `app.py` creates `MapRenderState` once, passes it to all three components.
- [ ] `uv run pytest tests/ -q` → 44 passed, 0 failed.
- [ ] App launches with `flet run src/main.py` — map renders, group chips highlight, info panel updates on tap.
