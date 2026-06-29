# Implementation Plan: Schedule Group Stage Display

**Branch**: `012-schedule-group-display` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/012-schedule-group-display/spec.md`

---

## Summary

Enhance the existing Schedule tab with (1) a chip-based group selector replacing the current dropdown, (2) full stadium venue names instead of city names, and (3) confirmed score display for finished matches and UTC kickoff + venue for upcoming matches. All data already comes from the existing `FootballDataClient.get_group_matches()` — no new API calls or services required. Changes are confined to `schedule_view.py` and `match_row.py`.

---

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Flet ≥ 0.84, `flet[all]`; football-data.org API via `FootballDataClient`
**Storage**: N/A — data loaded in-memory per session
**Testing**: pytest (`tests/unit/`, `tests/integration/`)
**Target Platform**: Web + Desktop (Flet cross-platform)
**Project Type**: Feature increment on existing desktop/web app
**Performance Goals**: Chip filter response < 0.5 s (SC-002, client-side only)
**Constraints**: No new dependencies; no signature changes to `build_schedule_view()`; no calls to external API from UI layer (Constitution IV)
**Scale/Scope**: 48 group-stage matches, 13 chip options, 2 files modified

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Flet-First UI | ✅ PASS | Chips are plain `ft.Container` + `on_click`; no `ft.UserControl` |
| II. Feature-Module Separation | ✅ PASS | Changes confined to `features/schedule/`; no cross-feature imports |
| III. Test-First | ✅ PASS | Tests written before implementation (tasks enforce Red→Green) |
| IV. API-Backed Data Layer | ✅ PASS | UI reads from `_state["all_matches"]`; never calls API directly |
| V. Simplicity & YAGNI | ✅ PASS | No new services, models, or abstractions; minimal diff to 2 files |

All gates pass. No violations to document.

---

## Project Structure

### Documentation (this feature)

```
specs/012-schedule-group-display/
├── plan.md              ← this file
├── research.md          ← Phase 0 ✅
├── data-model.md        ← Phase 1 ✅
├── quickstart.md        ← Phase 1 ✅
├── contracts/
│   └── schedule_ui.md   ← Phase 1 ✅
└── tasks.md             ← Phase 2 (created by /speckit.tasks)
```

### Files modified by this feature

```
src/features/schedule/
├── views/
│   └── schedule_view.py     ← replace group_dd with chips_row; update _state
└── components/
    └── match_row.py         ← venue column: raw venue name instead of city

tests/unit/
└── test_schedule_group_display.py   ← NEW — TDD tests
```

No new files in `src/`. No changes to `app.py`, `core/`, or other features.

---

## Phase 0: Research Summary

Six decisions resolved — see [research.md](research.md) for full rationale.

| # | Decision | Chosen approach |
|---|----------|----------------|
| 1 | Group selector UI | Chips (`ft.Container` + `on_click`), not dropdown or Tabs |
| 2 | Venue display | Raw API `venue` field (stadium name), not `venue_to_city()` city |
| 3 | Chip state management | `_state["active_group"]` + manual `.update()` |
| 4 | `match_row()` changes | Internal-only: rename city → venue column; no signature change |
| 5 | Service layer | Existing `get_group_matches()` unchanged; no new service needed |
| 6 | Chip row layout | `ft.Row(wrap=True)` — reflows on narrow viewports (SC-005) |

---

## Phase 1: Design Summary

### Data model

No new dataclasses. One new `_state` key: `active_group: str` (default `"All"`).
See [data-model.md](data-model.md).

### Contracts

Three contracts defined — see [contracts/schedule_ui.md](contracts/schedule_ui.md):
1. `_build_group_chips(active_group, on_select) -> ft.Row`
2. `match_row()` venue column change (internal)
3. `build_schedule_view()` public signature unchanged

### Quickstart

See [quickstart.md](quickstart.md) — run + manual acceptance test instructions.

---

## Post-Design Constitution Re-check

All five gates still pass after design. No new complexity introduced.
