# Data Model: World Cup Participating Countries Map

**Feature**: 001-worldcup-map | **Date**: 2026-05-15

## Entities

### ParticipatingCountry

Represents a nation qualified for the FIFA World Cup 2026.

```python
@dataclass(frozen=True)
class ParticipatingCountry:
    iso_a3: str          # ISO 3166-1 alpha-3 code (e.g. "BRA"), used as primary key
    name: str            # Display name (e.g. "Brazil")
    group: str           # FIFA group letter (e.g. "A" … "L")
    appearances: int     # Number of World Cup appearances including 2026
    flag_emoji: str      # Unicode flag emoji (e.g. "🇧🇷")
```

**Constraints**:
- `iso_a3` MUST be exactly 3 uppercase ASCII letters
- `group` MUST be a single uppercase letter A–L
- `appearances` MUST be >= 1
- Exactly 48 instances exist; duplicates are an error

---

### FIFAGroup

A logical grouping of 4 participating countries by FIFA assignment.

```python
@dataclass(frozen=True)
class FIFAGroup:
    name: str                       # Single letter, e.g. "A"
    countries: tuple[str, ...]      # Ordered tuple of iso_a3 codes (4 entries)
```

**Constraints**:
- `name` MUST be one of A–L (12 groups total for 2026)
- `countries` MUST contain exactly 4 distinct iso_a3 codes
- All iso_a3 codes MUST reference existing `ParticipatingCountry` instances

---

### GeoFeature

A GeoJSON feature (country boundary polygon) loaded from the static asset.
Not a dataclass — treated as an opaque dict from `json.load`. Relevant fields:

| JSON path | Type | Description |
|-----------|------|-------------|
| `properties.ISO_A3` | `str` | Matches `ParticipatingCountry.iso_a3` |
| `properties.NAME` | `str` | Country display name (fallback if not in team data) |
| `geometry.type` | `str` | `"Polygon"` or `"MultiPolygon"` |
| `geometry.coordinates` | `list` | Polygon ring(s) of `[lon, lat]` pairs |

**Handling**:
- `Polygon`: single ring list → `coordinates[0]`
- `MultiPolygon`: multiple polygon list → iterate `coordinates[i][0]`
- Antarctica (`ISO_A3 = "ATA"`) MUST be skipped during rendering (distorts bounding box)

---

### MapRenderState (runtime, not persisted)

Transient state held by `WorldCupMapView` during a user session.

```python
@dataclass
class MapRenderState:
    canvas_width: float
    canvas_height: float
    active_group_filter: str | None   # None = show all; "A"–"L" = filter to group
    selected_country: ParticipatingCountry | None  # Currently shown in info panel
```

---

## Asset Schemas

### `src/assets/worldcup2026.json`

Top-level array of team objects. One entry per qualifying nation.

```json
[
  {
    "iso_a3": "ARG",
    "name": "Argentina",
    "group": "B",
    "appearances": 18,
    "flag_emoji": "🇦🇷"
  }
]
```

- Array length MUST equal 48
- `iso_a3` values MUST be unique
- `group` values MUST be A–L; each group MUST appear exactly 4 times

### `src/assets/countries.geojson`

Standard GeoJSON FeatureCollection. Source: Natural Earth 1:110m admin-0.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "ISO_A3": "ARG", "NAME": "Argentina" },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon, lat], ...]]
      }
    }
  ]
}
```

---

## Relationships

```
ParticipatingCountry ----(iso_a3)----> GeoFeature.properties.ISO_A3
FIFAGroup.countries[] ---(iso_a3)---> ParticipatingCountry.iso_a3
MapRenderState.selected_country ----> ParticipatingCountry | None
MapRenderState.active_group_filter -> FIFAGroup.name | None
```
