# Implementation Plan: World Cup Participating Countries Map

**Branch**: `001-worldcup-map` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-worldcup-map/spec.md`

## Summary

Render an interactive world map inside a Flet web app where all 48 FIFA World Cup
2026 qualifying nations are colour-highlighted. Users can click any country to see
a detail panel (name, group, flag), and filter the map to a specific FIFA group.
The map is built entirely with `ft.Canvas` drawing country polygons projected from
a bundled GeoJSON asset — no external map tile service or JavaScript is required.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Flet >= 0.84 (`flet[all]`); stdlib only for data loading (json, math)
**Storage**: Static files only — `src/assets/countries.geojson` (Natural Earth) + `src/assets/worldcup2026.json` (team data)
**Testing**: pytest (unit + integration)
**Target Platform**: Web browser (desktop/tablet primary); desktop Flet app secondary
**Project Type**: Flet web app (single-page)
**Performance Goals**: Map renders within 5 seconds on broadband; canvas repaints < 100 ms on filter change
**Constraints**: Zero runtime dependencies beyond `flet[all]`; no external API calls at runtime; offline-capable after initial load
**Scale/Scope**: Single page, 48 countries, ~12 FIFA groups (A–L)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Flet-First UI | ✅ PASS | Map rendered via `ft.Canvas` + `ft.GestureDetector`; SVG assets via `ft.Image`. No Tkinter/JavaScript. |
| II. Feature-Module Separation | ✅ PASS | `views/`, `services/`, `shared/` modules defined; no cross-feature imports. |
| III. Test-First | ✅ PASS | Tests written before implementation; TDD cycle enforced in task order. |
| IV. API-Backed Data Layer | ✅ PASS | `WorldCupDataService` in `src/services/` mediates all data; views never touch files directly. |
| V. Simplicity & YAGNI | ✅ PASS | Equirectangular projection (stdlib math only); static data files; no ORM, no server-side DB. |

**Post-Phase-1 re-check**: ✅ All gates pass. Equirectangular projection chosen over Mercator — simpler math, sufficient for political-map highlighting. Static JSON chosen over SQLite — no benefit from a database at this scale.

## Project Structure

### Documentation (this feature)

```text
specs/001-worldcup-map/
├── plan.md              ← this file
├── research.md          ← Phase 0
├── data-model.md        ← Phase 1
├── quickstart.md        ← Phase 1
├── contracts/
│   └── worldcup-data-contract.md   ← Phase 1
└── tasks.md             ← Phase 2 (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── main.py                          # Flet entry point — wires ft.run(main) only
├── views/
│   └── map_view.py                  # WorldCupMapView: Canvas map + info panel + group filter
├── services/
│   └── worldcup_data.py             # WorldCupDataService: loads & queries static JSON data
└── shared/
    ├── models.py                    # ParticipatingCountry, FIFAGroup dataclasses
    └── geo_utils.py                 # Equirectangular projection, point-in-polygon

src/assets/
├── countries.geojson                # Natural Earth 1:110m country polygons (bundled)
└── worldcup2026.json                # 48 qualified teams: ISO-A3, group, appearances, flag emoji

tests/
├── unit/
│   ├── test_models.py
│   ├── test_worldcup_data.py
│   └── test_geo_utils.py
└── integration/
    └── test_map_view.py
```

**Structure Decision**: Single-project layout (Option 1). No backend server required —
data is static, loaded in-process by `WorldCupDataService`. `ft.run(main)` serves
the app in web mode directly via Flet's built-in server.

## Complexity Tracking

No constitution violations. No complexity justification required.

## Phases

### Phase 0: Research *(complete — see research.md)*

Key decisions resolved:
- **Map rendering**: `ft.Canvas` with GeoJSON polygon projection (no SVG service, no external tiles)
- **Projection**: Equirectangular (plate carrée) — sufficient for political highlighting, stdlib math only
- **Hit-testing**: Point-in-polygon via ray-casting algorithm (stdlib, O(n) per polygon)
- **Data source**: Natural Earth 1:110m GeoJSON (`ne_110m_admin_0_countries`) — CC0 licence ✅
- **Team data**: Hand-authored `worldcup2026.json` (48 teams, ISO-A3, group, appearances, flag emoji)

### Phase 1: Design *(complete — see data-model.md, contracts/, quickstart.md)*

Entities: `ParticipatingCountry`, `FIFAGroup`, `GeoFeature`
Interface contract: `WorldCupDataService` public API (see `contracts/worldcup-data-contract.md`)
