<!-- 
SYNC IMPACT REPORT
Version change: 1.0.0 → 1.0.1
Modified principles: I. Flet-First UI — corrected deprecated ft.UserControl API
  reference; added Flet-compliant rendering guidance (Canvas/Image for custom
  graphics); no semantic change to the principle itself
Added sections: none
Removed sections: none
Templates requiring updates:
  ✅ constitution.md updated
  ✅ plan-template.md reviewed — no constitution-driven changes required
  ✅ spec-template.md reviewed — no constitution-driven changes required
  ✅ tasks-template.md reviewed — no constitution-driven changes required
Follow-up TODOs: none
-->

# FootballImplFlet2026 Constitution

## Core Principles

### I. Flet-First UI (NON-NEGOTIABLE)
All user interface MUST be implemented with the Flet framework (Python >= 3.10,
Flet >= 0.84). No alternative UI frameworks (Tkinter, PyQt, web-only HTML/JS,
etc.) are permitted.

UI components MUST be cross-platform compatible: desktop, web, and mobile builds
are first-class targets. Custom reusable controls MUST be implemented as Python
functions or classes that compose standard Flet controls (e.g., `ft.Container`,
`ft.Column`, `ft.Row`). The deprecated `ft.UserControl` base class MUST NOT be
used; use plain Python composition instead.

Custom graphics (maps, charts, diagrams) MUST use Flet's built-in primitives:
`ft.Canvas` for procedural drawing, `ft.Image` for SVG/raster assets, or
`ft.GestureDetector` for interactive hit-testing. No raw JavaScript or
browser-DOM manipulation is permitted.

### II. Feature-Module Separation
Each major feature domain (e.g., match tracking, standings, player stats, settings)
MUST live in its own Python module under `src/`. Modules MUST NOT import from
sibling feature modules directly; shared logic belongs in `src/shared/` or
`src/services/`. This enforces clean boundaries and independent testability.

### III. Test-First (NON-NEGOTIABLE)
TDD is mandatory: tests MUST be written and approved by the developer before
implementation code is authored. The cycle is strictly: Red > Green > Refactor.
Unit tests live in `tests/unit/`, integration tests in `tests/integration/`.
A feature is not considered complete until all related tests pass with no
skipped or xfail entries that have not been explicitly documented.

### IV. API-Backed Data Layer
All football data (fixtures, results, standings, player stats) MUST be fetched
through a defined service layer (`src/services/`). The service layer abstracts
over data sources (live API, mock, cache). No UI component may call an external
API directly. FastAPI is used for any backend endpoints exposed to the Flet
frontend when running in web mode.

### V. Simplicity & YAGNI
Start with the simplest implementation that satisfies the requirement.
Over-engineering is a defect. Complexity MUST be justified with a documented
rationale in the PR or commit message. Prefer composition over inheritance.
Avoid premature abstraction; refactor only when duplication appears 3 or more times.

## Technology Stack

- **Language**: Python >= 3.10
- **UI Framework**: Flet >= 0.84 (`flet[all]`)
- **Backend (web mode)**: FastAPI >= 0.136
- **Package manager**: `uv` (pyproject.toml, PEP 517)
- **Test runner**: pytest
- **Supported targets**: Desktop (Linux, macOS, Windows), Web, Android (APK/AAB), iOS (IPA)
- **Build tool**: `flet build` CLI

No runtime dependency outside this list may be introduced without a constitution
amendment documenting the rationale.

## Development Workflow

1. All work MUST begin from a feature branch (`feature/<slug>`).
2. Tests MUST pass locally (`uv run pytest`) before a PR is opened.
3. Each PR MUST reference the task ID from `tasks.md`.
4. The `src/main.py` entry point MUST remain minimal — it wires the Flet `main`
   function and delegates to the router/view layer.
5. Secrets (API keys, tokens) MUST never be committed; use environment variables
   or a `.env` file listed in `.gitignore`.
6. `uv run flet run` (desktop) and `uv run flet run --web` (browser) are the
   canonical local-run commands; CI MUST validate both modes.

## Governance

This constitution supersedes all other project conventions. Any practice that
conflicts with a principle stated here is invalid until the constitution is
formally amended.

**Amendment procedure**:
- Open a PR that modifies `.specify/memory/constitution.md`.
- Increment the version according to semantic versioning rules:
  MAJOR = principle removal/redefinition; MINOR = new principle/section added;
  PATCH = clarification or wording fix.
- Update `LAST_AMENDED_DATE` to the date the amendment PR merges.
- All dependent templates (plan-template, spec-template, tasks-template) MUST be
  reviewed for consistency within the same PR.

All PRs and code reviews MUST verify compliance with the principles above.
Complexity introduced without documented justification MUST be refactored before
merge.

**Version**: 1.0.1 | **Ratified**: 2026-05-13 | **Last Amended**: 2026-05-15
