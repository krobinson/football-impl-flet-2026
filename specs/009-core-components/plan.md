# Implementation Plan: Core UI Component Library

**Branch**: `009-core-components` | **Date**: 2026-05-24 | **Spec**: [spec.md](spec.md)

---

## Summary

Extract four structural UI patterns that are copy-pasted across the six feature
views into a `src/core/components/` package.  Each pattern becomes a small
factory function.  All feature view files are then updated to import from
`core.components` instead of inlining the same boilerplate.

This is a **pure refactor**: no behaviour changes, no new features, no widget
style property changes.  The only test gate is that all 45 existing tests keep
passing and every tab still renders in the app.

---

## Technical Context

| Item | Value |
|------|-------|
| Language | Python 3.13 |
| Flet version | `flet==0.84.0` |
| Runner | `uv run flet run src/main.py` |
| Tests | `uv run pytest tests/ -q` → must stay 45 passed |
| Entry point | `src/main.py` → `src/app.py` |
| Existing helpers | `src/core/ui_helpers.py` — colours + atomic helpers (unchanged) |
| Target views | all 6 feature view files + `app.py` (map header) |

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Flet-First UI | ✅ PASS | Components return plain Flet controls; no new dependencies |
| Feature-Module Separation | ✅ PASS | Only `core/` gains new files; feature views import from core, not from each other |
| Test-First | ✅ PASS | `tests/unit/test_core_components.py` written before view migration |
| API-Backed Data Layer | ✅ PASS | No data layer touched |
| Simplicity & YAGNI | ✅ PASS | Exactly four components; no theme system, no generalised component registry |

---

## Project Structure After Implementation

```
src/
  core/
    ui_helpers.py                    ← unchanged
    components/
      __init__.py                    ← exports: page_header, styled_dropdown,
      │                                          scrollable_table_card,
      │                                          loading_row, LoadingRow
      page_header.py
      styled_dropdown.py
      scrollable_table_card.py
      loading_row.py
  features/
    map/views/map_view.py            ← page_header (title+subtitle inside MapView)
    tournament/views/tournament_view.py   ← page_header, styled_dropdown
    teams/views/teams_view.py             ← page_header, styled_dropdown (×2)
    matches/views/matches_view.py         ← page_header, styled_dropdown (×3),
    │                                        scrollable_table_card, loading_row
    records/views/records_view.py         ← page_header, scrollable_table_card
    schedule/views/schedule_view.py       ← page_header, styled_dropdown, loading_row
    venues/views/osm_map_view.py          ← page_header (no Divider variant)

tests/
  unit/
    test_core_components.py          ← new, 4 smoke tests

specs/
  009-core-components/
    plan.md   ← this file
    spec.md
```

---

## Component Designs

### 1 · `page_header(title, subtitle, divider=True)`

Returns `ft.Column` wrapping a bold 22 px title, 13 px subtitle, and an
optional `ft.Divider`.

```python
def page_header(title: str, subtitle: str, *, divider: bool = True) -> ft.Column:
    controls: list[ft.Control] = [
        ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
        ft.Text(subtitle, size=13, color=TEXT_SECONDARY),
    ]
    if divider:
        controls.append(ft.Divider(color=BORDER_COLOR, height=1))
    return ft.Column(controls, spacing=4)
```

`divider=False` handles `osm_map_view.py` which omits the rule.

---

### 2 · `styled_dropdown(label, options, value, width, on_change=None)`

Returns `ft.Dropdown` with the project's standard colour props pre-applied.

```python
def styled_dropdown(
    label: str,
    options: list[ft.dropdown.Option],
    value: str | None = None,
    width: int = 200,
    on_change: Callable | None = None,
) -> ft.Dropdown:
    return ft.Dropdown(
        label=label, options=options, value=value, width=width,
        on_change=on_change,
        bgcolor=BG_CARD, color=TEXT_PRIMARY,
        focused_border_color=ACCENT, border_color=BORDER_COLOR,
    )
```

---

### 3 · `scrollable_table_card(content, height=380, padding=12)`

Returns the standard bordered, scrollable card used for data tables.

```python
def scrollable_table_card(
    content: ft.Control,
    height: int = 380,
    padding: int = 12,
) -> ft.Container:
    return ft.Container(
        content=ft.Column([content], scroll=ft.ScrollMode.AUTO, expand=True),
        bgcolor=BG_CARD, border_radius=8, padding=padding, height=height,
        border=ft.Border.all(1, BORDER_COLOR),
    )
```

---

### 4 · `loading_row(prefix_controls=None)` → `LoadingRow`

Factory returns a `LoadingRow` dataclass whose `.notice`, `.ring`, and `.row`
are all the caller needs to embed in their layout and manipulate.

```python
@dataclass
class LoadingRow:
    notice: ft.Text
    ring:   ft.ProgressRing
    row:    ft.Row          # embed in layout; contains ring + any prefix controls

def loading_row(
    prefix_controls: list[ft.Control] | None = None,
) -> LoadingRow:
    notice = ft.Text("", size=12, color=TEXT_SECONDARY, visible=False)
    ring   = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
    row    = ft.Row(
        [*(prefix_controls or []), ring],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return LoadingRow(notice=notice, ring=ring, row=row)
```

Callers in `matches_view` and `schedule_view` embed `lr.row` in their layout,
place `lr.notice` below it, and toggle `lr.ring.visible`/`lr.notice.value`
in background threads — identical to the current inline code.

---

## Phases & Steps

### Phase 1 — Create `core/components/` package (no view changes yet)

**Step 1.1** — Create directory and four module files + `__init__.py`.  
Run: `uv run pytest tests/ -q` → 45 passed (no regressions from adding files).

**Step 1.2** — Write `tests/unit/test_core_components.py`:
- `test_page_header_returns_column` — assert result is `ft.Column`, first child is `ft.Text`
- `test_page_header_no_divider` — `divider=False` omits `ft.Divider`
- `test_styled_dropdown_returns_dropdown` — assert result is `ft.Dropdown`, `bgcolor == BG_CARD`
- `test_scrollable_table_card_returns_container` — assert `ft.Container`, has scroll-wrapped child
- `test_loading_row_fields` — `LoadingRow.ring` is hidden, `LoadingRow.notice` is hidden

Run: `uv run pytest tests/unit/test_core_components.py -q` → 5 passed.  
Run: `uv run pytest tests/ -q` → 50 passed.

---

### Phase 2 — Migrate feature views (parallel within phase)

All five steps can be executed in parallel (different files, no shared edits).

**Step 2.1** — `tournament_view.py`  
Replace: inline title/subtitle/Divider → `page_header(…)`.  
Replace: `year_dd = ft.Dropdown(label=…, bgcolor=BG_CARD, …)` → `styled_dropdown(…)`.  
Remove now-unused `BG_PAGE` import if only used for the dropdown.

**Step 2.2** — `teams_view.py`  
Replace: inline title/subtitle/Divider → `page_header(…)`.  
Replace: `team1_dd` and `team2_dd` → `styled_dropdown(…)`.

**Step 2.3** — `matches_view.py`  
Replace: inline title/subtitle/Divider → `page_header(…)`.  
Replace: `year_dd`, `stage_dd`, `group_dd` → `styled_dropdown(…)`.  
Replace: scrollable table `ft.Container` block → `scrollable_table_card(table_container)`.  
Replace: `notice`/`loading_ring` inline creation + `ft.Row([…loading_ring], …)` → `lr = loading_row([year_dd, stage_dd, group_dd])`.  Use `lr.notice`, `lr.ring`, `lr.row`.

**Step 2.4** — `records_view.py`  
Replace: inline title/subtitle/Divider → `page_header(…)`.  
Replace: scrollable table `ft.Container` block → `scrollable_table_card(table_container, height=380)`.

**Step 2.5** — `schedule_view.py`  
Replace: inline title/subtitle/Divider → `page_header(…)`.  
Replace: `group_dd = ft.Dropdown(…)` → `styled_dropdown(…)`.  
Replace: `notice`/`loading_ring` inline creation + `ft.Row([group_dd, loading_ring], …)` → `lr = loading_row([group_dd])`.

Run after all five: `uv run pytest tests/ -q` → 50 passed.

---

### Phase 3 — Migrate remaining views

**Step 3.1** — `map_view.py` (inside `MapView` `@ft.component`)  
Replace: inline `ft.Text(title, …)` + `ft.Text(subtitle, …)` at top of returned `ft.Column` → `page_header("FIFA World Cup 2026", "48 qualifying nations — click a country")`.  
Note: `page_header` returns a `ft.Column`; embed it as the first element of the outer `ft.Column.controls` or spread its children — spreading is cleaner to match current spacing.

**Step 3.2** — `osm_map_view.py`  
Replace: inline `ft.Text("FIFA World Cup 2026 — Host Venues", …)` → `page_header(…, divider=False)`.  
`divider=False` because the venue map has no `ft.Divider` in its current layout.

Run: `uv run pytest tests/ -q` → 50 passed.

---

### Phase 4 — Cleanup & verification

**Step 4.1** — Remove now-unused symbols from feature view imports:
- Trim `BG_PAGE` from any view where it is no longer used after dropdown migration.
- Ensure no feature view still has the old inline dropdown/header/table boilerplate.

**Step 4.2** — Final test run: `uv run pytest tests/ -q` → **50 passed**.

**Step 4.3** — Manual smoke-check: `flet run --web src/main.py` — open all seven
tabs and verify headers, dropdowns, tables, spinners all render correctly.

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| `osm_map_view` header uses no Divider — `page_header` must support `divider=False` | Low | `divider` keyword arg with `True` default, `False` for venues view |
| `loading_row` callers use `lr.ring.visible` / `lr.notice.value` in threads — same pattern, just renamed | Low | Names identical to current `loading_ring`/`notice`; rename in one step per file |
| `map_view.py` uses `@ft.component` — `page_header` returns a `ft.Column` placed inside another `ft.Column` | Low | Spread children into outer list (`*page_header(…).controls`) or just nest; either is valid in Flet |

---

## Definition of Done

- [ ] `src/core/components/` package with 4 modules + `__init__.py` exists
- [ ] `tests/unit/test_core_components.py` with ≥ 5 tests, all passing
- [ ] All 6 feature views + `map_view.py` import from `core.components`
- [ ] No inline duplicate of any of the four patterns remains
- [ ] `uv run pytest tests/ -q` → **50 passed**
- [ ] App loads without errors; all tabs render
