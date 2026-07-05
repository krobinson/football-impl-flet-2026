# Contract: WorldCupJsonService (Extended)

**Feature**: 017-knockout-stage-results  
**Date**: 2026-07-04

---

## Overview

`WorldCupJsonService` is extended to return all 104 tournament matches (group stage + knockout) with scores and stage classification. This contract documents the changes from the feature 016 contract.

---

## Class: `WorldCupJsonService`

**Module**: `src/features/schedule/services/worldcup_json_service.py`

### New Public Method

#### `get_all_matches() -> list[dict]`

Fetches all tournament matches (group stage + knockout), transforms them to the normalized dict shape, and returns them sorted by date then time.

**Returns**: `list[dict]` — 104 match dicts. Each dict includes the new `stage` and `round_display` fields.

**Raises**:
- `WorldCupDataError` — if both URL fetch and local file fallback fail.

**Data source priority**: Same as `get_group_matches()` — URL first, local file fallback.

**Difference from `get_group_matches()`**: Does not filter to group stage only. Includes all knockout matches.

---

### Existing Method (unchanged)

#### `get_group_matches() -> list[dict]`

Retained for backward compatibility. Returns only group stage matches (72 matches).

---

## New Transformation Functions

### `classify_stage(raw: dict) -> str`

Returns the tournament stage classification for a match.

**Input**: Raw match dict from worldcup.json.

**Output**: One of `"GROUP_STAGE"`, `"ROUND_OF_32"`, `"ROUND_OF_16"`, `"QUARTER_FINAL"`, `"SEMI_FINAL"`, `"FINAL"`, `"UNKNOWN"`.

**Rules**:
- If `group` field matches "Group [A-L]" → `"GROUP_STAGE"`
- If `round` is "Round of 32" → `"ROUND_OF_32"`
- If `round` is "Round of 16" → `"ROUND_OF_16"`
- If `round` is "Quarter-final" → `"QUARTER_FINAL"`
- If `round` is "Semi-final" → `"SEMI_FINAL"`
- If `round` is "Final" or "Match for third place" → `"FINAL"`

---

### `round_display_label(raw: dict) -> str`

Returns a short display label for knockout rounds.

**Input**: Raw match dict from worldcup.json.

**Output**: Short label string, or empty string for group stage matches.

**Mapping**:
- Group stage → `""`
- Round of 32 → `"R32"`
- Round of 16 → `"R16"`
- Quarter-final → `"QF"`
- Semi-final → `"SF"`
- Final → `"F"`
- Match for third place → `"3rd"`

---

## Extended Transformed Match Dict

The `transform_match()` function now includes two additional fields:

```python
{
    "utcDate": "2026-06-28T19:00:00Z",
    "status": "FINISHED",
    "matchday": 99,
    "group": "",
    "venue": "Los Angeles (Inglewood)",
    "homeTeam": {"name": "South Africa", "tla": None},
    "awayTeam": {"name": "Canada", "tla": None},
    "score": {"fullTime": {"home": 0, "away": 1}},
    "stage": "ROUND_OF_32",        # NEW
    "round_display": "R32",         # NEW
}
```

---

## Stage Chip Component

### `build_stage_chips(active_stage: str, on_select) -> ft.Row`

**Module**: `src/features/schedule/components/stage_chips.py`

Returns a row of stage selector chips.

**Parameters**:
- `active_stage`: Currently selected stage value (e.g., `"ALL"`, `"GROUP_STAGE"`)
- `on_select`: Callback function receiving the selected stage value string

**Chip labels and values**:

| Label | Value |
|-------|-------|
| All | `"ALL"` |
| Group Stage | `"GROUP_STAGE"` |
| R32 | `"ROUND_OF_32"` |
| R16 | `"ROUND_OF_16"` |
| QF | `"QUARTER_FINAL"` |
| SF | `"SEMI_FINAL"` |
| Final | `"FINAL"` |

**Styling**: Reuses the same chip pattern as group chips (rounded container, active/inactive colours from schedule_view.py).

---

## Usage Example

```python
from features.schedule.services.worldcup_json_service import WorldCupJsonService

service = WorldCupJsonService()
matches = service.get_all_matches()  # 104 matches
source = service.get_data_source()   # "url" or "local"

# Filter by stage
knockout = [m for m in matches if m["stage"] != "GROUP_STAGE"]
quarter_finals = [m for m in matches if m["stage"] == "QUARTER_FINAL"]
```
