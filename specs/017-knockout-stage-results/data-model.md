# Data Model: Knockout Stage Results & Live Scores

**Feature**: 017-knockout-stage-results  
**Date**: 2026-07-04

---

## Source Data Format (openfootball worldcup.json)

The URL returns a JSON object with 104 matches. Group stage matches have a `group` field; knockout matches do not.

### Group Stage Match (with score)

```json
{
  "round": "Matchday 1",
  "date": "2026-06-11",
  "time": "13:00 UTC-6",
  "team1": "Mexico",
  "team2": "South Africa",
  "score": { "ft": [2, 0], "ht": [1, 0] },
  "goals1": [{"name": "Julián Quiñones", "minute": "9"}],
  "goals2": [],
  "group": "Group A",
  "ground": "Mexico City"
}
```

### Knockout Match (with score)

```json
{
  "round": "Round of 32",
  "num": 73,
  "date": "2026-06-28",
  "time": "12:00 UTC-7",
  "team1": "South Africa",
  "team2": "Canada",
  "score": { "ft": [0, 1], "ht": [0, 0] },
  "goals1": [],
  "goals2": [{"name": "Stephan Eustáquio", "minute": "90+2"}],
  "ground": "Los Angeles (Inglewood)"
}
```

### Knockout Match (upcoming, no score)

```json
{
  "round": "Round of 32",
  "num": 74,
  "date": "2026-06-29",
  "time": "16:30 UTC-4",
  "team1": "1E",
  "team2": "3A/B/C/D/F",
  "ground": "Boston (Foxborough)"
}
```

---

## Transformed Data Format (extended from feature 016)

The `transform_match()` function now produces these additional fields:

| Field | Type | Example | Source |
|-------|------|---------|--------|
| `utcDate` | `str` | `"2026-06-28T19:00:00Z"` | Synthesized from `date` + `time` (converted to UTC) |
| `status` | `str` | `"FINISHED"` or `"SCHEDULED"` | Derived from score presence |
| `matchday` | `int` | `1` | Parsed from `round` numeric suffix; 99 for knockout |
| `group` | `str` | `"GROUP_A"` or `""` | Converted from "Group A"; empty for knockout |
| `venue` | `str` | `"Los Angeles (Inglewood)"` | From `ground` field (or "TBD") |
| `homeTeam.name` | `str` | `"South Africa"` or `"1A"` | From `team1` |
| `awayTeam.name` | `str` | `"Canada"` or `"2B"` | From `team2` |
| `homeTeam.tla` | `None` | `None` | Not available in URL data |
| `awayTeam.tla` | `None` | `None` | Not available in URL data |
| `score` | `dict` or `None` | `{"fullTime": {"home": 0, "away": 1}}` | Transformed from `score.ft`; None if no score |
| `stage` | `str` | `"ROUND_OF_32"` | **NEW**: Derived from `round`/`group` |
| `round_display` | `str` | `"R32"` | **NEW**: Short display label for knockout round |

---

## Stage Classification

### `classify_stage(match: dict) -> str`

```python
def classify_stage(match: dict) -> str:
    group = match.get("group", "")
    if group.startswith("Group "):
        return "GROUP_STAGE"
    round_name = match.get("round", "")
    stage_map = {
        "Round of 32": "ROUND_OF_32",
        "Round of 16": "ROUND_OF_16",
        "Quarter-final": "QUARTER_FINAL",
        "Semi-final": "SEMI_FINAL",
        "Final": "FINAL",
        "Match for third place": "FINAL",
    }
    return stage_map.get(round_name, "UNKNOWN")
```

### `round_display_label(match: dict) -> str`

```python
def round_display_label(match: dict) -> str:
    group = match.get("group", "")
    if group.startswith("Group "):
        return ""
    round_name = match.get("round", "")
    label_map = {
        "Round of 32": "R32",
        "Round of 16": "R16",
        "Quarter-final": "QF",
        "Semi-final": "SF",
        "Final": "F",
        "Match for third place": "3rd",
    }
    return label_map.get(round_name, "")
```

---

## Stage Filter Values

| Stage Chip Label | Filter Value | Match Count |
|-----------------|--------------|-------------|
| All | `"ALL"` | 104 |
| Group Stage | `"GROUP_STAGE"` | 72 |
| R32 | `"ROUND_OF_32"` | 16 |
| R16 | `"ROUND_OF_16"` | 8 |
| QF | `"QUARTER_FINAL"` | 4 |
| SF | `"SEMI_FINAL"` | 2 |
| Final | `"FINAL"` | 2 (Final + 3rd place) |

---

## View State

### `_state` dict (extended from feature 016)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `all_matches` | `list[dict]` | `[]` | All 104 fetched + transformed matches |
| `active_stage` | `str` | `"ALL"` | Currently selected stage chip |
| `active_group` | `str` | `"All"` | Currently selected group chip (only applies when stage is GROUP_STAGE) |
| `data_source` | `str` | `""` | Origin of loaded data: `"url"`, `"local"`, or `"error"` |

---

## Invariants

- `_state["active_stage"]` is always one of `{"ALL", "GROUP_STAGE", "ROUND_OF_32", "ROUND_OF_16", "QUARTER_FINAL", "SEMI_FINAL", "FINAL"}`.
- `_state["active_group"]` is always one of `{"All", "A", "B", ..., "L"}`.
- Group chips are visible only when `active_stage == "GROUP_STAGE"`.
- All matches in `_state["all_matches"]` have been transformed to the normalized dict shape.
- All matches have `stage` field set to a valid stage value.
- Knockout matches have `group` set to `""` (empty string).
- Knockout matches have `round_display` set to a non-empty short label.
- Sort order is always: `date` asc, then `time` asc (both in UTC).
