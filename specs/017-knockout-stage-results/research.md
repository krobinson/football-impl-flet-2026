# Research: Knockout Stage Results & Live Scores

**Feature**: 017-knockout-stage-results  
**Date**: 2026-07-04

---

## Decision 1 — Include Knockout Matches: Remove group-only filter

**Decision**: Remove the `is_group_stage()` filter from `WorldCupJsonService.get_group_matches()` (or rename to `get_all_matches()`) so that all 104 matches (group + knockout) are returned.

**Rationale**: The spec requires displaying knockout matches alongside group stage matches. The existing filter explicitly excludes them. Removing it is the simplest approach — the data already contains all matches.

**Alternatives considered**:
- Add a separate method `get_knockout_matches()` and merge results — adds unnecessary API surface; violates YAGNI.
- Keep the filter and add a parameter to toggle it — adds complexity for a one-time change.

---

## Decision 2 — Stage Classification: Derive from `round` and `group` fields

**Decision**: Add a `stage` field to the transformed match dict, derived as follows:
- If `group` field exists and matches "Group [A-L]" → `"GROUP_STAGE"`
- If `round` is "Round of 32" → `"ROUND_OF_32"`
- If `round` is "Round of 16" → `"ROUND_OF_16"`
- If `round` is "Quarter-final" → `"QUARTER_FINAL"`
- If `round` is "Semi-final" → `"SEMI_FINAL"`
- If `round` is "Final" or "Match for third place" → `"FINAL"`

**Rationale**: The URL data uses `round` for knockout stages and `group` for group stage. A normalized `stage` field allows simple equality filtering in the view layer. Grouping "Match for third place" under "FINAL" keeps the chip count manageable (7 chips total).

**Alternatives considered**:
- Use the raw `round` string for filtering — fragile, requires string matching in the view; "Match for third place" would need special handling.
- Create a separate "Third Place" stage chip — adds a chip for a single match; poor UX.

---

## Decision 3 — Round Display Name: Short labels for knockout matches

**Decision**: Add a `round_display` field to the transformed match dict:
- Group stage → `""` (empty, group letter is shown instead)
- Round of 32 → `"R32"`
- Round of 16 → `"R16"`
- Quarter-final → `"QF"`
- Semi-final → `"SF"`
- Final → `"F"`
- Match for third place → `"3rd"`

**Rationale**: The Group column in match_row is 55px wide. Short labels fit without truncation. Full names ("Round of 32") are too long for the column width.

**Alternatives considered**:
- Use full round names ("Round of 32") — too long for 55px column; would require wider column or truncation.
- Abbreviate differently ("Ro32", "Qtr") — non-standard; "R32", "QF" are widely understood in football context.

---

## Decision 4 — Stage Chips: New component, reuse chip pattern

**Decision**: Create a new `stage_chips.py` component that reuses the exact same chip styling from `_build_group_chips()` in `schedule_view.py`. The stage chips are: All, Group Stage, R32, R16, QF, SF, Final.

**Rationale**: Visual consistency with existing group chips. The chip pattern is already established (rounded container, active/inactive colours). Extracting it to a shared component avoids duplication.

**Alternatives considered**:
- Inline the stage chips in schedule_view.py — duplicates chip-building logic; harder to test.
- Use a dropdown instead of chips — inconsistent with existing group chip UX; more clicks to select.

---

## Decision 5 — Conditional Group Chips: Hide when non-group stage selected

**Decision**: When any stage other than "Group Stage" or "All" is selected, hide the group letter chips row. When "Group Stage" is selected, show both stage chips and group chips. When "All" is selected, hide group chips (since group filtering doesn't apply to knockout matches).

**Rationale**: Group chips only make sense for group stage matches. Showing them when viewing knockout matches is confusing and wastes screen space. The simplest rule: group chips visible only when "Group Stage" is the active stage filter.

**Alternatives considered**:
- Always show group chips, disable them for non-group stages — visually cluttered; disabled state is unclear.
- Show group chips when "All" is selected too — group filter would only apply to group matches within "All", which is confusing UX.

---

## Decision 6 — Score Display: Existing logic already handles knockout scores

**Decision**: No changes needed to `_score_text()` or status badge logic. The existing `transform_match()` already converts `score.ft` to `score.fullTime` format, and `_score_text()` already handles both scored and unscored matches. The status derivation (`"FINISHED"` if score exists, `"SCHEDULED"` otherwise) also works for knockout matches.

**Rationale**: The URL data uses the same `score.ft` format for both group and knockout matches. The existing transformation and rendering code is format-agnostic.

**Alternatives considered**:
- Add knockout-specific score display (e.g., show penalties) — out of scope per spec; adds complexity.

---

## Decision 7 — Backward Compatibility: Keep `get_group_matches()` method

**Decision**: Keep the existing `get_group_matches()` method for backward compatibility but add a new `get_all_matches()` method that returns all 104 matches. The schedule view will call `get_all_matches()`.

**Rationale**: Other parts of the codebase or tests may depend on `get_group_matches()`. Adding a new method is safer than modifying the existing one. The new method shares the same fetch/transform pipeline but skips the group filter.

**Alternatives considered**:
- Modify `get_group_matches()` to return all matches — breaks the method's contract; may break existing callers.
- Add a boolean parameter `include_knockout=False` — works but less clear than a dedicated method name.

---

## Decision 8 — Local File Update: Sync data/worldcup/2026/worldcup.json

**Decision**: Update the local fallback file to include the latest scores from the URL. This is a data update, not a code change.

**Rationale**: FR-010 requires the local file to include current scores so offline users see results. The file is already bundled in the repo.

**Alternatives considered**:
- Auto-sync the local file on each URL fetch — adds file I/O complexity; the data is semi-static and can be updated manually.
