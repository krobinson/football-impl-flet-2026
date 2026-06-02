# Tasks: Team Tournament Progression

**Input**: Design documents from `specs/011-team-progression/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story — US1, US2, US3
- TDD required (constitution III): test tasks marked with **⚠️ Write FIRST — must FAIL before implementation**

---

## Phase 1: Setup

**Purpose**: Create the new tournament services module skeleton so all subsequent tasks have a valid import target.

- [X] T001 Create `src/features/tournament/services.py` with module docstring and `__all__` stub

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data model dataclasses, round-priority logic, and shared test fixtures that ALL user stories depend on. No story work can begin until this phase is complete.

- [X] T002 [P] Implement `MatchRow`, `RoundGroup`, `TeamProgression` dataclasses in `src/features/tournament/services.py`
- [X] T003 [P] Implement `ROUND_PRIORITY` constant dict and `_round_priority(stage: str) -> int` helper in `src/features/tournament/services.py`
- [X] T004 [P] Create `tests/unit/test_tournament_progression.py` with shared pytest fixtures: minimal `matches_df` covering group stage + knockout rows for years 2022 and 2018

**Checkpoint**: Dataclasses importable; fixture data available; no user story tasks blocked.

---

## Phase 3: User Story 1 — View Team Path Through Tournament (Priority: P1) 🎯 MVP

**Goal**: Any user selecting an edition sees all matches grouped by round in chronological order, all sections expanded by default, with two-line score display for AET/penalty matches.

**Independent Test**: Run the app, open History tab, select 2022 — progression panel appears below summary badges; every round from Matchday 1 to Final is visible expanded; Argentina's Final entry shows `3–3` on line 1 and `(AET, 4–2 pens)` smaller below.

### Tests ⚠️ Write FIRST — must FAIL before implementation

- [X] T005 [P] [US1] Write failing tests for `get_team_progression(df, year=2022, team=None)`: assert all rounds present, correct sort order, all matches included in `tests/unit/test_tournament_progression.py`
- [X] T006 [P] [US1] Write failing tests for `get_team_progression(df, year=2022, team=None)` edge cases: blank stage defaults to `"Unknown Stage"`, edition with no data returns empty rounds list

### Implementation

- [X] T007 [US1] Implement `get_team_progression()` function body in `src/features/tournament/services.py` (TDD green — T005/T006 must pass)
- [X] T008 [P] [US1] Implement `_format_score(match: MatchRow) -> tuple[str, str | None]` helper in `src/features/tournament/views/tournament_view.py` — returns `("3–3", "(AET, 4–2 pens)")` or `("2–0", None)`
- [X] T009 [P] [US1] Implement `_build_match_tile(match: MatchRow) -> ft.Control` in `src/features/tournament/views/tournament_view.py` — two-line layout: score line 1, qualifier line 2 in `TEXT_SECONDARY` smaller font
- [X] T010 [US1] Implement `_build_progression_panel(progression: TeamProgression) -> ft.Column` in `src/features/tournament/views/tournament_view.py` — `ft.ExpansionTile` per round, `initially_expanded=True`, lists match tiles inside
- [X] T011 [US1] Integrate progression panel into `build_tournament_view()` in `src/features/tournament/views/tournament_view.py`: call `get_team_progression(store.matches, year)` on initial render; append panel below summary badges in `detail_col`

**Checkpoint**: US1 fully functional. History tab shows complete round-by-round tournament progression for any selected edition. No team filter yet.

---

## Phase 4: User Story 2 — Filter Progression by Team (Priority: P2)

**Goal**: User selects a team from a dropdown; progression panel instantly shows only that team's matches. Clearing filter restores all-teams view.

**Independent Test**: Select 2022, choose Argentina — only Argentina's 7 matches shown across their rounds. Select "All Teams" — all 64 matches visible again in round groups.

### Tests ⚠️ Write FIRST — must FAIL before implementation

- [X] T012 [P] [US2] Write failing tests for `get_team_progression(df, year=2022, team="Argentina")`: assert only Argentina matches, rounds ordered correctly, no rounds for teams not matching filter in `tests/unit/test_tournament_progression.py`
- [X] T013 [P] [US2] Write failing test: `get_team_progression(df, year=2022, team="Nonexistent FC")` returns `TeamProgression` with empty `rounds` list

### Implementation

- [X] T014 [US2] Add teams-for-year helper `_teams_for_year(matches_df, year) -> list[str]` in `src/features/tournament/services.py`
- [X] T015 [US2] Add team filter `styled_dropdown` ("All Teams" default) below year selector in `build_tournament_view()` in `src/features/tournament/views/tournament_view.py`; populate with `_teams_for_year(store.matches, year)`
- [X] T016 [US2] Wire team filter `on_change` to re-call `get_team_progression(store.matches, year, team)` and re-render progression panel without page reload in `src/features/tournament/views/tournament_view.py`

**Checkpoint**: US2 fully functional. Team filter works independently from edition selector.

---

## Phase 5: User Story 3 — Compare Team Progressions Across Editions (Priority: P3)

**Goal**: When team filter is active and edition changes, progression panel refreshes for new edition; if team didn't play that year a clear message shows.

**Independent Test**: Select Germany, switch from 2014 to 2018 — panel updates to Germany's 3 group-stage matches with a "eliminated in group stage" result visible.

### Tests ⚠️ Write FIRST — must FAIL before implementation

- [X] T017 [P] [US3] Write failing test: `get_team_progression(df, year=1934, team="Germany")` returns appropriate result (Germany did not participate in 1934, so empty rounds) in `tests/unit/test_tournament_progression.py`

### Implementation

- [X] T018 [US3] Update `_on_year_change` handler in `src/features/tournament/views/tournament_view.py` to pass current team filter value (not just `None`) to `get_team_progression` and refresh team dropdown options for new year
- [X] T019 [US3] Add "did not participate" empty-state message to `_build_progression_panel()`: when `progression.rounds` is empty and `progression.team` is not `None`, render `ft.Text("⚠️ {team} did not participate in this edition.", color=TEXT_SECONDARY)` in `src/features/tournament/views/tournament_view.py`

**Checkpoint**: US3 fully functional. All three user stories independently verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T020 [P] Verify SC-005 responsive layout: wrap progression panel `ft.Column` with `scroll=ft.ScrollMode.AUTO` and `expand=True` — no horizontal overflow on 360 px viewport in `src/features/tournament/views/tournament_view.py`
- [X] T021 [P] Update `src/features/tournament/views/__init__.py` to export `build_tournament_view` if not already exported
- [X] T022 Run full test suite `uv run pytest` — all tests pass, no regressions

---

## Dependencies

```
Phase 1 (T001)
    └── Phase 2 (T002, T003, T004) — parallel within phase
            ├── Phase 3 (T005–T011)
            │       └── Phase 4 (T012–T016)
            │               └── Phase 5 (T017–T019)
            │                       └── Phase 6 (T020–T022)
            └── (Phase 6 T021 independent but run last)
```

Story independence:
- **US1** (T005–T011): Can be demonstrated and tested without US2 or US3.
- **US2** (T012–T016): Requires US1 complete (panel exists to filter).
- **US3** (T017–T019): Requires US2 complete (team filter exists to persist across edition change).

---

## Parallel Execution Examples

**Phase 2 (all parallel after T001)**:
```
T002 (dataclasses) ║ T003 (round priority) ║ T004 (test fixtures)
```

**Phase 3 tests + independent helpers (after T004)**:
```
T005 (test all-teams) ║ T006 (test edge cases) 
→ T007 (implement function, depends on T005+T006)
T008 (score formatter) ║ T009 (match tile)    ← parallel with T007
→ T010 (progression panel, depends on T008+T009)
→ T011 (integrate into view, depends on T007+T010)
```

**Phase 4 tests + foundation (after Phase 3)**:
```
T012 (test team filter) ║ T013 (test nonexistent team) ║ T014 (teams helper)
→ T015+T016 (dropdown + wiring)
```

---

## Implementation Strategy

**MVP scope**: Phase 1 + Phase 2 + Phase 3 (US1 only).  
Delivers the core "see team progression" value with zero filtering — fully
demonstrable after T011.

**Increment 2**: Phase 4 (US2) — adds team filter.  
**Increment 3**: Phase 5 (US3) — adds cross-edition comparison.  
**Final**: Phase 6 — polish and regression check.

---

## Task Count Summary

| Phase | Tasks | User Story |
|-------|-------|-----------|
| Phase 1: Setup | 1 | — |
| Phase 2: Foundational | 3 | — |
| Phase 3: US1 MVP | 7 | US1 (P1) |
| Phase 4: US2 | 5 | US2 (P2) |
| Phase 5: US3 | 3 | US3 (P3) |
| Phase 6: Polish | 3 | — |
| **Total** | **22** | |
