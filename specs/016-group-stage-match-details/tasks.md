# Tasks: Group Stage Match Details via URL Data Source

**Input**: Design documents from `/specs/016-group-stage-match-details/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in feature specification. Test tasks omitted per task generation rules.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration

- [x] T001 Add WORLDCUP_JSON_URL constant to src/core/config.py
- [x] T002 Create src/features/schedule/services/ directory with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data service infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create WorldCupDataError exception class in src/features/schedule/services/worldcup_json_service.py
- [x] T004 Implement transform_match() function in src/features/schedule/services/worldcup_json_service.py
- [x] T005 Implement is_group_stage() filter function in src/features/schedule/services/worldcup_json_service.py
- [x] T006 Implement WorldCupJsonService class with get_group_matches() method in src/features/schedule/services/worldcup_json_service.py
- [x] T007 Implement get_data_source() method in WorldCupJsonService class in src/features/schedule/services/worldcup_json_service.py

**Checkpoint**: Foundation ready - WorldCupJsonService can fetch, transform, and filter data from URL with local fallback

---

## Phase 3: User Story 1 - View all group stage matches from URL data (Priority: P1) 🎯 MVP

**Goal**: Load and display all 48 group stage matches from the openfootball worldcup.json URL without requiring an API key

**Independent Test**: Launch the app with no API key configured. Open the Schedule tab. Verify all 48 group stage matches load from the URL and display team names, dates, times, groups, and venues.

### Implementation for User Story 1

- [x] T008 [US1] Modify build_schedule_view() signature to accept WorldCupJsonService parameter in src/features/schedule/views/schedule_view.py
- [x] T009 [US1] Implement data loading logic using WorldCupJsonService.get_group_matches() in src/features/schedule/views/schedule_view.py
- [x] T010 [US1] Add data source notice display ("Loaded from openfootball data") in src/features/schedule/views/schedule_view.py
- [x] T011 [US1] Modify match_row() to handle URL data format (no TLA codes, no score field) in src/features/schedule/components/match_row.py
- [x] T012 [US1] Update app.py to instantiate WorldCupJsonService and pass to build_schedule_view() in src/app.py

**Checkpoint**: At this point, User Story 1 should be fully functional - all 48 matches display from URL data without API key

---

## Phase 4: User Story 2 - Filter matches by group (Priority: P1)

**Goal**: Allow users to filter matches by selecting a group chip (A-L) or view all matches

**Independent Test**: Open the Schedule tab. Click "Group C". Verify exactly 6 Group C matches appear. Click "All" to verify all 48 matches return.

### Implementation for User Story 2

- [x] T013 [US2] Verify existing group chip filtering works with transformed "GROUP_A" format in src/features/schedule/views/schedule_view.py
- [x] T014 [US2] Test group filtering with URL data to ensure 6 matches per group display correctly in src/features/schedule/views/schedule_view.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - matches load from URL and filter by group

---

## Phase 5: User Story 3 - See match details with venue information (Priority: P2)

**Goal**: Display venue/city information for each match from the ground field in URL data

**Independent Test**: Select any group. Verify each match shows a venue name (city or stadium). Verify venue data matches the ground field from the worldcup.json source.

### Implementation for User Story 3

- [x] T015 [US3] Ensure venue field displays ground value correctly in match_row() in src/features/schedule/components/match_row.py
- [x] T016 [US3] Handle missing ground field by displaying "TBD" in match_row() in src/features/schedule/components/match_row.py
- [x] T017 [US3] Verify parenthetical venue details display correctly (e.g., "Guadalajara (Zapopan)") in src/features/schedule/components/match_row.py

**Checkpoint**: At this point, User Story 3 works - venue information displays for all matches

---

## Phase 6: User Story 4 - Distinguish match scheduling status (Priority: P2)

**Goal**: Display "Scheduled" status and "vs" for all URL data matches (pre-tournament fixtures)

**Independent Test**: View any group. Verify all matches show a "Scheduled" status indicator. Verify no scores are shown for unplayed matches (display "vs" instead).

### Implementation for User Story 4

- [x] T018 [US4] Verify status badge displays "Scheduled" for URL data matches in src/features/schedule/components/match_row.py
- [x] T019 [US4] Verify score area displays "vs" when score field is None in src/features/schedule/components/match_row.py
- [x] T020 [US4] Ensure date and time information displays clearly for all matches in src/features/schedule/components/match_row.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, validation, and final integration

- [x] T021 Add error handling for WorldCupDataError in schedule_view.py with user-friendly message in src/features/schedule/views/schedule_view.py
- [x] T022 Implement retry logic or fallback notice when URL fetch fails in src/features/schedule/views/schedule_view.py
- [x] T023 Verify all 48 matches display correctly with no API key configured in src/app.py
- [x] T024 Run quickstart.md validation scenarios and verify all pass
- [x] T025 Code cleanup and remove any debug logging or temporary code

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Builds on US1 data loading
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3

### Within Each User Story

- Models before services (not applicable - no new models)
- Services before views
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (none marked)
- All Foundational tasks marked [P] can run in parallel (none marked - sequential dependency)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all implementation tasks for User Story 1:
Task: "Modify build_schedule_view() signature to accept WorldCupJsonService parameter"
Task: "Implement data loading logic using WorldCupJsonService.get_group_matches()"
Task: "Add data source notice display"
Task: "Modify match_row() to handle URL data format"
Task: "Update app.py to instantiate WorldCupJsonService"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T007) - CRITICAL
3. Complete Phase 3: User Story 1 (T008-T012)
4. **STOP and VALIDATE**: Test User Story 1 independently (48 matches load without API key)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (service can fetch/transform data)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - matches display)
3. Add User Story 2 → Test independently → Deploy/Demo (group filtering works)
4. Add User Story 3 → Test independently → Deploy/Demo (venue info displays)
5. Add User Story 4 → Test independently → Deploy/Demo (status indicators work)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (data loading + display)
   - Developer B: User Story 2 (group filtering)
   - Developer C: User Stories 3 + 4 (venue + status - smaller scope)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Task Summary

- **Total tasks**: 25
- **Setup**: 2 tasks
- **Foundational**: 5 tasks
- **User Story 1**: 5 tasks
- **User Story 2**: 2 tasks
- **User Story 3**: 3 tasks
- **User Story 4**: 3 tasks
- **Polish**: 5 tasks

## Suggested MVP Scope

**MVP = User Story 1 only** (Phases 1-3, tasks T001-T012)

This delivers: All 48 group stage matches load from URL and display without API key requirement.
