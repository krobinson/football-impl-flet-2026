# Feature Specification: Country Polygons on OSM Map

**Feature Branch**: `004-polygon-countries`
**Created**: 2026-05-20
**Status**: Draft
**Input**: "on the world map 2026 we only have dots marking each country that is playing in the world cup. Please change the dot to be a polygon which goes around the perimeter of each country."

---

## Problem Statement

The "2026 Map" tab currently renders one circle `Marker` per qualifying country,
placed at the country's bounding-box centroid. This gives no sense of the country's
actual shape or size.

The fix is to replace `MarkerLayer` + circle markers with `PolygonLayer` +
`PolygonMarker` objects whose `coordinates` are taken directly from the GeoJSON
outer rings, so each qualifying country is filled and outlined on the OSM tile map.

---

## User Scenarios & Testing

### User Story 1 — Qualifying countries shown as filled polygons (P1)

A user opens the "2026 Map" tab. Each of the 48 World Cup qualifying nations is
rendered as a filled polygon with a coloured border that traces the country's real
geographic boundary.

**Acceptance Scenarios**:

1. **Given** the map tab is open, **When** it first renders, **Then** each qualifying
   country is visible as a coloured polygon (not a dot) overlaying the OSM tiles.
2. **Given** a `MultiPolygon` country (e.g. USA, Indonesia), **When** rendered,
   **Then** all island/territorial polygons are drawn, not just the mainland.
3. **Given** no group filter is active, **When** the map renders, **Then** all
   qualifying polygons are green with a white border; non-qualifiers have no polygon.
4. **Given** a group filter is set, **When** the map renders, **Then** countries in
   the group are orange, other qualifiers are dimmed grey.
5. **Given** a country is selected, **When** the map renders, **Then** that country's
   polygon(s) are red.

### User Story 2 — Clicking a polygon selects the country (P1)

A user clicks anywhere inside a qualifying country's polygon on the map.

**Acceptance Scenarios**:

1. **Given** the user taps inside a qualifying polygon, **When** the tap resolves,
   **Then** that country is selected and the info panel updates.
2. **Given** the user taps the ocean or a non-qualifying country, **When** the tap
   resolves, **Then** the selection is cleared (or unchanged).

---

## Technical Design

### API used

- `ftm.PolygonLayer(polygons=[...], simplification_tolerance=0.5)`
- `ftm.PolygonMarker(coordinates=[MapLatitudeLongitude(lat, lon), ...], color=..., border_color=..., border_stroke_width=1.5)`
  - `coordinates` takes `(latitude, longitude)` — note reverse from GeoJSON `[lon, lat]`
- `ftm.Map(on_tap=...)` — `MapTapEvent` gives `.coordinates.latitude/.longitude`

### Hit-testing

`PolygonMarker` has no `on_tap`. Use the `Map`-level `on_tap` callback with a pure
geographic point-in-polygon test (`_point_in_polygon` from `geo_utils.py`) operating
directly on GeoJSON lon/lat rings — no pixel projection needed.

### GeoJSON → PolygonMarker conversion

For each GeoJSON feature whose `ISO_A3` (or `ADM0_A3` fallback) is a qualifier:
- `Polygon`: one `PolygonMarker` from `coordinates[0]` (outer ring)
- `MultiPolygon`: one `PolygonMarker` per sub-polygon's outer ring

Use `ft.Colors.with_opacity(0.35, fill_colour)` for the fill so the OSM tiles
show through, and a solid `border_color` at full opacity.

### Refresh strategy

On state change (selection, group filter), rebuild the entire `PolygonLayer.polygons`
list and call `polygon_layer.update()` — same pattern as the existing marker refresh.

### Files changed

| File | Change |
|------|--------|
| `src/views/map_view.py` | Replace `MarkerLayer`+centroid logic with `PolygonLayer`; add geo hit-test |
| `src/shared/geo_utils.py` | Export `geo_hit_test(lon, lat, features)` → `str | None` for map-level tap |

### No new dependencies

`flet-map` is already installed.

---

## Out of Scope

- Hole/interior ring rendering (lakes inside countries)
- Hover/tooltip on polygons (not supported by `PolygonMarker`)
- Non-qualifying country outlines (kept as plain OSM tiles)
