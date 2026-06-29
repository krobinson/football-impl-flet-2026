# Feature Specification: Schedule — Country Flags and Venue Population

**Feature Branch**: `014-schedule-flags-venue`  
**Created**: 2026-06-10  
**Status**: Draft  
**Input**: User description: "So the schedule needs work. We need to show flags for each country. The venue needs to be populated."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Country flags beside team names (Priority: P1)

A user viewing the match schedule sees a small flag emoji displayed immediately before each team's name on every match row — both the home team and the away team. At a glance they can identify the competing nations without needing to read the full team names.

**Why this priority**: Visual identification is the most immediately noticeable improvement. Flags are a standard feature of any football schedule and are expected by users familiar with tournament broadcasts.

**Independent Test**: Open the Schedule tab. Each match row shows a flag emoji to the left of the home team name and a flag emoji to the left of the away team name. If a team code cannot be mapped to a flag the name still appears without a flag and no error is thrown.

**Acceptance Scenarios**:

1. **Given** a match row with `homeTeam.tla = "USA"` and `awayTeam.tla = "MEX"`, **When** the row renders, **Then** the home side displays 🇺🇸 before "USA" and the away side displays 🇲🇽 before "Mexico".
2. **Given** a match row with a recognised team code, **When** the row renders, **Then** the flag emoji precedes the team name with a single space separator.
3. **Given** a match row with a missing or unrecognised team code, **When** the row renders, **Then** only the team name is shown — no flag, no placeholder character, no error.
4. **Given** the header row, **When** it renders, **Then** the "Home" and "Away" column headers are unchanged — flags only appear in data rows.

---

### User Story 2 — Venue column always populated (Priority: P2)

A user viewing the match schedule sees the stadium name in the Venue column for every match. Previously many rows showed "TBD" because the football-data.org API does not always populate the `venue` field. The venue is now resolved from local fixture data when the API field is absent, so every match shows a meaningful venue name.

**Why this priority**: A "TBD" venue degrades the usefulness of the schedule. With all 16 host stadiums known and fully assigned to matches, there is no reason for the column to be empty.

**Independent Test**: Open the Schedule tab. Every match row in the Venue column shows a stadium name (e.g. "MetLife Stadium", "SoFi Stadium"). No row shows "TBD" or a blank value. Rows where the API provides a venue directly use that value; rows where the API returns null fall back to the locally-derived venue.

**Acceptance Scenarios**:

1. **Given** the API returns a non-null `venue` string for a match, **When** the row renders, **Then** that venue string is displayed in the Venue column.
2. **Given** the API returns `null` for `venue`, **When** the row renders, **Then** the Venue column shows the stadium name resolved from local 2026 fixture data.
3. **Given** a match whose venue cannot be resolved from either the API or local data, **When** the row renders, **Then** the Venue column shows "TBD" (graceful fallback — not an error).
4. **Given** the local fixture data maps a match by home team + matchday to a known city, **When** the venue is resolved, **Then** the displayed name is the full stadium name for that city (not the city name alone).

---

### Edge Cases

- What if `homeTeam` or `awayTeam` is null/missing in the API response? The team name already defaults to "TBD"; the flag should simply be omitted without error.
- What if a team has a TLA that is a valid 3-letter code but has no corresponding flag mapping (e.g. "TBD", "N/A")? Show only the name — no broken characters.
- What if two local fixture rows match the same home team + matchday? Use the first match found; log a warning. This should not happen in a correctly structured 2026 fixture list.
- What if the schedule tab loads before the API response arrives? Venue resolution applies at render time; already-rendered rows are not retroactively updated (the full list is re-rendered on each data load, so this is naturally handled).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each match row MUST display a flag emoji immediately before the home team name.
- **FR-002**: Each match row MUST display a flag emoji immediately before the away team name.
- **FR-003**: Flag resolution MUST use the team's `tla` field (`homeTeam.tla` / `awayTeam.tla`) as the primary lookup key.
- **FR-004**: If `tla` is absent, null, or unmappable, the team name MUST be shown without a flag and without raising an error.
- **FR-005**: The Venue column MUST display a stadium name for every match row; "TBD" is only acceptable when both the API `venue` field and the local fallback lookup return no result.
- **FR-006**: Venue resolution MUST first use the API-provided `venue` field; if null or empty it MUST fall back to local 2026 fixture data matched by home team name and matchday number.
- **FR-007**: The local fallback MUST resolve the city to a full stadium name using the existing city-to-stadium mapping already present in the codebase.
- **FR-008**: The flag mapping table and venue fallback logic MUST be implemented as independently testable pure functions, separate from rendering code.
- **FR-009**: All existing schedule tests MUST continue to pass; new tests MUST cover flag lookup and venue fallback.

### Key Entities

- **Match row**: Extended to carry a flag emoji prefix on each team name and a resolved venue string.
- **TLA → flag map**: Static dict mapping FIFA 3-letter team codes to Unicode flag emoji. Covers all 48 qualified nations for 2026 plus common edge-case codes.
- **Local venue fallback**: Index built from the local 2026 fixture data, keyed by home team name + matchday → city → full stadium name via the city-to-stadium map.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every match row in the rendered schedule displays a flag emoji for both teams — verifiable by visual inspection across all 48 group-stage matches.
- **SC-002**: Zero match rows show "TBD" in the Venue column when the live API key is set and the schedule is loaded — verifiable by inspection.
- **SC-003**: 100% of existing automated tests (currently 143) continue to pass after the change.
- **SC-004**: New unit tests covering flag lookup (including unmappable codes) and venue fallback (API null path and local path) are added and pass.
- **SC-005**: The schedule tab renders without any new runtime errors or console warnings related to flags or venue resolution.

---

## Assumptions

- The football-data.org API returns `homeTeam.tla` and `awayTeam.tla` on each match object for the 2026 World Cup competition. If the API does not provide `tla`, team `shortName` or `name` may be used as a secondary source, but this path is not the primary one.
- The 2026 World Cup has 48 participating nations with well-known FIFA TLA codes. A hand-curated TLA → flag emoji map covering all 48 is feasible and maintainable.
- `data/worldcup/2026/worldcup.json` contains all 48 group-stage matches with `team1`, `round` (matchday), and `ground` (city) fields populated. This is confirmed by inspection.
- The `VENUES` list in `src/core/venue_data.py` contains all 16 host stadiums; the city → stadium lookup is unambiguous for all 16 host cities.
- The flag emoji rendering works correctly in Flet's `ft.Text` widget on both desktop and web targets (Unicode emoji support is standard on all supported platforms).
- The header row columns ("Home", "Away", "Venue") do not require any change; only data row content changes.
