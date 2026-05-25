# Feature Specification: Responsive Layout & Interactive Map Pan/Zoom

**Feature Branch**: `002-responsive-map`
**Created**: 2026-05-16
**Status**: Draft
**Input**: "please make the fit the display for both mobile phones and a desktop. In particular make the map moveable via touch or keys."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Responsive Layout Adapts to Screen Size (Priority: P1)

A user opens the app on a phone (< 650 px wide). The map fills the full width of
the screen and the info panel stacks below it vertically. On a desktop the existing
side-by-side layout is preserved. Navigation bar destination labels are visible on
desktop and hidden on mobile to save space.

**Acceptance Scenarios**:

1. **Given** the app is open on a device with viewport width < 650 px, **When** the map tab is shown, **Then** the map container spans 100 % of the available width and the info panel renders below the map.
2. **Given** the app is open on a desktop (width ≥ 650 px), **When** the map tab is shown, **Then** the map and info panel are arranged side-by-side (Row layout, info panel ~300 px wide).
3. **Given** the viewport is resized from desktop to mobile width, **When** the resize event fires, **Then** the layout transitions to the mobile stack without a page reload.
4. **Given** a mobile viewport, **When** the NavigationBar renders, **Then** destination labels are hidden to maximise map canvas area.

---

### User Story 2 — Map Pan via Touch Drag or Keyboard Arrows (Priority: P1)

A user on mobile can drag a finger across the map canvas to pan the view. A
desktop user can drag with the mouse or press arrow keys to pan. The pan offset
is stored in `MapRenderState` and applied during country polygon projection so all
country outlines move correctly together.

**Acceptance Scenarios**:

1. **Given** the map is displayed, **When** the user drags left/right/up/down on the canvas, **Then** all country polygons translate by the same delta and the canvas redraws within 100 ms.
2. **Given** the map is displayed, **When** the user presses the Left/Right/Up/Down arrow keys (with the page focused), **Then** the map pans 30 px in the corresponding direction per keypress.
3. **Given** the user has panned the map, **When** the user double-taps or presses the `Home` key, **Then** the pan resets to `(0, 0)` and zoom resets to `1.0`.

---

### User Story 3 — Map Zoom via Pinch-to-Zoom, Scroll, or Keyboard (Priority: P2)

A user on mobile can pinch (two-finger gesture) to zoom in/out on the map. A
desktop user can use the mouse wheel or `+` / `-` keys. Zoom is clamped between
0.5× and 8× and is centred on the gesture focal point.

**Acceptance Scenarios**:

1. **Given** the map is displayed, **When** the user scrolls the mouse wheel up/down, **Then** the map zooms in/out centred on the cursor position.
2. **Given** the map is displayed on mobile, **When** the user performs a pinch-to-zoom gesture, **Then** the map scales centred on the midpoint between the two touch points.
3. **Given** the map is displayed, **When** the user presses `+` or `=`, **Then** the zoom level increases by 25 %; pressing `-` decreases it by 25 %.
4. **Given** any zoom/pan state, **When** the zoom would fall below 0.5× or exceed 8×, **Then** the zoom is clamped at the boundary and no JavaScript error is raised.
5. **Given** the user has zoomed/panned, **When** the Home key or reset button is pressed, **Then** zoom returns to 1.0 and pan returns to (0, 0).

---

### User Story 4 — Reset Control (Priority: P2)

A small "⌂ Reset" icon button overlaid on the map allows the user to instantly
restore pan=(0,0) and zoom=1.0 with a single tap/click.

**Acceptance Scenarios**:

1. **Given** the user has panned or zoomed the map, **When** the reset button is tapped, **Then** pan and zoom reset and the map redraws.
2. **Given** pan=(0,0) and zoom=1.0 (default state), **When** the reset button is tapped, **Then** no visual change occurs (no error).

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Flet-First UI | ✅ PASS | `GestureDetector.on_pan_update`, `on_scale_update`, `on_scroll`, `page.on_keyboard_event` — no JS. |
| II. Feature-Module Separation | ✅ PASS | All changes confined to `map_view.py`, `shared/models.py`, `shared/geo_utils.py`. |
| III. Test-First | ✅ PASS | Projection-with-offset unit tests written before touching `geo_utils.project`. |
| IV. API-Backed Data Layer | ✅ PASS | `WorldCupDataService` unchanged. State lives in `MapRenderState`. |
| V. Simplicity & YAGNI | ✅ PASS | No external map libraries — offset/scale applied algebraically in `project()`. |

---

## Technical Design

### State additions to `MapRenderState`

```python
pan_x: float = 0.0      # horizontal pixel offset
pan_y: float = 0.0      # vertical pixel offset
zoom: float = 1.0       # scale factor (0.5 – 8.0)
```

### Updated `project()` signature in `geo_utils.py`

```python
def project(
    lon: float, lat: float,
    canvas_w: float, canvas_h: float,
    pan_x: float = 0.0,
    pan_y: float = 0.0,
    zoom: float = 1.0,
) -> tuple[float, float]:
    # equirectangular, then scale from centre, then translate
    cx = canvas_w / 2
    cy = canvas_h / 2
    x_base = (lon + 180) / 360 * canvas_w
    y_base = (90 - lat) / 180 * canvas_h
    x = cx + (x_base - cx) * zoom + pan_x
    y = cy + (y_base - cy) * zoom + pan_y
    return x, y
```

### Gesture wiring in `map_view.py`

| Gesture | Flet event | Action |
|---------|-----------|--------|
| Drag / touch pan | `GestureDetector.on_pan_update` | `state.pan_x += e.delta_x; state.pan_y += e.delta_y` |
| Pinch-to-zoom | `GestureDetector.on_scale_update` | `state.zoom = clamp(state.zoom * e.scale, 0.5, 8.0)` |
| Mouse scroll | `GestureDetector.on_scroll` | zoom ± 10 % per scroll tick, centred on cursor |
| Arrow keys | `page.on_keyboard_event` | pan ±30 px per event |
| `+` / `-` keys | `page.on_keyboard_event` | zoom ± 25 % |
| `Home` key / reset button | event / button | reset pan+zoom |
| Double-tap | `GestureDetector.on_double_tap` | reset pan+zoom |

### Responsive layout breakpoint

```python
_MOBILE_BREAKPOINT = 650  # px

def _is_mobile(page: ft.Page) -> bool:
    return (page.width or 1200) < _MOBILE_BREAKPOINT
```

`page.on_resized` wires to a handler that rebuilds the outer Row/Column layout and
calls `page.update()`.

---

## Out of Scope

- Tile-based map rendering (no external services)
- Inertial / momentum scrolling after a pan gesture ends
- Animated zoom transitions
- Country label rendering at high zoom levels
- Hit-test accuracy improvement at high zoom (tracked separately if needed)
