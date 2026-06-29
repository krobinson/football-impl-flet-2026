# Implementation Plan: Group Stage Match Details via URL Data Source

**Branch**: `016-group-stage-match-details` | **Date**: 2026-06-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/016-group-stage-match-details/spec.md`

## Summary

Load and display all 48 group stage matches from the openfootball worldcup.json public URL, eliminating the API key dependency for the Schedule tab. The system fetches from the URL at startup, normalizes the data into the existing match dict shape, and falls back to the locally bundled `data/worldcup/2026/worldcup.json` on failure. Existing group chip filtering and match row rendering are reused with minimal changes.

## Technical Context

**Language/Version**: Python >= 3.10  
**Primary Dependencies**: Flet >= 0.84, FastAPI >= 0.136 (web mode)  
**Storage**: Local JSON file fallback (`data/worldcup/2026/worldcup.json`)  
**Testing**: pytest  
**Target Platform**: Desktop (Linux, macOS, Windows), Web, Android, iOS  
**Project Type**: Desktop/web/mobile app (Flet)  
**Performance Goals**: 48 matches load within 3 seconds; group filter renders in < 0.5 s  
**Constraints**: No API key required; offline fallback via local file  
**Scale/Scope**: 48 group stage matches, 12 groups (A-L), 6 matches per group

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Flet-First UI | PASS | All UI uses Flet controls (ft.Container, ft.Row, ft.Text). No alternative frameworks. |
| II. Feature-Module Separation | PASS | New service lives in `src/features/schedule/services/`. No cross-feature imports. Shared URL fetching utility goes in `src/core/`. |
| III. Test-First | PASS | Tests written before implementation. Unit tests for data parsing/transformation; integration test for URL fetch with mock. |
| IV. API-Backed Data Layer | PASS | URL data accessed through a service layer (`WorldCupJsonService`). UI never calls URL directly. |
| V. Simplicity & YAGNI | PASS | Reuse existing group chips, match row, and colour palette. Transform URL data to match existing dict shape rather than creating a parallel rendering path. |

**Gate result**: All principles pass. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/016-group-stage-match-details/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── worldcup-json-service.md
└── tasks.md             # Phase 2 output (by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── app.py                                    # Wires schedule view (unchanged)
├── core/
│   ├── config.py                             # Add WORLDCUP_JSON_URL constant
│   ├── network.py                            # Existing FootballDataClient (unchanged)
│   ├── venue_data.py                         # Existing venue lookups (unchanged)
│   └── ui_helpers.py                         # Shared UI helpers (unchanged)
├── features/
│   └── schedule/
│       ├── services/
│       │   ├── __init__.py
│       │   └── worldcup_json_service.py      # NEW: URL fetch + local fallback + transform
│       ├── components/
│       │   ├── __init__.py
│       │   ├── match_row.py                  # MODIFY: handle URL data format fields
│       │   └── header_row.py                 # MODIFY: adapt column headers for URL data
│       └── views/
│           ├── __init__.py
│           └── schedule_view.py              # MODIFY: use WorldCupJsonService as primary data source
└── main.py

tests/
├── unit/
│   └── test_worldcup_json_service.py         # NEW: parsing, transform, fallback logic
└── integration/
    └── test_schedule_url_data.py             # NEW: end-to-end schedule loading
```

**Structure Decision**: Single project structure (existing). New service module added under `src/features/schedule/services/` following the existing feature-module separation pattern. No new top-level directories.

## Implementation Approach

### Data Source Strategy

The openfootball worldcup.json URL provides data in a different format than the football-data.org API:

| Field | URL format | API format |
|-------|-----------|------------|
| Home team | `team1` (string) | `homeTeam.name` |
| Away team | `team2` (string) | `awayTeam.name` |
| Date | `date` ("2026-06-11") | `utcDate` (ISO-8601) |
| Time | `time` ("13:00 UTC-6") | `utcDate` (ISO-8601) |
| Group | `group` ("Group A") | `group` ("GROUP_A") |
| Venue | `ground` ("Mexico City") | `venue` ("MetLife Stadium") |
| Round | `round` ("Matchday 1") | `matchday` (int) |
| Score | not present | `score.fullTime.home/away` |
| Status | not present | `status` ("SCHEDULED") |
| Team TLA | not present | `homeTeam.tla`, `awayTeam.tla` |

### Transformation Layer

A `transform_match()` function normalizes URL data dicts into the shape the existing `match_row()` expects, mapping:
- `team1` → `homeTeam.name` (no TLA available, so flag emoji omitted)
- `team2` → `awayTeam.name`
- `date` + `time` → `utcDate` (synthesized ISO-8601 string)
- `group` → `group` (converted from "Group A" to "GROUP_A")
- `ground` → `venue` (used directly as display string)
- `round` → `matchday` (extracted numeric suffix)
- status → hardcoded "SCHEDULED"
- score → omitted (shows "vs")

### View Layer Changes

The `build_schedule_view()` function is modified to:
1. Accept an optional `WorldCupJsonService` instead of (or alongside) `FootballDataClient`
2. Load data from the URL service first, falling back to local file
3. Display a data source notice ("Loaded from openfootball data")
4. Reuse existing group chip filtering logic with adapted group key format

### Fallback Chain

1. Fetch from URL → success: use data
2. URL fails → load from `data/worldcup/2026/worldcup.json` local file
3. Local file fails → show error message
