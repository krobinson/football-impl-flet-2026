# Feature Specification: Schedule Group Stage Display

**Feature Branch**: `012-schedule-group-display`
**Created**: 2026-06-09
**Status**: Draft
**Input**: User description: "please look at the schedule tab. Please give an option to display each group stage. Show the upcoming matches including the kickoff time and venue. When a match is finished show the results."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Browse matches by group (Priority: P1)

A user wants to focus on a single group rather than scrolling through all 48 matches at once. They select a group (e.g. Group C) from a set of clearly labelled tabs or buttons and instantly see only the 6 matches for that group — or switch back to see all groups at once.

**Why this priority**: This is the core ask. Without per-group filtering the schedule is one undifferentiated list of 48 rows. Group filtering transforms it into a usable match browser.

**Independent Test**: Open the Schedule tab. Click "Group C". Verify exactly the Group C matches appear, ordered by matchday. Click "All" to verify all 48 matches return.

**Acceptance Scenarios**:

1. **Given** the Schedule tab is open, **When** the page loads, **Then** a group selector (tabs or chips: All, A, B, … L) is visible above the match list.
2. **Given** "All" is active, **When** the user selects "Group E", **Then** only Group E matches are displayed and the selector reflects the active group.
3. **Given** a group is active, **When** the user selects a different group, **Then** the match list updates immediately without a page reload.
4. **Given** "All" is selected, **When** rendered, **Then** all loaded matches appear sorted by matchday then kick-off time.

---

### User Story 2 — See upcoming match details (kickoff time + venue) (Priority: P1)

A user looking at matches that have not yet been played needs to know when and where each match takes place. The kick-off time (in UTC, clearly labelled) and the full stadium/venue name are visible for every upcoming match.

**Why this priority**: Joint P1 with US1 — without time and venue information the schedule is not actionable for a fan planning to watch or attend.

**Independent Test**: Select any group containing at least one unplayed match. Verify each unplayed match row shows: date, UTC kick-off time labelled as UTC, and the stadium/venue name (not just the city). Verify the status badge reads "Scheduled" or "Confirmed".

**Acceptance Scenarios**:

1. **Given** a match has status `SCHEDULED` or `TIMED`, **When** rendered, **Then** the row displays the date, UTC kick-off time, and venue name.
2. **Given** the kick-off time is displayed, **When** shown, **Then** it is clearly labelled as UTC (e.g. "14:00 UTC") to avoid confusion with local time.
3. **Given** a venue name is available from the API, **When** rendered, **Then** the full stadium name is shown (e.g. "MetLife Stadium") not just the city.
4. **Given** a match has no venue data yet, **When** rendered, **Then** "TBD" is shown in place of the venue name.

---

### User Story 3 — See finished match results (Priority: P1)

A user checking on results needs to quickly distinguish completed matches from upcoming ones, and read the final score without having to interpret a status badge.

**Why this priority**: Joint P1 — results are as important as fixtures; the tab needs to serve both audiences simultaneously.

**Independent Test**: Select a group that contains at least one finished match. Verify the finished match shows the full-time score prominently (e.g. "2–1") and a "FT" status indicator, visually distinct from the "vs" shown for unplayed matches.

**Acceptance Scenarios**:

1. **Given** a match has status `FINISHED`, **When** rendered, **Then** the full-time score is displayed prominently (e.g. "2 – 1") instead of "vs".
2. **Given** a finished match, **When** rendered, **Then** a "FT" badge is shown in a visually distinct style (e.g. muted colour) to indicate the match is over.
3. **Given** a live/in-play match (status `IN_PLAY` or `PAUSED`), **When** rendered, **Then** the current score is shown alongside a highlighted "LIVE" or "HT" badge.
4. **Given** a mix of finished and upcoming matches in one group, **When** rendered together, **Then** finished matches and upcoming matches are visually distinguishable at a glance.

---

### Edge Cases

- What if the API returns no matches for a selected group? Show a "No matches available for this group" placeholder.
- What if the kick-off time is unknown (field missing or null)? Show "TBD" in the time column.
- What if only some matches in a group are finished? Finished rows appear alongside upcoming rows, ordered by matchday — no separate sections required.
- What if the API key is missing? The existing "Set FOOTBALL_DATA_API_KEY to load the live schedule" message remains; the group selector is still rendered but shows empty state.
- What if a group label from the API is `GROUP_A` format? Strip the prefix to display just the letter "A".

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Schedule tab MUST display a group selector showing options: All, A, B, C, D, E, F, G, H, I, J, K, L — rendered as clearly labelled interactive chips or tabs.
- **FR-002**: Selecting a group MUST filter the match list to only matches belonging to that group, updating instantly without a page reload.
- **FR-003**: Each match row MUST display: matchday number, date, kick-off time (UTC, clearly labelled), group, home team, score or "vs", away team, status badge, and venue name.
- **FR-004**: For unplayed matches (status `SCHEDULED` or `TIMED`), the score field MUST show "vs" and the kick-off time and venue MUST be prominently visible.
- **FR-005**: For finished matches (status `FINISHED`), the full-time score MUST be displayed (e.g. "2 – 1") and a "FT" status badge MUST be shown.
- **FR-006**: For live matches (status `IN_PLAY` or `PAUSED`), the current score MUST be shown alongside a "LIVE" or "HT" badge rendered in a highlighted colour.
- **FR-007**: Matches within any view MUST be sorted by matchday number (ascending) then by kick-off time (ascending).
- **FR-008**: When no API key is configured, the group selector MUST still render and the match area MUST show the existing API key missing notice.
- **FR-009**: Venue name MUST be the full stadium name (e.g. "MetLife Stadium") sourced from the API `venue` field; if absent, display "TBD".

### Key Entities

- **Group Selector**: Interactive UI element allowing filtering by a single group (A–L) or all groups.
- **Match Row**: Single-match display unit showing all required fields (date, time, teams, score/status, venue).
- **Match Status**: One of: SCHEDULED, TIMED, IN_PLAY, PAUSED, FINISHED, POSTPONED — each rendered with a distinct label and colour.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can locate all matches for any single group within 2 interactions (open tab, select group).
- **SC-002**: The match list for any selected group renders in under 0.5 seconds after selection (data already loaded).
- **SC-003**: 100% of loaded matches display a venue name or "TBD" — no match row ever shows a blank venue field.
- **SC-004**: Finished matches and upcoming matches are visually distinguishable without reading the status badge text.
- **SC-005**: The view is usable on viewport widths from 360 px (scrolls horizontally within the row if needed) to 1920 px.

---

## Assumptions

- Match data continues to be sourced from football-data.org via the existing `FootballDataClient.get_group_matches()` method — no new API endpoints required.
- The `venue` field in the API response contains the stadium name as a string; if it is absent or null, "TBD" is shown.
- UTC times are sufficient; local time conversion is out of scope for this feature.
- The existing `_STATUS_LABEL` dict in `match_row.py` already maps all required statuses — it may be reused or extended.
- The 2026 tournament has 12 groups (A–L), each with 4 teams and 6 group-stage matches (48 total).
- The group selector replaces the existing dropdown; the underlying filter logic remains the same.
