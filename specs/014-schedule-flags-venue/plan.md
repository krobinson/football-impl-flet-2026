# Implementation Plan: Schedule — Country Flags and Venue Population

**Branch**: `014-schedule-flags-venue` | **Date**: 2026-06-10 | **Spec**: [specs/014-schedule-flags-venue/spec.md](spec.md)

## Summary

Two visual improvements to the match schedule row:
1. **Flags** — prepend a Unicode flag emoji to each team name using a TLA → emoji lookup.
2. **Venue** — always show a stadium name by falling back to the local 2026 fixture JSON when the API `venue` field is null.

All logic lives in `src/features/schedule/components/match_row.py`. A reverse city→stadium map is added to `src/core/venue_data.py`. New unit tests are added in `tests/unit/test_schedule_flags_venue.py`.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Flet >= 0.84
**Storage**: `data/worldcup/2026/worldcup.json` (read-only; loaded once at module level)
**Testing**: pytest (143 existing + new tests)
**Target Platform**: Desktop + Web
**Project Type**: Desktop/web app
**Performance Goals**: Module-level index load — O(1) per lookup
**Constraints**: No new dependencies; no changes outside 3 files

## Constitution Check

| Gate | Principle | Status | Notes |
|------|-----------|--------|-------|
| UI uses Flet only | I. Flet-First UI | ✅ PASS | Emoji in ft.Text — no new frameworks |
| Feature module separation | II. Feature-Module Separation | ✅ PASS | schedule owns flags; core owns venue helpers |
| TDD cycle | III. Test-First | ✅ PASS | Tests written before implementation code |
| Data through service layer | IV. API-Backed Data Layer | ✅ PASS | Local fixture fallback via helper, not direct UI call |
| Simplicity / YAGNI | V. Simplicity & YAGNI | ✅ PASS | Static dict + index; no abstraction layers |

## Project Structure

### Documentation

```text
specs/014-schedule-flags-venue/
├── plan.md
├── spec.md
├── research.md          # (inline below)
├── checklists/requirements.md
└── tasks.md
```

### Source Code

```text
src/core/venue_data.py                                ← add CITY_STADIUM + city_to_stadium()
src/features/schedule/components/match_row.py         ← add _TLA_FLAG, tla_to_flag(), _resolve_venue(), update match_row()
tests/unit/test_schedule_flags_venue.py               ← new test file
```

## Research Decisions

1. **Flag source**: Unicode Regional Indicator emoji from TLA via a static hand-curated dict. All 48 nations + common edge codes. No external library.
2. **TLA field**: `homeTeam.tla` / `awayTeam.tla` from football-data.org API. If null/missing, flag omitted silently.
3. **Venue primary**: `match["venue"]` from API — use as-is when non-null.
4. **Venue fallback index**: Built once at import time from `data/worldcup/2026/worldcup.json`. Key = `(normalise(team1), matchday_int)` → city. Then city → stadium via `city_to_stadium()`.
5. **City → stadium**: Reverse of `VENUE_CITY` (stadium → city) in `venue_data.py`. Added as `CITY_STADIUM` dict + `city_to_stadium()` helper with substring fallback.

## Complexity Tracking

No violations.
