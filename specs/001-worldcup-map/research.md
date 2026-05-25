# Research: World Cup Participating Countries Map

**Feature**: 001-worldcup-map | **Date**: 2026-05-15

## Decision 1: Map Rendering Approach

**Decision**: `ft.Canvas` with GeoJSON polygon projection rendered in Python.

**Rationale**: Flet's `ft.Canvas` allows drawing arbitrary shapes and supports
`ft.GestureDetector` for click hit-testing. This requires no dependency outside
`flet[all]` and is fully constitution-compliant (no JavaScript, no external tiles).

**Alternatives considered**:
- *Embedded Leaflet.js via `ft.WebView`*: Rejected — violates Principle I (browser DOM / JavaScript).
- *Static SVG as `ft.Image`*: Attractive for simplicity, but `ft.Image` with SVG provides no per-polygon hit-testing; click coordinates cannot be mapped to country shapes.
- *Third-party mapping library (folium, plotly)*: Rejected — introduces runtime dependencies not in constitution's stack list; requires amendment.

---

## Decision 2: Map Projection

**Decision**: Equirectangular (plate carrée) projection.
- `x = (lon + 180) / 360 * canvas_width`
- `y = (90 - lat) / 180 * canvas_height`

**Rationale**: Simplest possible projection; requires only stdlib `float` arithmetic;
well-suited to political maps where exact area is not critical; familiar to users
(the standard "flat" world map).

**Alternatives considered**:
- *Web Mercator*: Larger formula, distorts polar regions, adds no value for country highlighting.
- *Robinson / Winkel Tripel*: Requires non-trivial iterative computation; overkill for this use case.

---

## Decision 3: Country Boundary Data

**Decision**: Natural Earth 1:110m admin-0 GeoJSON (`ne_110m_admin_0_countries.geojson`).

**Rationale**:
- Resolution 1:110m (simplified) — low filesize (~400 KB), renders fast.
- CC0 public-domain licence — no attribution required in-app.
- Each feature includes `ISO_A3` property for matching to team data.
- Available from: `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson`
- Bundle as `src/assets/countries.geojson` at development time; do NOT fetch at runtime.

**Alternatives considered**:
- *1:10m detail*: ~8 MB; acceptable but unnecessary at screen resolutions.
- *topojson*: Requires a parser; one more dependency.
- *Custom SVG paths*: Manual maintenance burden, no programmatic hit-testing.

---

## Decision 4: Hit-Testing (Click-to-Country)

**Decision**: Ray-casting point-in-polygon algorithm implemented in `geo_utils.py`.

**Rationale**:
- Pure Python, stdlib only (float arithmetic).
- O(n) per polygon ring; for 195 countries at 1:110m resolution (~50–300 points per polygon), acceptable at interactive rates.
- Works for both convex and concave polygons and multi-polygon countries.

**Implementation sketch**:
```python
def point_in_polygon(px: float, py: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside
```

**Alternatives considered**:
- *Shapely*: Correct and fast, but adds a C-extension dependency requiring a constitution amendment.
- *Bounding-box pre-filter only*: Fast but inaccurate for concave coastlines.

---

## Decision 5: World Cup 2026 Team Data

**Decision**: Hand-authored `src/assets/worldcup2026.json` bundled with the app.

**Rationale**: The 48 qualified teams are known and stable; a static file gives
zero-dependency offline capability. The file is small (< 8 KB) and easy to maintain.

**Schema** (see data-model.md for full contract):
```json
[
  {
    "iso_a3": "USA",
    "name": "United States",
    "group": "A",
    "appearances": 11,
    "flag_emoji": "🇺🇸"
  }
]
```

**Alternatives considered**:
- *Live FIFA API*: Creates a runtime network dependency; significantly increases complexity for no benefit since the team list is fixed.
- *SQLite*: Overengineered for 48 rows; violates Principle V.

---

## Decision 6: Flet Canvas Rendering Strategy

**Decision**: Draw each country as a single `ft.canvas.Path` shape. Re-draw only on
filter changes (not on every hover). Use `canvas.update()` to trigger repaint.

**Colour scheme**:
- Qualifying country: `#2ECC71` (green) / `#F39C12` (amber for selected group filter)
- Non-qualifying country: `#BDC3C7` (light grey)
- Country border: `#7F8C8D` (dark grey), stroke width 0.5

**Flet canvas API used**:
- `ft.canvas.Path` with `ft.canvas.PathMoveTo`, `ft.canvas.PathLineTo`, `ft.canvas.PathClose`
- `ft.canvas.Fill(color=...)` for the country polygon fill
- `ft.canvas.Stroke(color=..., width=0.5)` for borders
- `ft.GestureDetector(on_tap_down=...)` wrapping the canvas to capture click coordinates
