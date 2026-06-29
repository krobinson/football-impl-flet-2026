# Tasks: Schedule — Country Flags and Venue Population

**Input**: Design documents from `specs/014-schedule-flags-venue/`  
**Prerequisites**: plan.md ✅, spec.md ✅, checklists ✅  
**Tests**: New tests required (FR-009) — written before implementation code  
**Organization**: US1 (flags, P1) then US2 (venue, P2) — both touch `match_row.py`

---

## Phase 1: Setup

- [ ] T001 [US1+US2] Add `CITY_STADIUM` reverse-lookup dict and `city_to_stadium()` helper to `src/core/venue_data.py` [P]
- [ ] T002 [US1+US2] Build module-level `_VENUE_FALLBACK` index from `data/worldcup/2026/worldcup.json` in `src/features/schedule/components/match_row.py`

---

## Phase 2: Tests (TDD — write before implementation)

**⚠️ Write tests first; confirm they fail before Phase 3**

- [ ] T003 [US1] Write unit tests for `tla_to_flag()` in `tests/unit/test_schedule_flags_venue.py`:
  - Known TLA returns correct emoji (USA → 🇺🇸, MEX → 🇲🇽, FRA → 🇫🇷)
  - Unknown TLA returns `""`
  - None / empty string returns `""`
  - All 48 2026 nations have a non-empty mapping
- [ ] T004 [US2] Write unit tests for `_resolve_venue()` in `tests/unit/test_schedule_flags_venue.py`:
  - API `venue` populated → returned as-is
  - API `venue` null, local data match found → returns stadium name
  - API `venue` null, no local match → returns `"TBD"`
  - `city_to_stadium()` maps all 16 host cities to a stadium name
- [ ] T005 [US1] Write unit test: rendered team name text includes flag prefix when TLA is known
- [ ] T006 [US2] Write unit test: rendered venue text matches resolved venue

---

## Phase 3: Implementation

- [ ] T007 [US1] Add `_TLA_FLAG: dict[str, str]` and `tla_to_flag(tla: str) -> str` to `src/features/schedule/components/match_row.py`
- [ ] T008 [US2] Add `_resolve_venue(match: dict) -> str` to `src/features/schedule/components/match_row.py` using `_VENUE_FALLBACK` index and `city_to_stadium()`
- [ ] T009 [US1+US2] Update `match_row()` in `src/features/schedule/components/match_row.py` to:
  - Prepend `tla_to_flag(tla) + " "` to home and away team display strings (only when flag non-empty)
  - Replace `venue_name = match.get("venue") or "TBD"` with `venue_name = _resolve_venue(match)`

---

## Phase 4: Regression Verification

- [ ] T010 Run `uv run pytest tests/ -q` — confirm all tests pass (143 existing + new tests)

---

## Dependencies

```
T001 ──┐
T002 ──┼──► T007 ──► T009 ──► T010
T003 ──┘    T008 ──►           ▲
T004 ────────────────────────►─┘
T005 ────────────────────────►─┘
T006 ────────────────────────►─┘
```

T001 and T002 are setup; T003–T006 are TDD tests (write first); T007–T009 are implementation; T010 is regression gate.
