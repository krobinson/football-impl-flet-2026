# Research: Team Tournament Progression

## Summary of Findings

All NEEDS CLARIFICATION items resolved. No external research required — all
decisions derive from the existing codebase.

---

## Decision 1: Data Source

**Decision**: Use `store.matches` DataFrame (already loaded by `DataStore`).  
**Rationale**: The DataFrame is populated from `data/worldcup/<year>/worldcup.json`
for every edition 1930–2022. It already contains the `stage` column (the raw
`round` field from JSON) plus `home_team`, `away_team`, `home_score`,
`away_score`, `aet`, `et_home`, `et_away`, `pen_home`, `pen_away`. No additional
data loading is needed.  
**Alternatives considered**: Adding a separate service that re-parses JSON files
each time — rejected (DataStore already does this; duplicating it violates YAGNI).

---

## Decision 2: Round Ordering

**Decision**: Define a canonical round order list and sort `stage` values against it.
Stages not in the list are treated as group-stage matchdays and sorted
lexicographically before the knockout rounds.  
**Rationale**: The 2022 data shows these round name values (confirmed by inspection):
`Matchday 1`–`Matchday 13` (group stage), `Round of 16`, `Quarter-finals`,
`Semi-finals`, `Match for third place`, `Final`. Older editions use fewer rounds
(e.g. 1930/1950 had no knockout binary tree). Sorting by a fixed priority list
correctly handles both.  
**Canonical order** (ascending priority integer):
```
Matchday * (group stage) → Round of 16 → Quarter-finals → Semi-finals →
  Match for third place / Third place match → Final
```
**Alternatives considered**: Sorting by `date` — rejected because some editions
have incomplete or missing date fields in older JSON files.

---

## Decision 3: Progression Service Function

**Decision**: Add a pure function `get_team_progression(matches_df, year, team=None)`
in a new `src/features/tournament/services.py` file. Returns a list of
`(round_name, [MatchRow])` tuples ordered by round priority.  
**Rationale**: Keeps the UI layer (`tournament_view.py`) free of query logic;
pure function is trivially unit-testable without a Flet page (satisfies
constitution III — Test-First).  
**Alternatives considered**: Inline logic in the view — rejected (mixes concerns,
untestable in isolation).

---

## Decision 4: Team Filter UI

**Decision**: Add a `styled_dropdown` (already available in `core.components`)
for team selection beneath the year selector. Default value = "All Teams".  
**Rationale**: Consistent with the existing year selector pattern; no new UI
primitives required.  
**Alternatives considered**: Text-input autocomplete — rejected (overkill for a list
of max 32 teams; adds complexity without added value).

---

## Decision 5: Progression Panel Component

**Decision**: Build the progression panel as a `ft.Column` of expandable
`ft.ExpansionTile` sections, one per round. Each tile shows the round name in
the header and lists matches inside.  
**Rationale**: `ft.ExpansionTile` is standard Flet ≥ 0.84; allows all rounds to be
visible at a glance while keeping vertical space manageable.  
**Alternatives considered**: Flat scrolling list of all matches — acceptable but
harder to scan; bracket diagram — out of scope (requires custom Canvas work),
deferred to a future spec.

---

## Decision 6: Feature Module Boundary

**Decision**: The progression service lives in
`src/features/tournament/services.py` (new file). The view remains in
`src/features/tournament/views/tournament_view.py` (modified in-place). No new
feature module is created.  
**Rationale**: Progression is a sub-concern of the existing tournament feature
domain. Constitution II says shared logic belongs in `src/shared/`; logic private
to the tournament feature belongs in its own module.  
**Alternatives considered**: Adding to `DataStore` — rejected (DataStore is a
cross-feature service; tournament-specific query logic doesn't belong there).

---

## Resolved Clarifications

| # | Question | Answer |
|---|----------|--------|
| 1 | Does `store.matches` cover all editions? | Yes — all years 1930–2022 are loaded; 2026 is explicitly excluded (year ≥ 2026 check). |
| 2 | How is "group stage" detected? | `stage` field starts with "Matchday". |
| 3 | Are scores always integers? | `ft` array is `[int, int]`; already cast to `int` in `_parse_year`. |
| 4 | Does DataStore expose matches publicly? | Yes — `store.matches` is a public `pd.DataFrame`. |
| 5 | Is `styled_dropdown` available? | Yes — `core.components.styled_dropdown`. |
