# Research: Schedule Group Stage Display

**Feature**: 012-schedule-group-display  
**Date**: 2026-06-09

---

## Decision 1 — Group Selector UI: Chips, not Dropdown

**Decision**: Replace the existing `styled_dropdown` with a row of interactive chip buttons (one per group A–L, plus "All").

**Rationale**: The spec explicitly describes "clearly labelled tabs or chips". Chips are immediately visible without a click to open; with 13 options (All + 12 groups) a chip row fits on a single line at standard widths and offers single-tap selection. The map tab already has a working chip row pattern (`group_filter.py`) that can be referenced.

**Alternatives considered**:
- `styled_dropdown` (current) — requires two interactions (open + select); lower discoverability. Already exists and works but does not meet the spec intent.
- `ft.Tabs` — heavyweight; not styled to match the dark theme without custom overrides; adds unnecessary state management.

**Implementation note**: The map `GroupFilter` uses `@ft.component` (requires Renderer context). The schedule chips are plain `ft.Container` + `on_click` + manual `.update()` — simpler and correct outside a component renderer.

---

## Decision 2 — Venue Display: Raw Venue Name from API, not City

**Decision**: Display the raw `venue` field from the API (stadium name, e.g. "MetLife Stadium") in the match row instead of the city derived via `venue_to_city()`.

**Rationale**: FR-009 explicitly requires "full stadium name". The current `match_row` passes `venue` through `venue_to_city()` which discards the stadium name and shows only a city. The API `venue` field already contains the full stadium name as a string.

**Alternatives considered**:
- Show both city and stadium — too wide for the existing row layout; clutters the display.
- Keep city only — directly contradicts FR-009.

**Implementation note**: `match_row()` currently has a `city` parameter built from `venue_to_city(match.get("venue"))`. Change to use `match.get("venue") or "TBD"` directly in the row, rename the column header from "City" to "Venue".

---

## Decision 3 — Chip State Management: Local mutable state variable

**Decision**: Store the active group selection in a `dict` (same `_state` dict already used for `all_matches`) and update chips manually via `.update()` on the chip row.

**Rationale**: The schedule view is a plain builder function (not a `@ft.component`). A simple `_state["group"]` key toggled on chip click, followed by re-render of the chip row and match list, is the simplest correct approach. No observable/reactive pattern needed here.

**Alternatives considered**:
- `@ft.component` + `param.Parameterized` state — would require wrapping the whole view in a renderer context; disproportionate complexity for a filter toggle.

---

## Decision 4 — Match Row Changes: Minimal diff to existing `match_row()`

**Decision**: Modify the existing `match_row()` function signature to accept `venue_name: str` (replacing implicit `city`) and update the column. All other fields (matchday, date, time, group, home, score, away, status) remain unchanged.

**Rationale**: The existing match row already correctly handles all status variants, score display, and UTC labelling. Constitution V (YAGNI) says to make the minimum change. Only the venue column needs to change.

**Alternatives considered**:
- Rewrite match_row entirely — unnecessary; existing logic is correct.
- Add a second column for venue alongside city — too wide; the row already fills ~750 px.

---

## Decision 5 — No New Service Layer Required

**Decision**: Use the existing `FootballDataClient.get_group_matches(season=2026)` unchanged. No new service functions needed.

**Rationale**: The method already returns all 48 group-stage matches with `venue`, `status`, `utcDate`, `group`, `matchday`, `homeTeam`, `awayTeam`, `score` fields. All filtering is done client-side in the view layer (already the pattern). Constitution IV is satisfied: the UI does not call the API directly; it goes through `FootballDataClient`.

---

## Decision 6 — Chip Row Scroll: `ft.Row(wrap=True)`

**Decision**: The chip row uses `wrap=True` so it reflows to 2–3 rows on narrow viewports (≥360 px) instead of overflowing horizontally.

**Rationale**: SC-005 requires usability from 360 px. With 13 chips at ~70 px each, a single row needs ~910 px. `wrap=True` handles this automatically with no extra code.
