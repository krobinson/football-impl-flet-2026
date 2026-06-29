# Research: Remove History Tabs

**Feature**: 013-remove-history-tabs
**Date**: 2026-06-10

---

## Decision 1 — Scope: Only `app.py` changes required

**Decision**: All changes are confined to a single file: `src/app.py`. No view files are deleted; no tests require modification.

**Rationale**: The four tabs are wired exclusively in `app.py`. Removing their content blocks, nav destinations, and imports from that file completely satisfies FR-001 through FR-008. The view source files are preserved for potential future re-use (per spec Assumption 1).

**Alternatives considered**:
- Deleting the view files — rejected; spec explicitly says "not deleted from the repository".
- Moving views to a separate branch — unnecessary complexity; YAGNI (Constitution V).

---

## Decision 2 — `store` and `get_data_store` can be fully removed

**Decision**: Remove `get_data_store` import, the `store` variable in `main()`, and the `store` parameter from `_build_app()`.

**Rationale**: Verified by reading `app.py` — `store` is passed to `build_tournament_view(store)`, `build_teams_view(store)`, `build_matches_view(store, ...)`, and `build_records_view(store)` exclusively. The three remaining tabs use only `page`, `svc`, and `fd_client`. Removing `store` eliminates the `features.matches.services` import and its associated startup I/O (loading all worldcup JSON files).

**Evidence**:
- `build_osm_map_view(page)` — no `store`
- `build_schedule_view(fd_client)` — no `store`
- Map tab — uses `svc` (WorldCupDataService), `map_state` — no `store`

---

## Decision 3 — `_build_app` signature changes from 4 args to 3

**Decision**: Remove `store` parameter from `_build_app(page, svc, store, fd_client)` → `_build_app(page, svc, fd_client)`. Update the `page.render(...)` call accordingly.

**Rationale**: `store` is no longer used in the function body after the four content blocks are removed. Keeping it as an unused parameter would violate Constitution V (YAGNI) and would still trigger `get_data_store()` I/O at startup.

---

## Decision 4 — Four imports removed

**Decision**: Remove these four import lines from `app.py`:
```python
from features.matches.services import get_data_store
from features.tournament.views.tournament_view import build_tournament_view
from features.teams.views.teams_view import build_teams_view
from features.matches.views.matches_view import build_matches_view
from features.records.views.records_view import build_records_view
```

**Rationale**: Unused imports are dead code. Their presence would cause Python to import and execute module-level code in all four view modules at startup — wasted work. Clean imports = faster startup (SC-002).

---

## Decision 5 — No test changes required

**Decision**: Zero test files need modification.

**Rationale**: Existing tests operate on unit/integration level targeting individual view modules and services — none test `app.py` wiring. All 143 existing tests will continue to pass after removing the four content blocks from `app.py`.
