# Tasks: Remove History/Teams/Matches/Records Tabs

**Input**: Design documents from `specs/013-remove-history-tabs/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/app_wiring.md ✅  
**Tests**: No new tests (none requested in spec; no new logic added)  
**Organization**: Single user story (US1) — single file change to `src/app.py`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story — `[US1]` for all implementation tasks below
- All tasks target `src/app.py` (sequential — same file)

---

## Phase 1: User Story 1 — Simplified 3-tab navigation (Priority: P1) 🎯 MVP

**Goal**: Remove 4 tabs (History, Teams, Matches, Records) from the app navigation bar, leaving only 2026 Map, Venues, and Schedule.

**Independent Test**: `uv run flet run --web src/main.py` → navigation bar shows exactly 3 destinations (2026 Map, Venues, Schedule) with no errors. Each tab loads its content correctly.

### Implementation for User Story 1

- [X] T001 [US1] Remove 5 unused imports (`get_data_store`, `build_tournament_view`, `build_teams_view`, `build_matches_view`, `build_records_view`) from `src/app.py`
- [X] T002 [US1] Remove 4 content-block variables (`tournament_content`, `teams_content`, `matches_content`, `records_content`) and the `# ── History tabs` comment block from `_build_app()` in `src/app.py`
- [X] T003 [US1] Rewrite `tab_bodies` to 3 entries `[map_tab_content, osm_content, schedule_content]` and update `nav.destinations` to 3 entries (2026 Map, Venues, Schedule) in `src/app.py`
- [X] T004 [US1] Remove `store` parameter from `_build_app()` signature; remove `store = get_data_store()` from `main()`; update `page.render()` call to drop `store` argument in `src/app.py`
- [X] T005 [US1] Update module docstring from `"7-tab layout"` to `"3-tab layout"` in `src/app.py`

**Checkpoint**: At this point US1 is fully delivered — navigation bar shows exactly 3 tabs, imports are clean, `store` is gone from the startup path.

---

## Final Phase: Regression Verification

- [X] T006 Run full test suite `uv run pytest tests/ -q` and confirm all 143 existing tests pass with zero failures

---

## Dependencies

No inter-story dependencies (single story). All T001–T005 tasks are sequential on `src/app.py`; T006 runs after all edits are applied.

```
T001 → T002 → T003 → T004 → T005 → T006
```

## Parallel Execution

No parallelism — all tasks touch the same file (`src/app.py`). Execute sequentially in T001–T006 order.

## Implementation Strategy

**MVP = T001 + T002 + T003 + T004 + T005** (all in one PR — atomic change as described in spec).  
**Verification = T006** (regression gate — zero regressions expected).
