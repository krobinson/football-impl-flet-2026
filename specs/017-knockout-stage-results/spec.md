# Feature Specification: Knockout Stage Results & Live Scores

**Feature Branch**: `017-knockout-stage-results`  
**Created**: 2026-07-04  
**Status**: Draft  
**Input**: User description: "If you look at the URL which provides the real time data we have the full results of the group stages. We need to write up those results in the schedule. We also now need to show the results of the round of 32, the round of 16, the quarter final, the semifinal and the final."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View group stage match scores (Priority: P1)

A user opens the Schedule tab and sees the actual scores for all completed group stage matches. Instead of seeing "vs" for every match, they see the final score (e.g., "2–0") for matches that have been played. Upcoming matches that have not yet been played still show "vs".

**Why this priority**: The URL data source already contains full group stage results with scores. Displaying these scores is the core value — users open the schedule to see results, not just fixtures. Without scores, the schedule feels incomplete and outdated.

**Independent Test**: Open the Schedule tab. Verify that completed group stage matches display actual scores (e.g., "2–0", "1–1") in the Score column. Verify that any unplayed matches still show "vs". Verify the status badge shows "FT" for finished matches.

**Acceptance Scenarios**:

1. **Given** a group stage match has a score in the URL data, **When** the Schedule tab renders, **Then** the Score column shows the final score in "X–Y" format (e.g., "2–0").
2. **Given** a group stage match has a score in the URL data, **When** rendered, **Then** the status badge shows "FT" (Finished) instead of "Scheduled".
3. **Given** a group stage match has no score in the URL data (upcoming fixture), **When** rendered, **Then** the Score column shows "vs" and the status badge shows "Scheduled".
4. **Given** all 72 group stage matches are loaded from the URL, **When** rendered, **Then** every match with a score displays it correctly matching the source data.

---

### User Story 2 - View knockout stage matches (Priority: P1)

A user wants to see the results of knockout stage matches — Round of 32, Round of 16, Quarter-final, Semi-final, Final, and the third-place match. The Schedule tab displays all knockout matches alongside group stage matches, organized by round. Completed knockout matches show their scores; upcoming knockout matches show "vs".

**Why this priority**: Joint P1 with US1. The tournament is progressing beyond group stages, and users need to see knockout results to follow the full tournament narrative. Without knockout matches, the schedule is incomplete after group stage ends.

**Independent Test**: Open the Schedule tab. Verify knockout stage matches are visible (Round of 32, Round of 16, Quarter-final, Semi-final, Final). Verify completed knockout matches show scores. Verify the round name is displayed for each knockout match.

**Acceptance Scenarios**:

1. **Given** the URL data contains knockout matches, **When** the Schedule tab loads, **Then** all knockout matches (Round of 32, Round of 16, Quarter-final, Semi-final, Final, third-place match) are displayed.
2. **Given** a knockout match has a score, **When** rendered, **Then** the Score column shows the final score and the status badge shows "FT".
3. **Given** a knockout match has no score (not yet played), **When** rendered, **Then** the Score column shows "vs" and the status badge shows "Scheduled".
4. **Given** a knockout match has team placeholders (e.g., "1A", "2B", "3A/B/C/D/F"), **When** rendered, **Then** the placeholder text is displayed as the team name until actual team names are available in the data.
5. **Given** knockout matches are displayed, **When** rendered, **Then** each match shows its round name (e.g., "Round of 32", "Quarter-final", "Final") in place of the group letter.

---

### User Story 3 - Filter matches by tournament stage (Priority: P2)

A user wants to quickly navigate between group stage and knockout stage matches. Stage selector chips allow filtering to show only a specific stage: All, Group Stage, Round of 32, Round of 16, Quarter-final, Semi-final, or Final.

**Why this priority**: With 104 total matches (72 group + 32 knockout), filtering by stage is essential for navigation. Users looking for a specific knockout round should not have to scroll through all group stage matches.

**Independent Test**: Open the Schedule tab. Click "Round of 16". Verify only Round of 16 matches are displayed. Click "All" to verify all matches return.

**Acceptance Scenarios**:

1. **Given** the Schedule tab is loaded, **When** the page renders, **Then** stage selector chips are visible: All, Group Stage, Round of 32, Round of 16, Quarter-final, Semi-final, Final.
2. **Given** "All" is active, **When** the user selects "Quarter-final", **Then** only Quarter-final matches (4 matches) are displayed.
3. **Given** a stage filter is active, **When** the user selects "Group Stage", **Then** only group stage matches (72 matches) are displayed with the existing group chip filter also available.
4. **Given** "Group Stage" is active, **When** rendered, **Then** the existing group letter chips (A–L) are also visible for further filtering. When any other stage is selected, the group letter chips are hidden.
5. **Given** any stage filter is active, **When** the user selects "All", **Then** all 104 matches are displayed sorted by date and time.

---

### Edge Cases

- What happens when a knockout match has placeholder team names (e.g., "1A", "3A/B/C/D/F")? Display the placeholder text as-is in the team columns.
- What happens when the URL data contains a new knockout stage not yet handled (e.g., "Match for third place")? Display it under the "Final" stage filter or as its own category.
- What happens when a knockout match goes to extra time or penalties? Display the full-time score (the `ft` field); extra time and penalty details are out of scope.
- What happens when the URL is unreachable? Fall back to the local file, which may not have scores — display "vs" for all matches and show the fallback notice.
- What happens when a match has a half-time score but no full-time score? Display "vs" since the match is not yet finished.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display actual scores from the URL data for all completed matches (both group stage and knockout) in the Score column.
- **FR-002**: System MUST set the match status to "FINISHED" when a full-time score is present in the data, and "SCHEDULED" when no score is present.
- **FR-003**: System MUST include knockout stage matches (Round of 32, Round of 16, Quarter-final, Semi-final, Final, third-place match) in the schedule display.
- **FR-004**: System MUST display the round name for knockout matches in place of the group letter column.
- **FR-005**: System MUST provide stage selector chips to filter matches by tournament stage: All, Group Stage, Round of 32, Round of 16, Quarter-final, Semi-final, Final.
- **FR-006**: When "Group Stage" is selected in the stage filter, the existing group letter chips (A–L) MUST also be visible for sub-filtering. For all other stage selections, group letter chips MUST be hidden.
- **FR-007**: Knockout matches with placeholder team names (e.g., "1A", "2B") MUST display the placeholder text as the team name.
- **FR-008**: All matches (group and knockout) MUST be sorted by date ascending, then by kick-off time ascending within the "All" view.
- **FR-009**: System MUST continue to use the URL data source as primary with local file fallback (existing behavior from feature 016).
- **FR-010**: The local fallback file MUST be updated to include the latest score data so that offline users also see results.

### Key Entities

- **Match (extended)**: A single tournament fixture with attributes: team1 name, team2 name, date, time, score (full-time and half-time), goals, group name (group stage only), round name, ground/venue. The score field is now populated for completed matches.
- **Tournament Stage**: A classification of matches into stages: Group Stage, Round of 32, Round of 16, Quarter-final, Semi-final, Final (including third-place match).
- **Stage Selector**: Interactive UI element allowing filtering by tournament stage, working alongside the existing group chip filter.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of completed matches (those with scores in the URL data) display the correct final score in the Score column.
- **SC-002**: All 104 tournament matches (72 group stage + 32 knockout) load and display within 3 seconds of opening the Schedule tab.
- **SC-003**: A user can locate all matches for any knockout round within 2 interactions (open tab, select stage chip).
- **SC-004**: The schedule is fully functional without an API key — users see all tournament data with zero configuration.
- **SC-005**: Stage filtering renders in under 0.5 seconds after selection (data already loaded).
- **SC-006**: The view remains usable on viewport widths from 360px to 1920px without horizontal scrolling of the overall layout.

---

## Assumptions

- The openfootball worldcup.json URL continues to provide real-time score updates as matches are completed, including knockout stages.
- The URL data contains all 104 tournament matches: 72 group stage (12 groups × 6 matches) + 32 knockout (16 Round of 32 + 8 Round of 16 + 4 Quarter-final + 2 Semi-final + 1 Final + 1 third-place match).
- Knockout match team names may be placeholders (e.g., "1A", "2B", "3A/B/C/D/F") until the match participants are determined by prior results. The system displays whatever text the data provides.
- The existing score transformation logic in `WorldCupJsonService` (converting `score.ft` to `score.fullTime`) already handles knockout scores correctly.
- The "Match for third place" is grouped under the "Final" stage filter for simplicity, since it occurs on the same matchday as the final.
- The local fallback file (`data/worldcup/2026/worldcup.json`) will be updated to include current scores so offline users see results.
- Extra time and penalty shootout details are out of scope — only the full-time score (`ft` field) is displayed.
- The existing group chip UI pattern is reused for the stage selector chips for visual consistency.
