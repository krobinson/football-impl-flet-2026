# Feature Specification: Core UI Component Library

**Feature Branch**: `009-core-components`
**Created**: 2026-05-24
**Status**: Draft
**Input**: "please extract the common ui components into a /core/components directory"

---

## Problem Statement

Every feature view (`tournament`, `teams`, `records`, `matches`, `schedule`,
`map`) duplicates the same structural boilerplate:

| Duplicated pattern | Views affected |
|--------------------|----------------|
| Page header: 22 px bold title + 13 px subtitle + `ft.Divider` | All 6 views |
| `ft.Dropdown` with identical style props (`bgcolor`, `color`, `focused_border_color`, `border_color`) | 7 dropdown instances across 4 views |
| Scrollable table card: `ft.Container(ft.Column([…], scroll=AUTO), bgcolor=BG_CARD, border_radius=8, height=380, border=Border.all(1, BORDER_COLOR))` | `matches_view`, `records_view` (both inline; `scrollable_card()` in `ui_helpers.py` exists but is unused here) |
| Loading row: `ft.ProgressRing` (20 × 20, hidden) + `ft.Text("", visible=False)` status banner, updated by background threads | `matches_view`, `schedule_view` |

The duplication scatters styling decisions across feature files, making
theme changes require edits in many places.  `core/ui_helpers.py` already
collects atomic helpers (colours, `card()`, `stat_badge()`, `build_bar_chart()`,
`build_data_table()`), but higher-level structural components do not exist yet.

---

## Goals

1. Create `src/core/components/` Python package.
2. Define four shared component factories there:
   - `page_header(title, subtitle)` → `ft.Column`
   - `styled_dropdown(label, options, value, width, on_change=None)` → `ft.Dropdown`
   - `scrollable_table_card(content, height=380, padding=12)` → `ft.Container`
   - `loading_row()` → `LoadingRow` (dataclass carrying `.notice`, `.ring`, `.row`)
3. Replace all inline duplicates in the six feature views and `app.py` with
   imports from `core.components`.
4. Keep `core/ui_helpers.py` unchanged for its existing colour constants and
   atomic helpers; the new package sits alongside it.

---

## Non-Goals

- Do **not** convert any view to `@ft.component` (covered by spec-008).
- Do **not** move `card()`, `stat_badge()`, `build_bar_chart()`, or
  `build_data_table()` — they are already in `ui_helpers.py` and are used
  correctly.
- Do **not** create a design-system theme object — this is a pure copy-reduction
  refactor.

---

## Proposed API

### `page_header(title: str, subtitle: str) -> ft.Column`

```python
# src/core/components/page_header.py
def page_header(title: str, subtitle: str) -> ft.Column:
    return ft.Column([
        ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
        ft.Text(subtitle, size=13, color=TEXT_SECONDARY),
        ft.Divider(color=BORDER_COLOR, height=1),
    ], spacing=4)
```

**Current call sites** (replace inline code):

| File | Current code |
|------|-------------|
| `tournament_view.py` | `ft.Text("🏆 Tournament History", …)` + `ft.Text(…)` + `ft.Divider(…)` |
| `teams_view.py` | same pattern |
| `records_view.py` | same pattern |
| `matches_view.py` | same pattern |
| `schedule_view.py` | same pattern |
| `map_view.py` | same pattern (inside `MapView` component) |
| `osm_map_view.py` | similar (no Divider, but title + subtitle inline) |

---

### `styled_dropdown(label, options, value, width, on_change=None) -> ft.Dropdown`

```python
# src/core/components/styled_dropdown.py
def styled_dropdown(
    label: str,
    options: list[ft.dropdown.Option],
    value: str | None = None,
    width: int = 200,
    on_change: Callable | None = None,
) -> ft.Dropdown:
    return ft.Dropdown(
        label=label,
        options=options,
        value=value,
        width=width,
        bgcolor=BG_CARD,
        color=TEXT_PRIMARY,
        focused_border_color=ACCENT,
        border_color=BORDER_COLOR,
        on_change=on_change,
    )
```

**Current call sites** (7 duplicates):

| File | Variable |
|------|----------|
| `tournament_view.py` | `year_dd` |
| `teams_view.py` | `team1_dd`, `team2_dd` |
| `matches_view.py` | `year_dd`, `stage_dd`, `group_dd` |
| `schedule_view.py` | `group_dd` |

---

### `scrollable_table_card(content, height=380, padding=12) -> ft.Container`

```python
# src/core/components/scrollable_table_card.py
def scrollable_table_card(
    content: ft.Control,
    height: int = 380,
    padding: int = 12,
) -> ft.Container:
    return ft.Container(
        content=ft.Column([content], scroll=ft.ScrollMode.AUTO, expand=True),
        bgcolor=BG_CARD,
        border_radius=8,
        padding=padding,
        height=height,
        border=ft.Border.all(1, BORDER_COLOR),
    )
```

**Current call sites** (2 identical inline blocks):

| File | Context |
|------|---------|
| `matches_view.py` | wraps `table_container`, `height=380` |
| `records_view.py` | wraps `table_container`, `height=380` |

Note: `core/ui_helpers.scrollable_card()` (takes `height=350`) stays in place;
`scrollable_table_card` is the canonical name going forward and views are
migrated to it.

---

### `loading_row() -> LoadingRow`

```python
# src/core/components/loading_row.py
from dataclasses import dataclass

@dataclass
class LoadingRow:
    notice: ft.Text          # empty, hidden initially
    ring: ft.ProgressRing    # hidden initially
    row: ft.Row              # ft.Row([ring], spacing=12) for embedding in layout

def loading_row(extra_controls: list[ft.Control] | None = None) -> LoadingRow:
    notice = ft.Text("", size=12, color=TEXT_SECONDARY, visible=False)
    ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
    row = ft.Row([*(extra_controls or []), ring], spacing=12,
                 vertical_alignment=ft.CrossAxisAlignment.CENTER)
    return LoadingRow(notice=notice, ring=ring, row=row)
```

**Current call sites**:

| File | Pattern replaced |
|------|-----------------|
| `matches_view.py` | `notice = ft.Text(…)` + `loading_ring = ft.ProgressRing(…)` + `ft.Row([year_dd, stage_dd, group_dd, loading_ring], …)` |
| `schedule_view.py` | same two-line construct + `ft.Row([group_dd, loading_ring], …)` |

---

## File Layout After Implementation

```
src/
  core/
    ui_helpers.py          ← unchanged (colours + atomic helpers)
    components/
      __init__.py          ← re-exports all four public symbols
      page_header.py
      styled_dropdown.py
      scrollable_table_card.py
      loading_row.py
```

---

## Acceptance Criteria

1. `src/core/components/` package exists with `__init__.py` that exports
   `page_header`, `styled_dropdown`, `scrollable_table_card`, `loading_row`,
   `LoadingRow`.
2. Each of the six feature view files imports from `core.components` (no
   remaining inline duplicates of the four patterns above).
3. `uv run pytest tests/ -q` → **45 passed** (no regressions).
4. `flet run --web src/main.py` opens without errors and all seven tabs render
   correctly.
5. No colour constants or values are changed by this refactor.

---

## Out-of-Scope / Follow-on

- Spec-010 could apply `@ft.component` to the remaining imperative views now
  that `MapRenderState` is observable.
- `core/ui_helpers.py` consolidation (merge into `core/components`) is deferred.
