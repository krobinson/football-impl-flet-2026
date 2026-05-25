# Tasks: World Cup Participating Countries Map

**Input**: Design documents from `specs/001-worldcup-map/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and base structure

- [x] T001 Create directory structure: `src/views/`, `src/services/`, `src/shared/`, `src/assets/`, `tests/unit/`, `tests/integration/`
- [x] T002 Add Python pattern entries to `.gitignore` (`__pycache__/`, `*.pyc`, `.venv/`, `src/assets/countries.geojson`)
- [x] T003 Download Natural Earth 1:110m GeoJSON to `src/assets/countries.geojson` (see quickstart.md step 1)
- [x] T004 Create `src/assets/worldcup2026.json` with all 48 FIFA World Cup 2026 qualified teams (iso_a3, name, group A–L, appearances, flag_emoji)

---

## Phase 2: Foundational (Shared models + geo utilities)

**Purpose**: Data layer prerequisites used by all user stories

- [x] T005 [P] Create `src/shared/__init__.py` (empty)
- [x] T006 [P] Create `src/services/__init__.py` (empty)
- [x] T007 [P] Create `src/views/__init__.py` (empty)
- [x] T008 Create `src/shared/models.py` — `ParticipatingCountry` and `FIFAGroup` frozen dataclasses per data-model.md
- [x] T009 Create `src/shared/geo_utils.py` — `project(lon, lat, width, height)` equirectangular projection and `hit_test(px, py, features, width, height)` ray-casting point-in-polygon per contracts/worldcup-data-contract.md
- [x] T010 Create `src/services/worldcup_data.py` — `WorldCupDataService` class with constructor, all query methods, and validation per contracts/worldcup-data-contract.md

---

## Phase 3: User Story 1 — View World Cup Countries on Map (P1)

**Story goal**: Interactive world map with all 48 qualifying nations highlighted
**Independent test**: Open app in browser → all 48 countries are visually distinct from non-qualifiers

- [x] T011 [US1] Create `src/views/map_view.py` skeleton — `build_map_view(page, data_service)` function returning `ft.Container` with a `ft.Stack` housing canvas and controls
- [x] T012 [US1] Implement `_build_canvas(data_service, state)` in `src/views/map_view.py` — iterate GeoJSON features, project polygon rings with `geo_utils.project`, draw each country using `ft.canvas.Path` / `ft.canvas.Fill` / `ft.canvas.Stroke`; qualifying countries in `#2ECC71`, non-qualifying in `#BDC3C7`, borders in `#7F8C8D` at 0.5px
- [x] T013 [US1] Wrap canvas in `ft.GestureDetector(on_tap_down=_on_map_tap)` in `src/views/map_view.py`; `_on_map_tap` calls `geo_utils.hit_test` and stores result in `MapRenderState.selected_country`
- [x] T014 [US1] Update `src/main.py` — minimal entry point: construct `WorldCupDataService`, call `build_map_view`, add to `page`, set `page.title = "FIFA World Cup 2026 Map"` and `page.bgcolor = "#1A1A2E"`
- [x] T015 [US1] Add error banner to `src/views/map_view.py` — catch `FileNotFoundError` / `ValueError` from service constructor and display `ft.Banner` with error message instead of the map

---

## Phase 4: User Story 2 — Inspect Country Details (P2)

**Story goal**: Click a qualifying country → info panel shows name, group, flag, appearances
**Independent test**: Click any highlighted country → panel appears with correct details; click elsewhere → panel closes

- [x] T016 [P] [US2] Create `src/views/info_panel.py` — `build_info_panel(country: ParticipatingCountry | None) -> ft.Container` returns a styled card with flag emoji, country name, group badge, appearances count; returns empty `ft.Container` when `country` is `None`
- [x] T017 [US2] Integrate info panel into `src/views/map_view.py` — add panel to the `ft.Stack`; on `_on_map_tap`, update `MapRenderState.selected_country` and call `page.update()` to show/hide panel; clicking non-qualifying country closes any open panel

---

## Phase 5: User Story 3 — Filter by FIFA Group (P3)

**Story goal**: Dropdown/button bar to isolate one group; selected group shown in amber, others dimmed
**Independent test**: Select "Group A" → only 4 Group A nations turn amber; clear → all 48 return to green

- [x] T018 [P] [US3] Create `src/views/group_filter.py` — `build_group_filter(groups, on_select) -> ft.Row` renders labelled toggle buttons (A–L + "All"); calls `on_select(group_letter | None)` on tap
- [x] T019 [US3] Connect group filter to map in `src/views/map_view.py` — `on_select` updates `MapRenderState.active_group_filter`; redraw colours: active-group countries `#F39C12` (amber), non-active-group qualifiers `#95A5A6` (dimmed), non-qualifiers `#BDC3C7`; call `canvas.update()`

---

## Phase 6: Tests (Unit + Integration)

**Purpose**: Verify all stories per TDD principle III

- [x] T020 [P] Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`
- [x] T021 [P] Create `tests/unit/test_models.py` — test `ParticipatingCountry` and `FIFAGroup` construction, frozen immutability, validation constraints
- [x] T022 [P] Create `tests/unit/test_geo_utils.py` — test `project()` boundary values (corners, 0° meridian), test `hit_test()` with a synthetic 1-feature GeoJSON polygon
- [x] T023 [P] Create `tests/unit/test_worldcup_data.py` — test `WorldCupDataService` with fixture JSON: correct count, `get_team()`, `get_groups()`, `is_qualifier()`, error on missing file, error on count ≠ 48
- [x] T024 Create `tests/integration/test_map_view.py` — smoke test: build `WorldCupDataService` from real `src/assets/worldcup2026.json`, verify 48 teams load, all group letters A–L present, all `iso_a3` values non-empty

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T025 Add `pytest` to `pyproject.toml` dev dependencies and create `pytest.ini` (or `[tool.pytest.ini_options]` section) pointing to `tests/`
- [x] T026 Add `src/assets/countries.geojson` to `.gitignore` (large file, downloaded locally)
- [x] T027 Verify `uv run flet run --web` starts without errors and map renders in browser
- [x] T028 Add page-level responsive layout: `page.on_resize` handler triggers canvas redraw with updated `canvas_width` / `canvas_height` from `page.width` / `page.height`

---

## Dependencies

```
Phase 1 → Phase 2 (assets must exist before service loads them)
Phase 2 → Phase 3 (service + models + geo_utils needed for map)
Phase 3 → Phase 4 (info panel layers on top of map)
Phase 4 → Phase 5 (group filter modifies existing map state)
Phases 3-5 → Phase 6 (tests validate implemented behaviour)
Phase 6 → Phase 7 (polish after tests pass)
```

## Parallel Execution (within phases)

- Phase 2: T005, T006, T007 → run together (different empty init files)
- Phase 4+5: T016, T018 → run together (different files, no shared state)
- Phase 6: T020–T023 → run together (independent test files)

## Implementation Strategy

**MVP (Phase 1–3)**: Delivers User Story 1 — the full highlighted world map with click
  detection. Deployable and demonstrable independently.

**Increment 2 (Phase 4)**: Adds info panel — visible value for stakeholders.

**Increment 3 (Phase 5)**: Adds group filter — completes all specification requirements.

**Increment 4 (Phases 6–7)**: Tests + polish — production-ready.
