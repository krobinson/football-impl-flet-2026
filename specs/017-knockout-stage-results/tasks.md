# Tasks: Knockout Stage Results & Live Scores

**Input**: Design documents from `/specs/017-knockout-stage-results/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as the constitution requires TDD (Test-First principle).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup required — project structure already exists from feature 016.

No tasks needed for this phase.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend WorldCupJsonService to return all matches with stage classification. These changes are required before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 Implement `classify_stage()` function in src/features/schedule/services/worldcup_json_service.py
- [x] T002 Implement `round_display_label()` function in src/features/schedule/services/worldcup_json_service.py
- [x] T003 Add `stage` and `round_display` fields to `transform_match()` output in src/features/schedule/services/worldcup_json_service.py
- [x] T004 Implement `get_all_matches()` method (returns all 104 matches without group filter) in src/features/schedule/services/worldcup_json_service.py
- [x] T005 [P] Write unit tests for `classify_stage()` in tests/unit/test_worldcup_json_service.py
- [x] T006 [P] Write unit tests for `round_display_label()` in tests/unit/test_worldcup_json_service.py
- [x] T007 [P] Write unit tests for `get_all_matches()` returning 104 matches in tests/unit/test_worldcup_json_service.py
- [x] T008 Update local fallback file data/worldcup/2026/worldcup.json with current scores from URL

**Checkpoint**: Foundation ready - WorldCupJsonService returns all matches with stage classification

---

## Phase 3: User Story 1 - View Group Stage Match Scores (Priority: P1) 🎯 MVP

**Goal**: Display actual scores for all completed group stage matches. Matches with scores show "X–Y" format and "FT" status badge.

**Independent Test**: Open Schedule tab, select "Group Stage". Verify completed matches show scores (e.g., "2–0") in Score column and "FT" status badge. Unplayed matches show "vs" and "Scheduled".

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Unit test: group stage match with score displays "X–Y" in Score column in tests/unit/test_match_row_columns.py
- [x] T010 [P] [US1] Unit test: group stage match with score shows "FT" status badge in tests/unit/test_match_row_columns.py
- [x] T011 [P] [US1] Unit test: group stage match without score shows "vs" and "Scheduled" in tests/unit/test_match_row_columns.py

### Implementation for User Story 1

- [x] T012 [US1] Verify existing `_score_text()` and status badge logic in src/features/schedule/components/match_row.py handles scores correctly (no changes expected — existing logic should work)
- [x] T013 [US1] Verify `transform_match()` correctly converts `score.ft` to `score.fullTime` format for group stage matches in src/features/schedule/services/worldcup_json_service.py

**Checkpoint**: Group stage matches display actual scores. This is the MVP — can stop here and deliver value.

---

## Phase 4: User Story 2 - View Knockout Stage Matches (Priority: P1)

**Goal**: Display all knockout stage matches (Round of 32, Round of 16, Quarter-final, Semi-final, Final, third-place match) with scores for completed matches. Knockout matches show round name in Group column.

**Independent Test**: Open Schedule tab. Verify knockout matches are visible. Completed knockout matches show scores. Round names (R32, R16, QF, SF, F, 3rd) appear in Group column instead of group letters.

### Tests for User Story 2 ⚠️

- [x] T014 [P] [US2] Unit test: knockout match displays round label (e.g., "R32") in Group column in tests/unit/test_match_row_columns.py
- [x] T015 [P] [US2] Unit test: knockout match with score displays score and "FT" status in tests/unit/test_match_row_columns.py
- [x] T016 [P] [US2] Unit test: knockout match without score shows "vs" and "Scheduled" in tests/unit/test_match_row_columns.py
- [x] T017 [P] [US2] Unit test: knockout match with placeholder team names (e.g., "1A") displays placeholder text in tests/unit/test_match_row_columns.py

### Implementation for User Story 2

- [x] T018 [US2] Modify `match_row()` to display `round_display` in Group column when `group` is empty (knockout matches) in src/features/schedule/components/match_row.py
- [x] T019 [US2] Modify `build_schedule_view()` to call `get_all_matches()` instead of `get_group_matches()` in src/features/schedule/views/schedule_view.py
- [x] T020 [US2] Update notice message to show "104 matches loaded" instead of "48 matches loaded" in src/features/schedule/views/schedule_view.py

**Checkpoint**: All 104 matches (group + knockout) display with correct scores and round labels.

---

## Phase 5: User Story 3 - Filter Matches by Tournament Stage (Priority: P2)

**Goal**: Add stage selector chips to filter matches by tournament stage. Group chips visible only when "Group Stage" is selected.

**Independent Test**: Open Schedule tab. Click "R32" chip — verify only Round of 32 matches display. Click "Group Stage" — verify group chips (A–L) appear. Click "All" — verify all 104 matches display and group chips hide.

### Tests for User Story 3 ⚠️

- [x] T021 [P] [US3] Unit test: `build_stage_chips()` returns 7 chips with correct labels in tests/unit/test_stage_chips.py
- [x] T022 [P] [US3] Unit test: stage chip selection updates active state correctly in tests/unit/test_stage_chips.py
- [x] T023 [P] [US3] Unit test: filtering by stage returns correct match count (e.g., R32 = 16 matches) in tests/unit/test_schedule_stage_filter.py
- [x] T024 [P] [US3] Unit test: group chips visible only when "Group Stage" stage is active in tests/unit/test_schedule_stage_filter.py

### Implementation for User Story 3

- [x] T025 [US3] Create `build_stage_chips()` function in src/features/schedule/components/stage_chips.py
- [x] T026 [US3] Add stage chips row to `build_schedule_view()` above group chips in src/features/schedule/views/schedule_view.py
- [x] T027 [US3] Implement `_apply_stage_filter()` function to filter matches by stage in src/features/schedule/views/schedule_view.py
- [x] T028 [US3] Implement conditional visibility: hide group chips when stage is not "GROUP_STAGE" in src/features/schedule/views/schedule_view.py
- [x] T029 [US3] Update `_state` dict to include `active_stage` field with default "ALL" in src/features/schedule/views/schedule_view.py
- [x] T030 [US3] Wire stage chip selection to filter matches and update group chip visibility in src/features/schedule/views/schedule_view.py

**Checkpoint**: Stage filtering works. Users can navigate between group and knockout stages.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, testing, and cleanup

- [x] T031 Run all unit tests to verify no regressions: `uv run pytest tests/unit/ -v`
- [x] T032 Run integration tests: `uv run pytest tests/integration/ -v`
- [x] T033 Run quickstart.md manual acceptance tests (all 5 tests)
- [x] T034 [P] Verify responsive behavior on narrow viewports (360px) with stage chips visible
- [x] T035 Code review: ensure no cross-feature imports, all UI uses Flet controls
- [x] T036 Update AGENTS.md if any new patterns or conventions introduced

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Story 1 (Phase 3)**: Depends on Foundational — verifies score display works
- **User Story 2 (Phase 4)**: Depends on Foundational — adds knockout matches
- **User Story 3 (Phase 5)**: Depends on User Story 2 — needs all matches loaded first
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — independent verification of score display
- **User Story 2 (P1)**: Can start after Foundational — adds knockout matches (may run parallel with US1)
- **User Story 3 (P2)**: Depends on US2 — needs all 104 matches loaded before filtering makes sense

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service layer before UI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T005, T006, T007 (foundational tests) can run in parallel
- T009, T010, T011 (US1 tests) can run in parallel
- T014, T015, T016, T017 (US2 tests) can run in parallel
- T021, T022, T023, T024 (US3 tests) can run in parallel
- US1 and US2 can run in parallel after Foundational (different concerns)

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Unit test: knockout match displays round label in tests/unit/test_match_row_columns.py"
Task: "Unit test: knockout match with score displays score in tests/unit/test_match_row_columns.py"
Task: "Unit test: knockout match without score shows vs in tests/unit/test_match_row_columns.py"
Task: "Unit test: knockout match with placeholder team names in tests/unit/test_match_row_columns.py"

# Then implement:
Task: "Modify match_row() to display round_display in Group column in src/features/schedule/components/match_row.py"
Task: "Modify build_schedule_view() to call get_all_matches() in src/features/schedule/views/schedule_view.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (extend service to return all matches)
2. Complete Phase 3: User Story 1 (verify score display works)
3. **STOP and VALIDATE**: Test that group stage scores display correctly
4. Deploy/demo if ready — users see actual scores for group matches

### Incremental Delivery

1. Complete Foundational → Service returns all 104 matches with stage classification
2. Add User Story 1 → Verify scores display → Test independently (MVP!)
3. Add User Story 2 → Knockout matches visible → Test independently
4. Add User Story 3 → Stage filtering works → Test independently
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (verify scores)
   - Developer B: User Story 2 (add knockout matches)
3. After US2 complete:
   - Developer A or B: User Story 3 (stage filtering)
4. Stories integrate cleanly

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution requires TDD — tests written before implementation
- US1 is mostly verification — score display logic already exists from feature 016
- US2 requires match_row.py changes to show round names for knockout matches
- US3 requires new stage_chips.py component and schedule_view.py modifications
- Local data file update (T008) can happen anytime after Foundational
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
