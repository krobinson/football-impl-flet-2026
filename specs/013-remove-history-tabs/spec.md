# Feature Specification: Remove History Tabs from Navigation

**Feature Branch**: `013-remove-history-tabs`
**Created**: 2026-06-10
**Status**: Draft
**Input**: User description: "please remove from the ui the following tabs; history, teams, matches, records."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Simplified navigation with three tabs (Priority: P1)

A user opens the app and sees a clean, focused navigation bar containing only the three actively relevant tabs: **2026 Map**, **Venues**, and **Schedule**. The four historical data tabs (History, Teams, Matches, Records) are no longer visible and cannot be accessed.

**Why this priority**: This is the sole ask. Removing the tabs simplifies the app to its 2026-tournament-focused purpose. All four removals are a single atomic change; there is no value in removing them one at a time.

**Independent Test**: Open the app. Verify the navigation bar shows exactly three destinations: "2026 Map", "Venues", and "Schedule". Verify no tab labelled "History", "Teams", "Matches", or "Records" appears anywhere in the UI. Tap each of the three remaining tabs and confirm the correct content loads.

**Acceptance Scenarios**:

1. **Given** the app is open, **When** the navigation bar is visible, **Then** it contains exactly 3 destinations: 2026 Map, Venues, Schedule — in that order.
2. **Given** the app loads, **When** the default tab is shown, **Then** the 2026 Map tab is selected by default (index 0 unchanged).
3. **Given** the user taps "Venues", **When** the tab activates, **Then** the OSM venue map is displayed correctly.
4. **Given** the user taps "Schedule", **When** the tab activates, **Then** the 2026 pool schedule with group chips is displayed correctly.
5. **Given** History/Teams/Matches/Records are removed, **When** the app is used, **Then** no errors, blank tabs, or broken navigation states occur.

---

### Edge Cases

- What if the app state previously held a selected index of 2, 3, 4, or 5 (the removed tabs)? After removal those indices no longer exist; the default selected index is 0 (2026 Map), so this only matters for persisted state — which this app does not use.
- What if source code in the removed view modules is still imported by `app.py`? The import lines must also be removed to keep the codebase clean and avoid loading unused code at startup.
- What if tests reference the removed views? No existing tests test the `app.py` wiring directly; no test changes are required.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The navigation bar MUST contain exactly three destinations after this change: "2026 Map" (index 0), "Venues" (index 1), "Schedule" (index 2).
- **FR-002**: The tabs labelled "History", "Teams", "Matches", and "Records" MUST NOT appear in the navigation bar or anywhere else in the UI.
- **FR-003**: Selecting "2026 Map" MUST display the interactive 2026 World Cup polygon/tile map.
- **FR-004**: Selecting "Venues" MUST display the three-panel OSM venue map.
- **FR-005**: Selecting "Schedule" MUST display the 2026 group-stage schedule with group chip selector.
- **FR-006**: The 2026 Map tab MUST remain the default selected tab on app launch.
- **FR-007**: The corresponding build functions (`build_tournament_view`, `build_teams_view`, `build_matches_view`, `build_records_view`) and their imports MUST be removed from `app.py` to avoid loading unused modules at startup.
- **FR-008**: The `DataStore` (`store`) initialisation in `main()` MAY be removed if it is no longer required by any remaining tab. If it is still needed (e.g. by a remaining tab), it MUST be kept.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The navigation bar renders exactly 3 tabs — verifiable by inspection.
- **SC-002**: App startup time does not increase; removing 4 view modules from the startup path should keep or improve startup time.
- **SC-003**: 100% of existing automated tests continue to pass after the change — no regressions from removing the tabs.
- **SC-004**: The app can be navigated through all three remaining tabs without any runtime error.

---

## Assumptions

- The source code for the removed views (`tournament_view.py`, `teams_view.py`, `matches_view.py`, `records_view.py`) is **not deleted** from the repository — only their wiring in `app.py` is removed. This preserves the code for potential future re-use.
- The `DataStore` (`store`) is no longer needed by any of the three remaining tabs (2026 Map uses `WorldCupDataService`; Venues uses `venue_data`; Schedule uses `FootballDataClient`) — therefore the `get_data_store()` call and `store` variable can be removed. If investigation shows otherwise, FR-008 applies.
- No user-facing settings, saved preferences, or deep-link URLs reference the removed tab names.
- The `on_nav_change` handler operates by index; reducing the tab count from 7 to 3 automatically makes previously out-of-range indices unreachable.
