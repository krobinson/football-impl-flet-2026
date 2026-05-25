# Feature Specification: Football-Data.org API Integration — 2026 Pool Matches

**Feature Branch**: `005-football-data-api`
**Created**: 2026-05-21
**Status**: Draft
**Input**: "please look at pulling this URL https://docs.football-data.org/general/v4/competition.html. I want to see the pool matches for 2026. Make sure there is throttling using this resource. https://docs.football-data.org/general/v4/policies.html#_request_throttling"

---

## Problem Statement

The Matches tab currently shows static/mock match data from the local `worldcup2026.json`
file. Real 2026 World Cup group-stage (pool) matches are available via the
[football-data.org v4 API](https://www.football-data.org/). This feature adds a
`FootballDataClient` service that fetches group-stage matches from the live API,
respects the platform's request-throttling policy, and surfaces the results in the
existing Matches tab.

---

## API Reference

### Base URL
```
https://api.football-data.org/v4
```

### Authentication
All authenticated requests must include the header:
```
X-Auth-Token: <token>
```
Tokens are obtained by registering at https://www.football-data.org/. The token
is treated as a secret; it must **never** appear in committed source code. It is
read from the environment variable `FOOTBALL_DATA_API_KEY`.

### Key endpoint — Competition Matches
```
GET /v4/competitions/{code}/matches?stage=GROUP_STAGE
```

| Parameter | Value | Notes |
|-----------|-------|-------|
| `code`    | `WC`  | FIFA World Cup competition code |
| `stage`   | `GROUP_STAGE` | Enum value from API docs; returns only pool/group matches |
| `season`  | `2026` | Optional; defaults to current season |

Additional useful filter:
```
GET /v4/competitions/WC/matches?stage=GROUP_STAGE&group=GROUP_A
```

Response shape (relevant fields):
```json
{
  "filters": { "stage": "GROUP_STAGE" },
  "resultSet": { "count": 48, "played": 12 },
  "matches": [
    {
      "id": 12345,
      "utcDate": "2026-06-11T20:00:00Z",
      "status": "SCHEDULED",
      "stage": "GROUP_STAGE",
      "group": "GROUP_A",
      "homeTeam": { "id": 9, "name": "USA", "tla": "USA", "crest": "..." },
      "awayTeam": { "id": 762, "name": "Mexico", "tla": "MEX", "crest": "..." },
      "score": {
        "winner": null,
        "fullTime": { "home": null, "away": null }
      }
    }
  ]
}
```

### Throttling policy (source: policies page)

| Plan   | Limit              |
|--------|--------------------|
| Free   | 10 requests/minute |
| Standard | 30 requests/minute |
| Full   | 60 requests/minute |

HTTP 429 is returned when the limit is exceeded. The `X-Requests-Available-Minute`
response header reports remaining capacity.

---

## User Scenarios & Testing

### User Story 1 — Matches tab shows live group-stage matches (P1)

A user opens the Matches tab. The group-stage matches fetched from
football-data.org are displayed, grouped by FIFA group (A–L).

**Acceptance Scenarios**:

1. **Given** a valid API key is configured, **When** the Matches tab loads,
   **Then** a `FootballDataClient.get_group_matches()` call is issued and the
   returned matches replace the static data.
2. **Given** the API responds with 48 group-stage matches, **When** rendered,
   **Then** all 48 matches appear, each showing home team, away team, date/time,
   and score (or "vs" if not yet played).
3. **Given** no API key is set, **When** the Matches tab loads, **Then** a
   user-visible warning ("API key not configured — showing cached data") is shown
   and the previous static data is used as fallback.
4. **Given** the API returns HTTP 4xx/5xx, **When** the client handles the error,
   **Then** the error is logged, the fallback static data is shown, and no
   unhandled exception propagates to the UI.

### User Story 2 — Throttle compliance (P1)

The client never violates the free-plan 10-requests/minute cap.

**Acceptance Scenarios**:

1. **Given** 10 requests have been issued within 60 seconds, **When** an 11th
   request is triggered, **Then** the client waits until the window resets before
   sending.
2. **Given** the API returns HTTP 429, **When** the client receives it, **Then**
   it backs off for 60 seconds and retries once before returning a cached/fallback
   result.
3. **Given** the app is open for an extended period and the user navigates away
   and back to the Matches tab, **When** `get_group_matches()` is called again,
   **Then** the client serves a cached response if the TTL (5 minutes) has not
   expired, issuing no network request.

### User Story 3 — Group filter (P2)

A user selects a specific group (e.g. "Group A") from a dropdown. Only the
matches for that group are shown.

**Acceptance Scenarios**:

1. **Given** the user selects "Group B", **When** the filter is applied, **Then**
   only Group B matches are shown — the client calls
   `get_group_matches(group="GROUP_B")` using a cached full-fetch, not a new
   network call.

---

## Technical Design

### New module: `src/services/football_data_client.py`

```python
class FootballDataClient:
    BASE_URL = "https://api.football-data.org/v4"
    COMPETITION = "WC"
    # Free plan: 10 req/min → minimum inter-request gap = 6 s
    MIN_INTERVAL_S = 6.0
    CACHE_TTL_S = 300  # 5 minutes

    def __init__(self, api_key: str | None = None): ...
    def get_group_matches(self, group: str | None = None) -> list[dict]: ...
    def _fetch(self, path: str, params: dict) -> dict: ...
    def _throttle(self) -> None: ...  # token-bucket / sliding window
```

**Throttle implementation**:
- Track `_last_request_time: float` (monotonic clock).
- Before each request, compute elapsed = `time.monotonic() - _last_request_time`.
- If `elapsed < MIN_INTERVAL_S`, call `time.sleep(MIN_INTERVAL_S - elapsed)`.
- On HTTP 429, sleep 60 s and retry once.

**Caching**:
- After a successful fetch, store `(timestamp, data)` in `_cache: dict[str, tuple]`.
- On subsequent calls within TTL, return cached data without a network request.

**Environment variable**:
- Key: `FOOTBALL_DATA_API_KEY`
- Read via `os.environ.get("FOOTBALL_DATA_API_KEY")` in `__init__`.
- If `None`, `get_group_matches()` raises `ApiKeyMissingError` (custom exception).

**Request headers**:
```python
headers = {
    "X-Auth-Token": self._api_key,
    "Accept": "application/json",
}
```

**HTTP client**: stdlib `urllib.request` (no external dependency) or `httpx` if
already a project dependency. Prefer `urllib.request` for zero additional deps.

### Integration point

`src/views/matches_view.py` is updated to:
1. Instantiate `FootballDataClient` (or receive it via DI from `main.py`).
2. Call `get_group_matches()` asynchronously (Flet `page.run_thread`) on tab
   activation.
3. Display a loading spinner while the request is in-flight.
4. Fall back to `WorldCupDataService` static data on `ApiKeyMissingError` or
   network error.

### Data contract — Match item

| Field | Type | Source |
|-------|------|--------|
| `id` | `int` | API |
| `utcDate` | `str` (ISO-8601) | API |
| `status` | `str` (enum: SCHEDULED, IN_PLAY, FINISHED, …) | API |
| `stage` | `str` | API |
| `group` | `str` (GROUP_A … GROUP_L) | API |
| `homeTeam.name` | `str` | API |
| `awayTeam.name` | `str` | API |
| `score.fullTime.home` | `int \| None` | API |
| `score.fullTime.away` | `int \| None` | API |

---

## Configuration

`src/config.py` (new or extend existing):
```python
import os

FOOTBALL_DATA_API_KEY: str | None = os.environ.get("FOOTBALL_DATA_API_KEY")
FOOTBALL_DATA_THROTTLE_INTERVAL_S: float = float(
    os.environ.get("FOOTBALL_DATA_THROTTLE_INTERVAL_S", "6.0")
)
FOOTBALL_DATA_CACHE_TTL_S: int = int(
    os.environ.get("FOOTBALL_DATA_CACHE_TTL_S", "300")
)
```

A `.env.example` file documents the required variable:
```
FOOTBALL_DATA_API_KEY=your_token_here
```

---

## Out of Scope

- Knock-out / elimination round matches (spec 006+)
- Live score polling / push updates
- Persisting responses to disk cache
- Scorers / standings sub-resources

---

## Open Questions

1. **Competition code for WC 2026** — The docs show codes like `PL`, `WC`. Needs
   confirmation by making an unauthenticated call to
   `GET /v4/competitions` and checking for the FIFA World Cup entry. The code is
   very likely `WC` but must be verified before implementation.
2. **Free vs paid tier** — If the user has a paid API key the throttle interval
   can be reduced. `FootballDataClient` should read tier from env
   (`FOOTBALL_DATA_PLAN=FREE|STANDARD|FULL`) and adjust `MIN_INTERVAL_S`
   accordingly (6 s / 2 s / 1 s).
3. **Season parameter** — Since the 2026 tournament runs in 2026, the API should
   default to it as "current season". A `?season=2026` parameter should be added
   defensively.
