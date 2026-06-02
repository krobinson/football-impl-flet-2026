# Feature Specification: Team Tournament Progression

**Feature Branch**: `011-team-progression`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "please change the group stages so we can see the progress of each of the teams through the rounds to the final."

## Clarifications

### Session 2026-05-26

- Q: How should match scores involving extra time or penalties be displayed? → A: Two-line — main full-time score on line 1, qualifier `(AET, 4–2 pens)` in smaller text below.
- Q: Should round sections start expanded or collapsed when the panel first loads? → A: All rounds expanded by default.
- Q: When no team filter is active, how should the all-teams view be organised? → A: Grouped by round only — all matches for a round listed together, no sub-grouping by group letter.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Team Path Through Tournament (Priority: P1)

A user selects a World Cup edition in the History tab and can see — for every team that participated — which rounds they reached and their results at each stage, from group stage matches through to the Final.

**Why this priority**: This is the core ask. Without it, the tab only shows aggregate stats; adding round-by-round progression transforms it into a meaningful tournament narrative.

**Independent Test**: Select a single edition (e.g. 2022). Verify that for at least one team (e.g. Argentina) all stages are listed in order: three group-stage matches, then Round of 16, then Quarter-finals, then Semi-finals, then Final, with correct results at each step.

**Acceptance Scenarios**:

1. **Given** a World Cup edition is selected, **When** the user views the tournament progression panel, **Then** every participating team appears at least once.
2. **Given** a team that was eliminated in the group stage, **When** the user views that team's progression, **Then** only its three group-stage matches are shown with no knockout rounds.
3. **Given** the tournament champion, **When** the user views its progression, **Then** all six (or seven) stages including the Final are shown, with all results correct.
4. **Given** a team that finished third, **When** the user views its progression, **Then** the third-place playoff match appears as the final stage.

---

### User Story 2 - Filter Progression by Team (Priority: P2)

A user wants to focus on a single team and follow its journey across all rounds without scrolling through all other teams.

**Why this priority**: High-value interaction for fans of a specific country; enables quick lookup without needing to scan the full bracket.

**Independent Test**: Select an edition, then choose a single team from a filter. Verify only that team's matches are displayed and arranged in round order.

**Acceptance Scenarios**:

1. **Given** a tournament is selected, **When** the user selects a specific team, **Then** only that team's matches are shown ordered from group stage to the furthest round they reached.
2. **Given** the filter is cleared, **When** viewing the panel, **Then** all teams are visible again.

---

### User Story 3 - Compare Team Progressions Across Editions (Priority: P3)

A user can switch between World Cup editions and immediately see how that team (if re-selected in the filter) fared in different years, building a historical picture.

**Why this priority**: Nice-to-have that adds depth to the history feature; lowest priority as it relies on P1 and P2 working first.

**Independent Test**: Select Germany as the team filter. Switch from 2014 to 2018. Verify Germany's progression updates to match its 2018 results (group-stage exit).

**Acceptance Scenarios**:

1. **Given** a team filter is active, **When** the edition selector changes, **Then** the progression panel refreshes to show that team's journey in the newly selected edition.
2. **Given** a team did not participate in the selected edition, **When** viewing the panel, **Then** a clear "Team did not participate in this edition" message is shown.

---

### Edge Cases

- What happens when data for an older edition only has group-stage results (no knockout structure)? Show only available round data with no empty knockout rows.
- How does the system handle a match recorded without a score (incomplete data)? Show the match with the result displayed as "—" or "TBD".
- What if a team name changed between editions (e.g. West Germany → Germany)? Each edition uses the team name as it appears in that edition's data.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tournament progression view MUST display all participating teams' matches grouped by round, for the currently selected edition. Within each round all matches are listed together with no sub-grouping.
- **FR-002**: Rounds MUST be displayed in chronological order: Group Stage (Matchday 1 → 3), Round of 16, Quarter-finals, Semi-finals, Third Place Play-off (where applicable), Final.
- **FR-003**: Each match entry MUST show: team 1, team 2, full-time score, and the round/stage name. When a match was decided by extra time or penalties, a second line in smaller text MUST show the qualifier (e.g. `(AET, 4–2 pens)`).
- **FR-004**: Users MUST be able to filter the progression view to a single team.
- **FR-005**: When no team filter is active, all rounds for the edition MUST be shown, each containing every match played in that round.
- **FR-006**: The view MUST update without a full page reload when the edition or team filter changes.
- **FR-007**: Teams eliminated in the group stage MUST NOT appear as "lost in Round of 16" — only rounds where they actually played are shown.
- **FR-008**: The existing edition summary (champion, runner-up, goals, etc.) MUST remain visible alongside the new progression panel.
- **FR-009**: All round sections in the progression panel MUST be expanded by default when the panel first loads or refreshes.

### Key Entities

- **Edition**: A single World Cup year; has a name and a collection of matches.
- **Match**: A single game; belongs to a round/stage, has two teams and a score.
- **Round**: A named stage of the tournament (e.g. "Group Stage", "Quarter-finals"); matches are grouped under rounds.
- **Team Progression**: The ordered sequence of rounds a specific team played in a given edition, with results.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can identify which round any team was eliminated in for any edition within 10 seconds of selecting that edition.
- **SC-002**: The full progression view for any edition loads and renders in under 2 seconds.
- **SC-003**: Filtering to a single team updates the view in under 0.5 seconds.
- **SC-004**: 100% of matches present in the source data appear in the progression view — no matches are silently omitted.
- **SC-005**: The view is readable on viewport widths from 360 px to 1920 px without horizontal scrolling inside the progression panel.

---

## Assumptions

- The existing `worldcup.json` match data for each edition (with `round`, `team1`, `team2`, `score` fields) is sufficient; no additional data sources are needed.
- "Group Stage" matches are those whose `round` value starts with "Matchday"; all other named rounds are knockout rounds.
- Third-place playoff is included when present in the data.
- The feature targets the existing **History** tab (tournament view); no new top-level navigation item is required.
- Editions without knockout data (e.g. 1950 round-robin final) will show only the rounds that exist in their data file.
