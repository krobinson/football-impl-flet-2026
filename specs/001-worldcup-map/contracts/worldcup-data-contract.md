# Interface Contract: WorldCupDataService

**Module**: `src/services/worldcup_data.py`
**Type**: Internal Python API (called by view layer only)
**Date**: 2026-05-15

## Overview

`WorldCupDataService` is the sole data-access point for the world-map feature.
It loads static asset files once on construction and exposes read-only query
methods. Views MUST NOT read asset files directly.

---

## Constructor

```python
WorldCupDataService(
    teams_path: str | Path,
    geo_path: str | Path,
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `teams_path` | `str \| Path` | Absolute or relative path to `worldcup2026.json` |
| `geo_path` | `str \| Path` | Absolute or relative path to `countries.geojson` |

**Raises**: `FileNotFoundError` if either file is missing.
**Raises**: `ValueError` if team data fails validation (count != 48, duplicate iso_a3).

---

## Methods

### `get_all_teams() -> list[ParticipatingCountry]`

Returns all 48 participating countries, unordered.

**Returns**: `list[ParticipatingCountry]` (length == 48)
**Raises**: never (data already validated on construction)

---

### `get_team(iso_a3: str) -> ParticipatingCountry | None`

Returns the team for a given ISO-A3 code, or `None` if not a qualifier.

| Parameter | Type | Description |
|-----------|------|-------------|
| `iso_a3` | `str` | 3-letter ISO code, case-insensitive |

**Returns**: `ParticipatingCountry` or `None`

---

### `get_groups() -> list[FIFAGroup]`

Returns all 12 FIFA groups (A–L), each containing 4 countries.

**Returns**: `list[FIFAGroup]` sorted alphabetically by `name`

---

### `get_group(name: str) -> FIFAGroup | None`

Returns the group with the given letter, or `None` if invalid.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Single letter A–L, case-insensitive |

**Returns**: `FIFAGroup` or `None`

---

### `get_geo_features() -> list[dict]`

Returns all GeoJSON feature dicts from `countries.geojson`, excluding Antarctica.

**Returns**: `list[dict]` — each dict has `properties` and `geometry` keys as
described in data-model.md.

---

### `is_qualifier(iso_a3: str) -> bool`

Returns `True` if the ISO-A3 code belongs to a World Cup 2026 qualifier.

| Parameter | Type | Description |
|-----------|------|-------------|
| `iso_a3` | `str` | 3-letter ISO code, case-insensitive |

**Returns**: `bool`

---

## Error Handling Contract

| Scenario | Behaviour |
|----------|-----------|
| Asset file missing at startup | `FileNotFoundError` raised in constructor |
| Asset file not valid JSON | `json.JSONDecodeError` propagates from constructor |
| Team count != 48 | `ValueError("Expected 48 teams, got N")` in constructor |
| Duplicate iso_a3 in team data | `ValueError("Duplicate iso_a3: XYZ")` in constructor |
| Unknown iso_a3 in query | Return `None` (never raise) |
| Unknown group letter in query | Return `None` (never raise) |

The view layer MUST catch `FileNotFoundError` and `ValueError` at app startup
and display a user-visible error panel rather than crashing.

---

## GeoUtils Contract

**Module**: `src/shared/geo_utils.py`

### `project(lon: float, lat: float, width: float, height: float) -> tuple[float, float]`

Converts WGS-84 lon/lat to canvas pixel coordinates using equirectangular projection.

### `hit_test(px: float, py: float, features: list[dict], width: float, height: float) -> str | None`

Returns the `ISO_A3` of the first GeoJSON feature whose polygon contains the screen
point `(px, py)`, or `None` if no match. Tests all rings of MultiPolygon features.
