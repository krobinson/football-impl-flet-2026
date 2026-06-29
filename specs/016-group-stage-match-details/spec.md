# Feature Specification: Group Stage Match Details via URL Data Source

**Feature Branch**: `016-group-stage-match-details`  
**Created**: 2026-06-28  
**Status**: Draft  
**Input**: User description: "Please give me the details of each match in each group stage using the URL specifying the football world cup data"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View all group stage matches from URL data (Priority: P1)

A user opens the Schedule tab and sees all 48 group stage matches (Groups A through L) loaded from the openfootball worldcup.json URL. Each match displays the two teams, date, kick-off time, group letter, and venue. The data loads without requiring an API key, making the schedule immediately accessible to all users.

**Why this priority**: This is the core requirement. Without loading match data from the URL, no other functionality is possible. It also eliminates the API key dependency that currently blocks users from seeing the schedule.

**Independent Test**: Launch the app with no API key configured. Open the Schedule tab. Verify all 48 group stage matches load from the URL and display team names, dates, times, groups, and venues.

**Acceptance Scenarios**:

1. **Given** the app starts with no API key configured, **When** the Schedule tab opens, **Then** all 48 group stage matches are fetched from the openfootball worldcup.json URL and displayed.
2. **Given** the data is loaded, **When** rendered, **Then** each match shows both team names, the date, the kick-off time with UTC offset, the group letter (A-L), and the venue/city name.
3. **Given** the data source URL, **When** the request succeeds, **Then** matches are grouped by their group field (Group A through Group L) with 6 matches per group.
4. **Given** the matches are displayed, **When** rendered, **Then** they are sorted by date and kick-off time within each group.

---

### User Story 2 - Filter matches by group (Priority: P1)

A user wants to focus on a specific group. They select a group chip (e.g., "C") and instantly see only the 6 matches for that group. Selecting "All" returns the full list of 48 matches.

**Why this priority**: Joint P1 with US1. Group filtering is essential for navigating 48 matches and is the primary way users interact with group stage data.

**Independent Test**: Open the Schedule tab. Click "Group C". Verify exactly 6 Group C matches appear. Click "All" to verify all 48 matches return.

**Acceptance Scenarios**:

1. **Given** the Schedule tab is loaded with URL data, **When** the page renders, **Then** a group selector with options All, A, B, C, D, E, F, G, H, I, J, K, L is visible.
2. **Given** "All" is active, **When** the user selects "Group E", **Then** only Group E matches (6 matches) are displayed.
3. **Given** a group filter is active, **When** the user selects a different group, **Then** the match list updates immediately without a page reload.
4. **Given** any group is selected, **When** the user selects "All", **Then** all 48 group stage matches are displayed sorted by date and time.

---

### User Story 3 - See match details with venue information (Priority: P2)

A user wants to know where each match takes place. Each match row displays the venue city and stadium name sourced from the local worldcup.json data, allowing fans to identify the location of every group stage match.

**Why this priority**: Venue information is a key part of "match details" and adds significant value for users planning to attend or follow matches by location.

**Independent Test**: Select any group. Verify each match shows a venue name (city or stadium). Verify venue data matches the ground field from the worldcup.json source.

**Acceptance Scenarios**:

1. **Given** a match has a ground value in the data, **When** rendered, **Then** the venue city is displayed (e.g., "Mexico City", "Atlanta").
2. **Given** a match has a ground value with parenthetical detail (e.g., "Guadalajara (Zapopan)"), **When** rendered, **Then** the full ground string is shown.
3. **Given** a match has no ground value, **When** rendered, **Then** "TBD" is displayed in place of the venue.

---

### User Story 4 - Distinguish match scheduling status (Priority: P2)

A user needs to see which matches have been played and which are upcoming. Since the URL data contains fixtures (pre-tournament), all matches display as scheduled. The system clearly indicates these are upcoming fixtures with no scores.

**Why this priority**: Status indication helps users understand the tournament state and sets expectations about what data is available from the URL source.

**Independent Test**: View any group. Verify all matches show a "Scheduled" status indicator since the URL data contains pre-tournament fixtures. Verify no scores are shown for unplayed matches.

**Acceptance Scenarios**:

1. **Given** a match from the URL data has no score field, **When** rendered, **Then** the score area shows "vs" to indicate the match has not been played.
2. **Given** a match from the URL data, **When** rendered, **Then** a status badge shows "Scheduled" to indicate the match is upcoming.
3. **Given** all group stage matches from the URL, **When** rendered, **Then** each match clearly shows date and time information since no live score data is available from this source.

---

### Edge Cases

- What happens when the URL is unreachable (network error)? Show a user-friendly error message with a retry option and display the locally bundled worldcup.json data as a fallback.
- What happens when the URL returns malformed or empty data? Show an error notice and fall back to the local data file bundled in the project.
- What happens when a group has fewer than 6 matches in the data? Display whatever matches are present for that group without error.
- What happens when the data contains both group stage and knockout stage matches? Only display matches that have a group field (Group A through Group L), filtering out knockout rounds.
- What happens when the user has no internet connection? Use the locally bundled worldcup.json file at data/worldcup/2026/worldcup.json as the data source.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST fetch group stage match data from the openfootball worldcup.json URL (https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json) when the Schedule tab loads.
- **FR-002**: System MUST fall back to the locally bundled worldcup.json file when the URL is unreachable or returns an error.
- **FR-003**: System MUST filter the loaded data to include only group stage matches (those with a group field containing "Group A" through "Group L"), excluding knockout stage matches.
- **FR-004**: System MUST display a group selector with options: All, A, B, C, D, E, F, G, H, I, J, K, L rendered as interactive chips or tabs.
- **FR-005**: Selecting a group MUST filter the match list to show only matches belonging to that group, updating instantly without a page reload.
- **FR-006**: Each match row MUST display: team1 name, team2 name, date, kick-off time with UTC offset, group letter, and venue/ground name.
- **FR-007**: Matches within any view MUST be sorted by date (ascending) then by kick-off time (ascending).
- **FR-008**: For matches without scores (all URL fixture data), the score area MUST display "vs" and a "Scheduled" status badge.
- **FR-009**: System MUST display a notice indicating the data source (e.g., "Loaded from openfootball data") so users know where the information comes from.
- **FR-010**: System MUST NOT require an API key to load and display the group stage schedule from the URL data source.

### Key Entities

- **Match**: A single group stage fixture with attributes: team1 name, team2 name, date, time (with UTC offset), group name, round name, and ground/venue.
- **Group**: A collection of 4 teams and 6 matches within one of 12 groups (A through L) in the tournament.
- **Group Selector**: Interactive UI element allowing filtering by a single group (A-L) or all groups simultaneously.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 48 group stage matches load and display within 3 seconds of opening the Schedule tab on a standard connection.
- **SC-002**: A user can locate all matches for any single group within 2 interactions (open tab, select group).
- **SC-003**: 100% of loaded matches display a venue name or "TBD" — no match row ever shows a blank venue field.
- **SC-004**: The schedule is fully functional without an API key — users see all group stage data with zero configuration.
- **SC-005**: The match list for any selected group renders in under 0.5 seconds after selection (data already loaded).
- **SC-006**: The view is usable on viewport widths from 360 px to 1920 px without horizontal scrolling of the overall layout.

---

## Assumptions

- The openfootball worldcup.json URL (https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json) is publicly accessible and does not require authentication.
- The URL data contains all 48 group stage matches (12 groups x 4 teams x 3 matchdays = 72 match slots, but only 48 unique matches since each pair plays once) for the 2026 FIFA World Cup.
- The local file at data/worldcup/2026/worldcup.json is kept in sync with the URL data and serves as a reliable offline fallback.
- All matches in the URL data are pre-tournament fixtures; no live score updates are expected from this data source.
- The existing group chip UI pattern from the current schedule view (spec 012) will be reused for consistency.
- UTC offset times from the data (e.g., "UTC-6", "UTC-4") are displayed as-is without conversion to the user's local timezone.
- Knockout stage matches in the same JSON file (Round of 32, Quarter-finals, etc.) are excluded from this feature's scope, which focuses on group stage only.
