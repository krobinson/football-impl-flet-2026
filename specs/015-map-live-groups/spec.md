# Feature Specification: World Map — Live Group Stage Draw

**Feature Branch**: `015-map-live-groups`  
**Created**: 2026-06-14  
**Status**: Draft  
**Input**: User description: "What i found with the pages is the group stages A to L are incorrect on the 2026 world map. These details need to be taken from the realt time data URL prior to building the map."

---

## Background

The 2026 World Cup map colours each participating country by its assigned group (A–L). The group assignments are currently read from a static data file that contains a placeholder/speculative draw — not the official FIFA draw. As a result, almost every country is shown in the wrong group. The official draw is available from the live football-data.org API, which is already used by the Schedule tab. The map must use this authoritative source.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Map shows the correct official group for every country (Priority: P1)

A user opens the 2026 Map tab and sees each of the 48 participating countries coloured and labelled with their **correct** assigned group (A–L) from the official 2026 FIFA World Cup draw. The group filter row correctly lists the teams in each group. Clicking a group chip highlights only the countries in that group.

**Why this priority**: This is the core bug. With nearly all groups wrong, the map is misleading and unusable for its primary purpose. No other map work has value until the group data is correct.

**Independent Test**: Open the 2026 Map tab. Click the "Group D" chip. The map highlights the four countries assigned to Group D by the official draw. Verify against the [official FIFA group page](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/groups). No country should be highlighted in a group other than its official one.

**Acceptance Scenarios**:

1. **Given** the app opens with a valid API key, **When** the 2026 Map tab renders, **Then** each of the 48 countries is assigned to the group it holds in the official 2026 FIFA draw.
2. **Given** the user clicks the "Group D" chip on the map, **When** the filter applies, **Then** exactly the four countries in official Group D are highlighted.
3. **Given** any group chip A–L is selected, **When** the filter applies, **Then** exactly 4 countries are highlighted (every group in 2026 has 4 teams).
4. **Given** the map loads with live data, **When** it is displayed, **Then** the group colour legend matches the actual group colouring — no country appears in a different colour than its chip.
5. **Given** the country info panel is shown for a selected country, **When** the user reads it, **Then** the group label shown matches the official assigned group.

---

### User Story 2 — Graceful fallback when live group data is unavailable (Priority: P2)

A user opens the app without an API key set, or when the API is temporarily unreachable. The map still renders using the static data, but a clearly visible warning banner explains that the group assignments shown may not reflect the official draw and instructs the user to set the API key.

**Why this priority**: The map must always render — the app should never be broken. But users need to know the data may be wrong so they are not misled.

**Independent Test**: Run the app without setting `FOOTBALL_DATA_API_KEY`. Open the 2026 Map tab. The map renders (no crash, no blank screen). A warning message is visible stating that live group data could not be loaded and that the displayed groups may be approximate.

**Acceptance Scenarios**:

1. **Given** no API key is configured, **When** the map tab opens, **Then** the map renders using the static group data.
2. **Given** no API key is configured, **When** the map renders, **Then** a visible warning notice informs the user that group assignments may not be accurate.
3. **Given** the API returns an error (network failure or rate-limit), **When** the map renders, **Then** the same fallback behaviour applies — static data is shown with a warning.
4. **Given** live data loads successfully on a subsequent app open, **When** the map renders, **Then** the warning is not shown and the correct groups are displayed.

---

### Edge Cases

- What if the live API returns matches where a team's code does not match any entry in the local 48-team list? That team's group is left unchanged from the static data and a warning is logged. The map does not crash.
- What if the live API returns fewer than 12 groups or more than 4 teams per group? This would indicate an unexpected API response; use the static fallback and log a warning.
- What if the app has no internet access? Covered by US2 fallback — static data is used with a warning notice.
- What if the group data fetch is slow? The map must render immediately with the static data and silently update (re-render) once the live data arrives. The map must not block the UI thread.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: At app startup, the 2026 Map MUST attempt to fetch the official group draw from the live football-data.org API before displaying group-coloured countries.
- **FR-002**: The group assignments shown on the map MUST match the official 2026 FIFA World Cup draw when live data is successfully fetched.
- **FR-003**: The live group data fetch MUST NOT block the UI — the map MUST render immediately and update in place when the data arrives.
- **FR-004**: If live group data cannot be fetched (no API key, network error, rate-limit), the map MUST fall back to the static group data and display a warning notice to the user.
- **FR-005**: The warning notice (US2) MUST be dismissible or disappear automatically when live data loads successfully.
- **FR-006**: The group filter chips (A–L) MUST reflect the live group assignments — clicking "Group D" MUST highlight the four countries officially in Group D.
- **FR-007**: The country info panel MUST show the correct group letter from the live data once it has loaded.
- **FR-008**: The group draw fetch MUST reuse the existing data-fetching infrastructure already in place for the Schedule tab — no additional rate-limit bypasses, duplicate network connections, or redundant API calls are permitted.

### Key Entities

- **Group draw**: The authoritative mapping of team → group (A–L) for all 48 nations, sourced from the live API and used to override the static data at render time.
- **GroupOverride**: A dict mapping team identifier → group letter, derived from live API matches and applied to the map service before rendering.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a valid API key is set, all 48 countries on the map are in their correct official group — verifiable against the official FIFA draw published on fifa.com.
- **SC-002**: Zero countries appear in a mismatched group colour when live data is loaded — verifiable by inspection of each group chip filter.
- **SC-003**: The map renders within the same time it did before this change when no API key is set (fallback path adds no render delay).
- **SC-004**: When live data is unavailable, the warning notice is visible without the user needing to scroll or interact.
- **SC-005**: 100% of existing automated tests continue to pass; new tests cover the group override path and the fallback path.

---

## Assumptions

- The football-data.org API `GET /competitions/WC/matches?stage=GROUP_STAGE&season=2026` endpoint returns match objects with `homeTeam.tla`, `awayTeam.tla`, and `group` (e.g. `"GROUP_D"`) fields populated for the 2026 season. This is consistent with what the Schedule tab already uses.
- The team TLA codes returned by the API (e.g. `"USA"`, `"MEX"`) correspond 1-to-1 with the ISO-A3 codes already stored in the 48-team static list. Where they differ (e.g. `"GER"` vs `"DEU"`), the existing alias map in the map service already handles the mapping.
- The group draw is stable — once the official draw is published and the tournament has started, group assignments do not change. The cached API response (with the existing cache TTL) is therefore appropriate for this data.
- The map service already supports loading team data from the static JSON; this feature extends it to accept an optional group-override dict at runtime without altering the static asset.
- No changes are required to the GeoJSON boundary data, the map rendering engine, or the group colour palette — only the group letter assigned to each team changes.
