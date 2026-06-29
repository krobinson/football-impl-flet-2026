# Research: Group Stage Match Details via URL Data Source

**Feature**: 016-group-stage-match-details  
**Date**: 2026-06-28

---

## Decision 1 — Data Fetching: urllib.request, not new dependency

**Decision**: Use `urllib.request` (stdlib) to fetch the worldcup.json URL, consistent with the existing `FootballDataClient` in `core/network.py` which already uses `urllib.request`.

**Rationale**: Constitution V (YAGNI) and the technology stack constraint ("No runtime dependency outside this list may be introduced without a constitution amendment"). The project already uses `urllib.request` for HTTP. Adding `requests` or `httpx` would violate the stack constraint.

**Alternatives considered**:
- `requests` library — would require adding a new dependency; constitution prohibits this without amendment.
- `httpx` — same issue as requests.
- `aiohttp` — async not needed for a single JSON fetch; adds complexity.

---

## Decision 2 — Data Transformation: Normalize to existing dict shape

**Decision**: Create a `transform_match()` function that converts URL format dicts (`team1`, `team2`, `date`, `time`, `group`, `ground`) into the same dict shape the existing `match_row()` expects (`homeTeam.name`, `awayTeam.name`, `utcDate`, `group`, `venue`, `status`, `matchday`).

**Rationale**: The existing `match_row()` in `src/features/schedule/components/match_row.py` already handles all display logic (status badges, score formatting, UTC time parsing, group colour, flag emoji). By transforming URL data to match the expected shape, we reuse 100% of the rendering code. Creating a parallel rendering path would violate YAGNI and double the maintenance surface.

**Alternatives considered**:
- Create a new `url_match_row()` component — duplicates rendering logic; violates DRY/YAGNI.
- Modify `match_row()` to handle both formats with conditionals — increases complexity in a working component; harder to test.
- Transform data to API shape (chosen) — single transformation point; existing rendering works unchanged.

---

## Decision 3 — Service Location: `src/features/schedule/services/`

**Decision**: Place the new `WorldCupJsonService` in `src/features/schedule/services/worldcup_json_service.py`.

**Rationale**: Constitution II (Feature-Module Separation) requires feature-specific logic to live under its feature module. The URL data service is specific to the schedule feature. Shared utilities (if any) go in `src/core/`.

**Alternatives considered**:
- Place in `src/core/` — this is schedule-specific data loading, not shared infrastructure.
- Place in `src/services/` — no such directory exists; the project uses per-feature `services/` subdirectories.

---

## Decision 4 — Fallback Strategy: URL → local file → error

**Decision**: Three-tier fallback: (1) fetch from URL, (2) on failure load `data/worldcup/2026/worldcup.json`, (3) on failure show error message.

**Rationale**: The spec requires offline capability (edge case: no internet). The local file is already bundled in the repo and contains the same data. This ensures the schedule is always available regardless of network status.

**Alternatives considered**:
- URL only, no fallback — fails when offline; violates FR-002 and edge case requirement.
- Local file only, no URL — does not satisfy FR-001 (MUST fetch from URL).
- Cache URL response locally — adds complexity (file I/O, cache invalidation) without clear benefit for static tournament data.

---

## Decision 5 — Group Key Normalization: "Group A" → "GROUP_A"

**Decision**: Transform the URL format group string ("Group A") to the API format ("GROUP_A") during data normalization, so the existing group chip filtering logic (`m.get("group") == f"GROUP_{sel}"`) works unchanged.

**Rationale**: The existing `_apply_group_filter()` in `schedule_view.py` filters by `"GROUP_A"` format. Transforming at load time means zero changes to the filtering logic.

**Alternatives considered**:
- Change filter logic to handle "Group A" format — requires modifying working filter code; introduces format-dependent branching.
- Store both formats — unnecessary duplication.

---

## Decision 6 — Date/Time Synthesis: Combine `date` + `time` into `utcDate`

**Decision**: Synthesize an ISO-8601 `utcDate` string from the URL data's separate `date` ("2026-06-11") and `time` ("13:00 UTC-6") fields. Parse the UTC offset from the time string and construct a timezone-aware datetime, then format as ISO-8601 with "Z" suffix (converting to UTC).

**Rationale**: The existing `_fmt_utc()` function in `match_row.py` parses ISO-8601 strings with `datetime.fromisoformat()`. By synthesizing a compatible string, the existing time display logic works unchanged.

**Alternatives considered**:
- Modify `_fmt_utc()` to handle the URL format directly — adds format-specific branching to a working function.
- Display date and time as separate strings — would require changing the match_row layout.
- Synthesize ISO-8601 (chosen) — single transformation point; existing parsing works.

---

## Decision 7 — Team Flags: Omit for URL data (no TLA codes available)

**Decision**: URL data provides team names as strings but no FIFA 3-letter codes (TLA). The `tla_to_flag()` function in `match_row.py` already returns empty string for unknown/missing TLA. Transformed data will have no `tla` field, so flags are naturally omitted.

**Rationale**: The URL data schema does not include TLA codes. Adding a manual mapping would be brittle and require maintenance. The existing code handles missing TLA gracefully (no flag shown). This is acceptable for a URL-sourced fallback.

**Alternatives considered**:
- Build a team name → TLA mapping — adds maintenance burden; team names in URL data may not match exactly.
- Show text-based country codes instead of flags — inconsistent with API-sourced display.

---

## Decision 8 — Matchday Extraction: Parse numeric suffix from round string

**Decision**: Extract the matchday number from the URL data's `round` field (e.g., "Matchday 1" → 1, "Matchday 8" → 8). For knockout rounds that lack a matchday number, assign a high sort value (99) so they sort after group stage matches.

**Rationale**: The existing sort uses `match.get("matchday") or 99`. The URL data uses "Matchday N" format. Simple string parsing extracts the number. Since we filter to group stage only (FR-003), knockout rounds are excluded anyway, but the extraction function should be robust.

**Alternatives considered**:
- Use round string directly for sorting — alphabetical sort of "Matchday 1", "Matchday 14", "Matchday 8" gives wrong order.
- Assign sequential matchday numbers based on date order — unnecessary complexity when the round string already contains the number.
