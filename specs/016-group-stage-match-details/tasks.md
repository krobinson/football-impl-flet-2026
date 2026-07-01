# Tasks: Group Stage Match Details — Split Match Column

**Input**: Design documents from `/specs/016-group-stage-match-details/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as specified in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No additional setup required — the project structure already exists with the WorldCupJsonService, match_row component, and schedule_view in place.

No tasks needed for this phase.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Understand the current match row structure and identify all places where the combined "Match" column is rendered.

**⚠️ CRITICAL**: This phase must be complete before modifying the UI.

- [x] T001 Review current match_row layout in src/features/schedule/components/match_row.py to understand the combined "Match" column structure (line 200-239)
- [x] T002 Review current header_row layout in src/features/schedule/components/match_row.py to understand the "Match" header (line 260-285)
- [x] T003 Identify column width constraints and responsive behavior for the schedule table

**Checkpoint**: Foundation ready — understanding of current structure is complete.

---

## Phase 3: User Story 1 — Split Match Column into Home Team, Away Team, and Score (Priority: P1) 🎯 MVP

**Goal**: Replace the single combined "Match" column (showing "Home Team vs Away Team") with three separate columns: Home Team, Away Team, and Score. This improves readability and makes it easier to scan team names and scores independently.

**Independent Test**: Open the Schedule tab. Verify each match row displays three separate columns: Home Team (showing home team name with flag if available), Away Team (showing away team name with flag if available), and Score (showing "vs" for scheduled matches or "X–Y" for finished matches). The header row should show "Home", "Away", and "Score" labels.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US1] Unit test for match_row rendering with separate home team, away team, and score columns in tests/unit/test_match_row_columns.py
- [x] T005 [P] [US1] Unit test for header_row rendering with "Home", "Away", "Score" headers in tests/unit/test_match_row_columns.py

### Implementation for User Story 1

- [x] T006 [US1] Modify match_row() function in src/features/schedule/components/match_row.py to replace the combined "Match" column (line 200-239) with three separate columns:
  - Home Team column (width ~150px, showing flag + home team name)
  - Away Team column (width ~150px, showing flag + away team name)
  - Score column (width ~60px, showing "vs" or "X–Y" score)
- [x] T007 [US1] Modify header_row() function in src/features/schedule/components/match_row.py to replace the "Match" header (line 276) with three separate headers: "Home" (width ~150px), "Away" (width ~150px), "Score" (width ~60px)
- [x] T008 [US1] Adjust column widths to ensure the table remains usable on viewports from 360px to 1920px without horizontal scrolling (per SC-006)
- [x] T009 [US1] Verify score display handles both scheduled matches ("vs") and finished matches ("X–Y") correctly in the new Score column

**Checkpoint**: At this point, the match row displays three separate columns for Home Team, Away Team, and Score. The table is readable and functional.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T010 Run unit tests to verify match_row and header_row render correctly with the new column structure
- [x] T011 Run quickstart.md manual acceptance tests to verify the UI displays correctly in the app
- [x] T012 Verify responsive behavior on narrow viewports (360px width) — ensure columns don't overflow or truncate excessively
- [x] T013 Code cleanup: remove the old `match_text` variable and any unused formatting logic from match_row.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation before validation
- Story complete before moving to polish

### Parallel Opportunities

- T004 and T005 (tests) can run in parallel
- T006 and T007 (implementation) can run in parallel after tests are written

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for match_row rendering with separate columns in tests/unit/test_match_row_columns.py"
Task: "Unit test for header_row rendering with separate headers in tests/unit/test_match_row_columns.py"

# Launch implementation tasks together:
Task: "Modify match_row() function in src/features/schedule/components/match_row.py"
Task: "Modify header_row() function in src/features/schedule/components/match_row.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (review current structure)
2. Complete Phase 3: User Story 1 (split columns)
3. **STOP and VALIDATE**: Test the new column layout independently
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Foundational → Understanding ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Polish → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- The change is localized to match_row.py — no service layer or data model changes required
- Column widths are approximate and may need adjustment based on visual testing
- Flag emojis (from tla_to_flag) should continue to display in the Home and Away columns when TLA codes are available
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
