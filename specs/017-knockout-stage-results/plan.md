# Implementation Plan: Knockout Stage Results & Live Scores

**Branch**: `017-knockout-stage-results` | **Date**: 2026-07-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-knockout-stage-results/spec.md`

## Summary

Display actual scores for all completed group stage matches and add knockout stage matches (Round of 32, Round of 16, Quarter-final, Semi-final, Final, third-place match) to the Schedule tab. The existing `WorldCupJsonService` already transforms scores correctly; the primary changes are removing the group-stage-only filter, adding a `stage` field to transformed data, introducing stage selector chips, and adapting the match row to show round names for knockout matches.

## Technical Context

**Language/Version**: Python >= 3.10  
**Primary Dependencies**: Flet >= 0.84, FastAPI >= 0.136 (web mode)  
**Storage**: Local JSON file fallback (`data/worldcup/2026/worldcup.json`)  
**Testing**: pytest  
**Target Platform**: Desktop (Linux, macOS, Windows), Web, Android, iOS  
**Project Type**: Desktop/web/mobile app (Flet)  
**Performance Goals**: 104 matches load within 3 seconds; stage filter renders in < 0.5 s  
**Constraints**: No API key required; offline fallback via local file  
**Scale/Scope**: 104 total matches (72 group stage + 32 knockout), 6 tournament stages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Flet-First UI | PASS | All UI uses Flet controls (ft.Container, ft.Row, ft.Text). Stage chips reuse existing chip pattern. No alternative frameworks. |
| II. Feature-Module Separation | PASS | Changes are within `src/features/schedule/`. No cross-feature imports. |
| III. Test-First | PASS | Tests written before implementation for score display, knockout rendering, and stage filtering. |
| IV. API-Backed Data Layer | PASS | Data accessed through `WorldCupJsonService`. UI never calls URL directly. |
| V. Simplicity & YAGNI | PASS | Reuse existing match_row, header_row, chip pattern, and score transformation. Minimal new code. |

**Gate result**: All principles pass. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/017-knockout-stage-results/
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
├── core/
│   ├── config.py                             # Unchanged
│   └── ...
├── features/
│   └── schedule/
│       ├── services/
│       │   └── worldcup_json_service.py      # MODIFY: remove group-only filter, add stage field, include knockout matches
│       ├── components/
│       │   ├── match_row.py                  # MODIFY: show round name for knockout matches in Group column
│       │   └── stage_chips.py                # NEW: stage selector chip row component
│       └── views/
│           └── schedule_view.py              # MODIFY: add stage chips, conditional group chips, stage filtering

tests/
├── unit/
│   ├── test_match_row_columns.py             # MODIFY: add knockout row tests
│   ├── test_worldcup_json_service.py         # MODIFY: add knockout + score tests
│   └── test_stage_chips.py                   # NEW: stage chip filtering tests
└── integration/
    └── test_schedule_url_data.py             # MODIFY: end-to-end with knockout matches
```

**Structure Decision**: Single project structure (existing). One new component file (`stage_chips.py`) added under `src/features/schedule/components/`. All other changes are modifications to existing files.

## Implementation Approach

### Data Source Changes

The `WorldCupJsonService.get_group_matches()` method is renamed/extended to `get_all_matches()`:

1. **Remove group-only filter**: The `is_group_stage()` filter is removed from the main pipeline so knockout matches are included.
2. **Add `stage` field**: `transform_match()` adds a `stage` field derived from the `round` or `group` field:
   - Group stage matches → `"GROUP_STAGE"`
   - Round of 32 → `"ROUND_OF_32"`
   - Round of 16 → `"ROUND_OF_16"`
   - Quarter-final → `"QUARTER_FINAL"`
   - Semi-final → `"SEMI_FINAL"`
   - Final / Match for third place → `"FINAL"`
3. **Add `round_display` field**: Human-readable round name for knockout matches (e.g., "Round of 32", "Quarter-final").
4. **Score transformation**: Already works — `score.ft` → `score.fullTime` handles both group and knockout scores.

### View Layer Changes

The `build_schedule_view()` function is modified to:

1. Add a stage chip row above the existing group chips
2. Conditionally show/hide group chips based on active stage (visible only when "Group Stage" is selected)
3. Filter matches by stage when a stage chip is selected
4. Pass all 104 matches (not just group stage) to the rendering pipeline

### Match Row Changes

The `match_row()` function is modified to:

1. For knockout matches (no group field), display the round name (e.g., "R32", "QF", "SF", "F") in the Group column instead of "Grp X"
2. Score and status display already work correctly for finished matches

### Fallback Chain

Unchanged: URL → local file → error. The local file must be updated to include current scores.
