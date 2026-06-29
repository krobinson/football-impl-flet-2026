# UI Contracts: Schedule Group Stage Display

**Feature**: 012-schedule-group-display  
**Date**: 2026-06-09

---

## Contract 1 — Group Chip Row

**Function**: `_build_group_chips(active_group: str, on_select: Callable[[str], None]) -> ft.Row`  
**Location**: `src/features/schedule/views/schedule_view.py` (view-local helper)

### Parameters

| Name | Type | Description |
|------|------|-------------|
| `active_group` | `str` | Currently selected group: `"All"` or single letter `"A"`–`"L"` |
| `on_select` | `Callable[[str], None]` | Called with the new group string when a chip is tapped |

### Return

`ft.Row(wrap=True, spacing=6, run_spacing=6)` containing 13 chip containers: "All" + "A"–"L".

### Chip visual states

| State | Background | Text colour |
|-------|-----------|------------|
| Active (selected) | `#F39C12` (amber) | `#000000` |
| Inactive | `#2C3E50` (dark blue-grey) | `#ECF0F1` |

### Behaviour

- Tapping a chip that is not active → calls `on_select(letter)`.
- Tapping the active chip → does NOT toggle off (selecting "All" again requires tapping "All").
- Chips never disappear or disable — all 13 are always rendered.

---

## Contract 2 — `match_row()` venue column change

**Function**: `match_row(match: dict, row_idx: int) -> ft.Container`  
**Location**: `src/features/schedule/components/match_row.py`

### Changed behaviour (internal only, no signature change)

| Column | Before | After |
|--------|--------|-------|
| Last column header | "City" | "Venue" |
| Last column value | `venue_to_city(match.get("venue"))` | `match.get("venue") or "TBD"` |

### All other columns unchanged

matchday, date, time (UTC), group badge, home, score/vs, away, status badge.

---

## Contract 3 — `build_schedule_view()` public interface (unchanged)

**Function**: `build_schedule_view(fd_client: FootballDataClient | None = None) -> ft.Column`  
**Location**: `src/features/schedule/views/schedule_view.py`

The public function signature is **unchanged**. Internal implementation replaces the `group_dd` dropdown with the `chips_row` but the caller in `app.py` requires no modification.
