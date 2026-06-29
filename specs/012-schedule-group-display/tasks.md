# Tasks: Schedule Group Stage Display

**Input**: Design documents from `specs/012-schedule-group-display/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story — US1, US2, US3
- TDD required (constitution III): test tasks marked **⚠️ Write FIRST — must FAIL before implementation**

---

## Phase 1: Setup

**Purpose**: Create the shared test file with fixtures so all user story test tasks have a valid import target and data to work with.

- [X] T001 Create `tests/unit/test_schedule_group_display.py` with shared pytest fixtures: minimal match dicts for `SCHEDULED`, `TIMED`, `FINISHED`, `IN_PLAY` statuses across two groups (GROUP_C and GROUP_E), covering missing-venue case

**Checkpoint**: Test file importable; fixtures available; `uv run pytest tests/unit/test_schedule_group_display.py` collects 0 tests (no errors).

---

## Phase 2: User Story 1 — Browse Matches by Group (Priority: P1) 🎯 MVP

**Goal**: A chip row (All, A–L) replaces the dropdown. Selecting a chip instantly filters the match list to that group. "All" restores all matches.

**Independent Test**: Open Schedule tab — 13 chips visible. Click "Group C" — only GROUP_C matches shown. Click "All" — all matches return.

### Tests ⚠️ Write FIRST — must FAIL before implementation

- [X] T002 [US1] Write failing tests for `_apply_group_filter` logic in `tests/unit/test_schedule_group_display.py`: given all matches loaded, when `active_group="C"`, only `GROUP_C` matches returned; when `"All"`, all returned; result sorted by `matchday` asc then `utcDate` asc

### Implementation

- [X] T003 [US1] Implement `_build_group_chips(active_group: str, on_select: Callable) -> ft.Row` helper in `src/features/schedule/views/schedule_view.py`: 13 chips (All + A–L), active chip amber `#F39C12` / inactive dark `#2C3E50`, `wrap=True`
- [X] T004 [US1] Refactor `build_schedule_view()` in `src/features/schedule/views/schedule_view.py`: remove `group_dd` dropdown and `lr = loading_row([group_dd])`; add `_state["active_group"] = "All"`; build `chips_row` via `_build_group_chips`; wire chip `on_select` to update `_state["active_group"]` and call `_apply_group_filter`; update `_apply_group_filter` to read `_state["active_group"]` instead of `group_dd.value`; render `chips_row` and `lr.row` (loading indicator) separately above the match list

**Checkpoint**: US1 fully functional. Group chips visible; filtering works; loading notice still appears without API key.

---

## Phase 3: User Story 2 — Upcoming Match Details: Kickoff Time + Venue (Priority: P1)

**Goal**: Every match row shows the full stadium name (e.g. "MetLife Stadium") instead of the city. "TBD" shown when no venue data.

**Independent Test**: Find any unplayed match row. Confirm venue column shows stadium name, not city. Find a match with no venue — confirms "TBD".

### Tests ⚠️ Write FIRST — must FAIL before implementation

- [X] T005 [P] [US2] Write failing tests for `match_row()` venue display in `tests/unit/test_schedule_group_display.py`: a `SCHEDULED` match with `venue="MetLife Stadium"` renders "MetLife Stadium" (not a city); a match with `venue=None` renders "TBD"; column header in `header_row()` reads "Venue" not "City"

### Implementation

- [X] T006 [US2] In `src/features/schedule/components/match_row.py`: change `city = venue_to_city(match.get("venue") or "")` to `venue_name = match.get("venue") or "TBD"`; update the last `ft.Container` column to display `venue_name`; in `header_row()` change `_h("City", width=140)` to `_h("Venue", width=140)`

**Checkpoint**: US2 fully functional. Stadium names visible; TBD for missing venue; T005 tests pass.

---

## Phase 4: User Story 3 — Finished Match Results (Priority: P1)

**Goal**: Finished matches show the full-time score prominently; "FT" badge is visually muted. Live matches show "LIVE" badge in green. Upcoming matches show "vs".

**Independent Test**: Find a finished match — score "X – Y" in amber bold, "FT" in grey. Find a scheduled match — "vs" in grey. Both visually distinguishable.

### Tests ⚠️ Write FIRST — must FAIL before implementation

- [X] T007 [P] [US3] Write tests for `match_row()` score and status display in `tests/unit/test_schedule_group_display.py`: `FINISHED` match with `score.fullTime={home:2, away:1}` renders "2–1" and status text "FT"; `SCHEDULED` match renders "vs"; `IN_PLAY` match renders "LIVE"; `PAUSED` match renders "HT"

### Implementation

- [X] T008 [US3] Run `uv run pytest tests/unit/test_schedule_group_display.py::TestMatchRowScoreStatus -v` — verify T007 tests already pass (existing `_score_text` and `_STATUS_LABEL` in `match_row.py` already implement this correctly); if any fail, fix in `src/features/schedule/components/match_row.py`

**Checkpoint**: US3 fully functional. All three user stories independently verified.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T009 [P] Run full test suite `uv run pytest tests/ -q` — all tests pass, no regressions; confirm 120+ tests pass including new `test_schedule_group_display.py`

---

## Dependencies

```
Phase 1 (T001 — fixtures)
    └── Phase 2 (T002 → T003 → T004)
            └── Phase 3 (T005 → T006)
                    └── Phase 4 (T007 → T008)
                            └── Phase 5 (T009)
```

Story independence:
- **US1** (T002–T004): Group chips demo-able before venue/score changes.
- **US2** (T005–T006): `match_row.py` change is independent of view chip logic — T005/T006 can be developed in parallel with T003/T004 since they touch different files.
- **US3** (T007–T008): Likely already passing — verification task only.

---

## Parallel Execution Examples

**US1 implementation + US2 tests (after T001)**:
```
T002 (chip filter tests)  ←→  T005 (venue display tests) [different files]
→ T003 (build chips fn)   ←→  T006 (venue column fix)    [different files]
→ T004 (wire into view)
```

**US3 test + US1 wiring (after T003)**:
```
T007 (score/status tests) ← parallel with T004 (view wiring)
```

---

## Implementation Strategy

**MVP scope**: All three user stories are P1 and form a single coherent increment — deliver T001–T008 as one slice.

Suggested order for a single developer:
1. T001 (fixtures) → T002 (chip tests) → T003 (chips fn) → T004 (wire view) — US1 done
2. T005 (venue tests) → T006 (venue fix) — US2 done
3. T007 (score tests) → T008 (verify) — US3 done
4. T009 (full suite) — ship

---

## Task Count Summary

| Phase | Tasks | User Story |
|-------|-------|------------|
| Phase 1: Setup | 1 | — |
| Phase 2: US1 | 3 | US1 (P1) |
| Phase 3: US2 | 2 | US2 (P1) |
| Phase 4: US3 | 2 | US3 (P1) |
| Phase 5: Polish | 1 | — |
| **Total** | **9** | |
