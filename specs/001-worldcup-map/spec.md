# Feature Specification: World Cup Participating Countries Map

**Feature Branch**: `001-worldcup-map`
**Created**: 2026-05-15
**Status**: Draft
**Input**: User description: "create a web app using flet which show each country on a world map that is participating in the word cup"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View World Cup Countries on Map (Priority: P1)

A visitor opens the web app and is immediately presented with an interactive world
map where every country participating in the current FIFA World Cup is visually
highlighted. The user can see at a glance which nations have qualified, without
needing to interact further.

**Why this priority**: This is the core deliverable — the entire value of the
feature is conveyed by this single, self-contained view.

**Independent Test**: Open the app in a browser; all 32 (or 48 for 2026) qualifying
nations MUST be distinctly highlighted on the map. The feature is testable and
delivers full stated value without any other story being implemented.

**Acceptance Scenarios**:

1. **Given** the app is open, **When** the map finishes loading, **Then** all participating countries are highlighted in a distinct colour that contrasts with non-participating countries.
2. **Given** the map is displayed, **When** a user views it on a desktop browser, **Then** the full world map is visible without horizontal scrolling.
3. **Given** the map is displayed, **When** a country is not a World Cup participant, **Then** it is shown in a neutral / muted colour clearly differentiated from participants.

---

### User Story 2 - Inspect Country Details (Priority: P2)

A user clicks or taps on a highlighted country and sees a brief info panel showing
the country name, their FIFA group (if applicable), flag, and number of times they
have previously appeared in the tournament.

**Why this priority**: Adds educational depth. Without it the app is still fully
functional (P1 covers the map), but this significantly increases engagement.

**Independent Test**: Clicking any highlighted country toggles an info panel that
shows at minimum the country name and group assignment. Can be demonstrated
independently.

**Acceptance Scenarios**:

1. **Given** the map is displayed, **When** the user clicks a participating country, **Then** an info panel appears with at minimum the country name and FIFA group.
2. **Given** an info panel is open, **When** the user clicks elsewhere on the map or a close button, **Then** the panel dismisses cleanly.
3. **Given** the user clicks a non-participating country, **Then** no info panel appears (or a brief "not qualified" notice is shown).

---

### User Story 3 - Filter / Search by Group (Priority: P3)

A user selects a FIFA group (A, B, C … H or equivalent) from a filter control
and the map highlights only the countries belonging to that group, dimming all
others.

**Why this priority**: Useful for fans following a specific group, but not
essential to the core purpose.

**Independent Test**: Selecting "Group A" from the filter highlights only the
four Group A nations. Testable in isolation.

**Acceptance Scenarios**:

1. **Given** the filter is set to a specific group, **When** the map re-renders, **Then** only countries in that group are fully highlighted; all others are dimmed.
2. **Given** a group filter is active, **When** the user clears the filter, **Then** all participating countries return to their default highlighted state.

---

### Edge Cases

- What happens when the country data fails to load (network error or missing data file)?
- How does the map render on narrow viewport widths (mobile browsers)?
- How are overseas territories or disputed regions handled (e.g., French Guiana shown as France)?
- What if the World Cup edition's team list is updated mid-tournament (late withdrawals)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST display a world map that fills the primary visible area of the browser window.
- **FR-002**: The app MUST visually distinguish all World Cup participating countries from non-participating countries using colour.
- **FR-003**: The list of participating countries MUST be accurate for the FIFA World Cup 2026 (48 teams).
- **FR-004**: Clicking or tapping a participating country MUST reveal a detail panel containing at minimum the country name and FIFA group.
- **FR-005**: A group filter control MUST allow users to isolate countries by their assigned FIFA group.
- **FR-006**: The app MUST be navigable and fully functional in a web browser (desktop and tablet viewports as primary targets).
- **FR-007**: Non-participating countries MUST remain visible on the map in a clearly differentiated style.
- **FR-008**: The map MUST be navigable — users MUST be able to zoom and pan.
- **FR-009**: Country highlighting state MUST update correctly when a group filter is applied or cleared.
- **FR-010**: The app MUST handle a missing or corrupt data source gracefully by showing a user-visible error message rather than a blank screen.

### Key Entities

- **ParticipatingCountry**: Represents a qualified nation. Key attributes (non-technical): name, ISO country code, FIFA group assignment, flag image, historical appearances.
- **FIFAGroup**: A group (A–L for 2026) containing exactly 4 participating countries. Used for filtering.
- **MapRegion**: A rendered polygon on the world map corresponding to a country boundary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 48 FIFA World Cup 2026 participating countries are correctly highlighted on the map on initial load, verifiable by visual inspection and automated test.
- **SC-002**: The map is fully rendered and interactive within 5 seconds on a standard broadband connection.
- **SC-003**: A user can identify any participating country and its FIFA group without leaving the map view (zero navigation steps beyond a single click).
- **SC-004**: The app renders without layout errors on viewport widths from 768 px (tablet) upward in a supported web browser.
- **SC-005**: 100% of the 48 countries display a correct info panel when clicked, as verified by automated or manual test coverage.

## Assumptions

- The target edition is **FIFA World Cup 2026** with 48 participating nations.
- The complete list of 48 qualified teams is known and will be embedded as static data in the app (no live FIFA API dependency required for the initial version).
- Primary target viewport is desktop/tablet web; native mobile app is out of scope for this spec.
- Country boundary map data is sourced from a permissively-licensed open dataset (e.g., Natural Earth or similar); licensing compliance is assumed to be satisfied before publication.
- Overseas territories are mapped to their governing nation (e.g., French Guiana counts as France) in alignment with FIFA nationality rules.
- Internationalisation (non-English country names / group labels) is out of scope for v1.
