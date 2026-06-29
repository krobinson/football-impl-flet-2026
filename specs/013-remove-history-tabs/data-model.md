# Data Model: Remove History Tabs

**Feature**: 013-remove-history-tabs
**Date**: 2026-06-10

---

## No new entities

This feature removes code — no new data models, dataclasses, or state structures are introduced.

---

## Changed: `_build_app()` function signature

| | Before | After |
|--|--------|-------|
| Signature | `_build_app(page, svc, store, fd_client)` | `_build_app(page, svc, fd_client)` |
| `page.render(...)` call | `page.render(_build_app, page, svc, store, fd_client)` | `page.render(_build_app, page, svc, fd_client)` |

---

## Removed: tab body variables

| Variable | Was |
|----------|-----|
| `tournament_content` | `ft.Container(build_tournament_view(store), ...)` |
| `teams_content` | `ft.Container(build_teams_view(store), ...)` |
| `matches_content` | `ft.Container(build_matches_view(store, ...), ...)` |
| `records_content` | `ft.Container(build_records_view(store), ...)` |

---

## Remaining: tab body variables (unchanged)

| Variable | Content |
|----------|---------|
| `map_tab_content` | 2026 Map (index 0) |
| `osm_content` | Venues (index 1) |
| `schedule_content` | Schedule (index 2) |

---

## Removed: nav destinations (indices 1–4 of old list)

| Old index | Label | Icon |
|-----------|-------|------|
| 1 | History | `EMOJI_EVENTS` |
| 2 | Teams | `GROUPS` |
| 3 | Matches | `SEARCH` |
| 4 | Records | `LEADERBOARD` |

## Remaining: nav destinations (new indices 0–2)

| New index | Label | Icon |
|-----------|-------|------|
| 0 | 2026 Map | `MAP` |
| 1 | Venues | `PUBLIC` |
| 2 | Schedule | `CALENDAR_MONTH` |
