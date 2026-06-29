# Contract: WorldCupJsonService

**Feature**: 016-group-stage-match-details  
**Date**: 2026-06-28

---

## Overview

`WorldCupJsonService` provides group stage match data from the openfootball worldcup.json URL with local file fallback. It is the sole data source for the Schedule tab when no API key is configured.

---

## Class: `WorldCupJsonService`

**Module**: `src/features/schedule/services/worldcup_json_service.py`

### Constructor

```python
class WorldCupJsonService:
    def __init__(
        self,
        url: str | None = None,
        local_path: str | Path | None = None,
    ) -> None:
```

**Parameters**:
- `url`: Override the default worldcup.json URL. Defaults to `config.WORLDCUP_JSON_URL` (`https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json`).
- `local_path`: Override the default local fallback file path. Defaults to `data/worldcup/2026/worldcup.json` relative to project root.

**Raises**: No exceptions at construction time. Errors occur during `get_group_matches()`.

---

## Public Methods

### `get_group_matches() -> list[dict]`

Fetches all group stage matches, transforms them to the normalized dict shape, and returns them sorted by date then time.

**Returns**: `list[dict]` — 48 match dicts (6 per group × 12 groups). Each dict conforms to the transformed data format (see data-model.md).

**Raises**:
- `WorldCupDataError` — if both URL fetch and local file fallback fail.

**Data source priority**:
1. Fetch from URL → success: return transformed data
2. URL fails (network error, timeout, HTTP error) → load local file
3. Local file fails (missing, malformed) → raise `WorldCupDataError`

**Side effects**: None. No caching (data is static tournament schedule).

---

### `get_data_source() -> str`

Returns the origin of the most recently loaded data.

**Returns**: One of:
- `"url"` — data was fetched from the remote URL
- `"local"` — data was loaded from the local fallback file
- `"error"` — no data has been loaded or last load failed

---

## Exceptions

### `WorldCupDataError(RuntimeError)`

Raised when both URL and local file sources fail to provide valid data.

**Attributes**:
- `message: str` — human-readable error description
- `url_error: Exception | None` — the original URL fetch error (if any)
- `file_error: Exception | None` — the original file load error (if any)

---

## Transformation Functions

### `transform_match(raw: dict) -> dict`

Converts a single URL-format match dict to the normalized shape expected by `match_row()`.

**Input**: Raw dict from worldcup.json with fields: `round`, `date`, `time`, `team1`, `team2`, `group`, `ground`.

**Output**: Normalized dict with fields: `utcDate`, `status`, `matchday`, `group`, `venue`, `homeTeam`, `awayTeam`, `score`.

**Rules**:
- `team1` → `homeTeam.name` (no `tla` field)
- `team2` → `awayTeam.name` (no `tla` field)
- `date` + `time` → `utcDate` (ISO-8601, UTC-normalized)
- `group` ("Group A") → `group` ("GROUP_A")
- `ground` → `venue` (or "TBD" if empty)
- `round` ("Matchday 1") → `matchday` (int 1)
- `status` → hardcoded `"SCHEDULED"`
- `score` → `None`

---

### `is_group_stage(match: dict) -> bool`

Returns `True` if the match belongs to a group stage (Group A through Group L).

**Input**: Raw match dict from worldcup.json.

**Output**: `True` if `group` field matches pattern `"Group [A-L]"`, `False` otherwise.

---

## Configuration

### `config.WORLDCUP_JSON_URL`

**Module**: `src/core/config.py`

**Type**: `str`

**Default**: `"https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"`

**Override**: Set `WORLDCUP_JSON_URL` environment variable.

---

## Usage Example

```python
from features.schedule.services.worldcup_json_service import WorldCupJsonService

service = WorldCupJsonService()
try:
    matches = service.get_group_matches()
    source = service.get_data_source()  # "url" or "local"
    print(f"Loaded {len(matches)} matches from {source}")
except WorldCupDataError as e:
    print(f"Failed to load data: {e}")
```

---

## Integration with Schedule View

The `build_schedule_view()` function in `schedule_view.py` is modified to:

1. Accept an optional `WorldCupJsonService` parameter (in addition to existing `FootballDataClient`).
2. Call `service.get_group_matches()` to load data.
3. Display a notice showing the data source (e.g., "Loaded from openfootball data (URL)" or "Loaded from local file").
4. Use the transformed match dicts with existing `match_row()` rendering.

**Priority**: If both `WorldCupJsonService` and `FootballDataClient` are available, prefer `WorldCupJsonService` (no API key required, always available).
