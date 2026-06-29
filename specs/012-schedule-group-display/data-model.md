# Data Model: Schedule Group Stage Display

**Feature**: 012-schedule-group-display  
**Date**: 2026-06-09

---

## Existing Entities (unchanged)

### MatchDict (runtime dict from football-data.org API)

No new model classes introduced. The existing dict shape from `FootballDataClient.get_group_matches()` is reused as-is.

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `utcDate` | `str` | `"2026-06-11T18:00:00Z"` | ISO-8601 UTC |
| `status` | `str` | `"SCHEDULED"`, `"FINISHED"` | See status map below |
| `matchday` | `int` | `1` | Group stage matchday 1–3 |
| `group` | `str` | `"GROUP_A"` | Strip `GROUP_` prefix for display |
| `venue` | `str \| None` | `"MetLife Stadium"` | Full stadium name; `None` → show "TBD" |
| `homeTeam.name` | `str` | `"USA"` | |
| `awayTeam.name` | `str` | `"Mexico"` | |
| `score.fullTime.home` | `int \| None` | `2` | `None` if not played |
| `score.fullTime.away` | `int \| None` | `1` | `None` if not played |

### Match Status Values

| API value | Display label | Colour |
|-----------|--------------|--------|
| `SCHEDULED` | Scheduled | Grey |
| `TIMED` | Confirmed | Blue |
| `IN_PLAY` | LIVE | Green |
| `PAUSED` | HT | Orange |
| `FINISHED` | FT | Grey (muted) |
| `POSTPONED` | Postponed | Red |
| `CANCELLED` | Cancelled | Red |

---

## New UI State

### `_state` dict (view-local, not persisted)

Extends the existing `_state` dict in `schedule_view.py`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `all_matches` | `list[dict]` | `[]` | All fetched matches (existing) |
| `active_group` | `str` | `"All"` | Currently selected group chip value: `"All"` or `"A"`–`"L"` |

---

## Changed Function Signatures

### `match_row(match, row_idx)` → `match_row(match, row_idx)` (no signature change)

The function is modified internally: the `city` variable is replaced with the raw `venue` field value. No signature change; callers are unaffected.

### `build_schedule_view(fd_client)` — internal refactor only

- `group_dd` (dropdown) removed; replaced with `chips_row` (`ft.Row` of chip containers).
- `_apply_group_filter` updated to read `_state["active_group"]` instead of `group_dd.value`.

---

## Invariants

- `_state["active_group"]` is always one of `{"All", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"}`.
- A chip is "active" when `_state["active_group"] == chip_label`.
- Filtering: when `active_group == "All"`, all matches are shown; otherwise matches where `match["group"] == f"GROUP_{active_group}"` are shown.
- Sort order is always: `matchday` asc, then `utcDate` asc.
