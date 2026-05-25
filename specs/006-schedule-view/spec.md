# Feature Specification: 2026 Pool Match Schedule View

**Feature Branch**: `006-schedule-view`
**Created**: 2026-05-22
**Status**: Draft
**Input**: "please show on another page the match days and times for each pool match and the city in which it will be played."

---

## Problem Statement

There is no single dedicated view showing the complete 2026 group-stage (pool) schedule
with kick-off times and host cities. The existing Matches tab focuses on historical
data and uses a generic table layout. A new **Schedule** tab will surface the
2026 pool fixtures from the football-data.org API in a clean, chronological schedule
layout — matchday, date, local time, group, home vs away, and city.

---

## User Scenarios & Testing

### User Story 1 — View full group-stage schedule (P1)

A user opens the Schedule tab. All 48 group-stage matches are shown sorted by
matchday then kick-off time, each with the host city.

**Acceptance Scenarios**:

1. **Given** the Schedule tab is open, **When** it loads, **Then** matches are
   displayed with columns: Matchday, Date, Time (UTC), Group, Home, Away, Score/Status, City.
2. **Given** matches are sorted by `matchday` then `utcDate`, **When** rendered,
   **Then** earlier matches appear first.
3. **Given** the API returns a `venue` field (stadium name) for each match,
   **When** rendered, **Then** the corresponding city from the host-venue lookup is shown.
4. **Given** a match has status `SCHEDULED` or `TIMED`, **When** rendered,
   **Then** the Score column shows "vs" and the status badge shows "Scheduled".
5. **Given** a match has status `FINISHED`, **When** rendered,
   **Then** the Score column shows `home–away` (e.g. "2–1").

### User Story 2 — Filter by group (P2)

A user selects "Group B" from a dropdown. Only Group B matches are shown.

**Acceptance Scenarios**:

1. **Given** 48 matches loaded, **When** user selects "Group C", **Then** only the
   group C matches are shown (6 matches × 3 = depends on format but typically 6).
2. **Given** filter "All" is selected, **When** rendered, **Then** all 48 matches shown.

### User Story 3 — No API key fallback (P1)

**Given** `FOOTBALL_DATA_API_KEY` is not set, **When** the Schedule tab loads,
**Then** a message "Set FOOTBALL_DATA_API_KEY to load the live schedule" is shown
instead of an empty table.

---

## Technical Design

### Data source

`FootballDataClient.get_group_matches(season=2026)` already returns the required
fields per match:

| API field | Display |
|-----------|---------|
| `matchday` | Matchday column |
| `utcDate` | Date + Time columns (split at "T") |
| `group` | Group column (strip "GROUP_" prefix → "A"…"L") |
| `homeTeam.name` | Home column |
| `awayTeam.name` | Away column |
| `score.fullTime.home/away` | Score column ("vs" if null) |
| `status` | Status badge |
| `venue` | Looked up against `VENUE_CITY` dict → City column |

### Venue → City lookup

Extract the `_VENUES` list from `osm_map_view.py` into
`src/shared/venue_data.py` so both the OSM map view and the schedule view share
the same authoritative venue data.  Build a `VENUE_CITY: dict[str, str]` mapping
`stadium_name → city`.  Stadium names from the API may differ slightly from local
names, so use a case-insensitive substring match fallback.

### New files

- `src/shared/venue_data.py` — venue list + `VENUE_CITY` lookup + `venue_to_city(name)` helper
- `src/views/schedule_view.py` — `build_schedule_view(fd_client)` → `ft.Column`

### Updated files

- `src/views/osm_map_view.py` — import `_VENUES` from `shared.venue_data` instead of defining locally
- `src/main.py` — add 7th tab "Schedule" and nav destination

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  📅  2026 World Cup Pool Schedule                        │
│  Group-stage kick-off times and host cities (UTC)        │
│  ──────────────────────────────────────────────────────  │
│  [Group ▼ All]  [● Loading…]                             │
│  ⚠️ notice text (API warnings / errors)                  │
│                                                          │
│  Matchday │ Date       │ Time  │ Grp │ Home   │ Away   │ Score │ City │
│  ─────────────────────────────────────────────────────── │
│  1        │ 2026-06-11 │ 20:00 │ A   │ USA    │ Mexico │ vs    │ Dallas│
│  …                                                       │
└──────────────────────────────────────────────────────────┘
```

### Sort order

Matches sorted by `(matchday, utcDate)` ascending within each rendered batch.

---

## Out of Scope

- Knock-out rounds
- Timezone conversion (UTC is displayed; user can convert locally)
- Live score updates / auto-refresh
