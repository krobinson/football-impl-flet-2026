# Data Model: Group Stage Match Details via URL Data Source

**Feature**: 016-group-stage-match-details  
**Date**: 2026-06-28

---

## Source Data Format (openfootball worldcup.json)

The URL returns a JSON object with this structure:

```json
{
  "name": "World Cup 2026",
  "matches": [
    {
      "round": "Matchday 1",
      "date": "2026-06-11",
      "time": "13:00 UTC-6",
      "team1": "Mexico",
      "team2": "South Africa",
      "group": "Group A",
      "ground": "Mexico City"
    }
  ]
}
```

### URL Match Fields

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `round` | `str` | `"Matchday 1"` | Contains matchday number; knockout rounds have different format |
| `date` | `str` | `"2026-06-11"` | YYYY-MM-DD format |
| `time` | `str` | `"13:00 UTC-6"` | HH:MM with UTC offset |
| `team1` | `str` | `"Mexico"` | Home team full name |
| `team2` | `str` | `"South Africa"` | Away team full name |
| `group` | `str` | `"Group A"` | Group name; absent for knockout matches |
| `ground` | `str` | `"Mexico City"` | Venue city, may include parenthetical detail |

---

## Transformed Data Format (normalized to API shape)

The `transform_match()` function converts URL dicts to this shape:

| Field | Type | Example | Source |
|-------|------|---------|--------|
| `utcDate` | `str` | `"2026-06-11T19:00:00Z"` | Synthesized from `date` + `time` (converted to UTC) |
| `status` | `str` | `"SCHEDULED"` | Hardcoded (URL data has no status) |
| `matchday` | `int` | `1` | Parsed from `round` numeric suffix |
| `group` | `str` | `"GROUP_A"` | Converted from "Group A" format |
| `venue` | `str` | `"Mexico City"` | From `ground` field |
| `homeTeam.name` | `str` | `"Mexico"` | From `team1` |
| `awayTeam.name` | `str` | `"South Africa"` | From `team2` |
| `homeTeam.tla` | `None` | `None` | Not available in URL data |
| `awayTeam.tla` | `None` | `None` | Not available in URL data |
| `score` | `None` | `None` | Not available in URL data |

---

## Filtering Rules

### Group Stage Filter (FR-003)

Only matches with a `group` field matching the pattern `"Group [A-L]"` are included. Knockout stage matches (Round of 32, Quarter-final, Semi-final, Final, etc.) have no `group` field or have values outside A-L range.

```python
def is_group_stage(match: dict) -> bool:
    group = match.get("group", "")
    return group.startswith("Group ") and len(group) == 8 and group[-1].isalpha()
```

### Sort Order (FR-007)

Matches are sorted by:
1. `date` ascending (YYYY-MM-DD string comparison)
2. `time` ascending (converted to UTC for consistent ordering)

---

## View State

### `_state` dict (view-local, not persisted)

Extends the existing `_state` dict in `schedule_view.py`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `all_matches` | `list[dict]` | `[]` | All fetched + transformed matches |
| `active_group` | `str` | `"All"` | Currently selected group chip: `"All"` or `"A"`–`"L"` |
| `data_source` | `str` | `""` | Origin of loaded data: `"url"`, `"local"`, or `"error"` |

---

## Invariants

- `_state["active_group"]` is always one of `{"All", "A", "B", ..., "L"}`.
- All matches in `_state["all_matches"]` have been transformed to the normalized dict shape.
- All matches have `group` field in `"GROUP_A"` through `"GROUP_L"` format.
- All matches have `status` set to `"SCHEDULED"`.
- All matches have `venue` set to a non-empty string (or "TBD" if ground was missing).
- Sort order is always: `date` asc, then `time` asc (both in UTC).
