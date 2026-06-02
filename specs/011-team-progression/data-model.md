# Data Model: Team Tournament Progression

## Entities

### MatchRow (read-only view over `store.matches`)

Represents a single match as it exists in the in-memory DataFrame. No new storage;
this is a typed alias for a row selected from `store.matches`.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `year` | `int` | `store.matches["year"]` | Edition year, e.g. 2022 |
| `match_id` | `str` | `store.matches["match_id"]` | Unique key `<year>_<idx>` |
| `stage` | `str` | `store.matches["stage"]` | Raw round string, e.g. "Round of 16" |
| `group` | `str \| None` | `store.matches["group"]` | Group letter for group-stage matches |
| `home_team` | `str` | `store.matches["home_team"]` | Canonical team name |
| `away_team` | `str` | `store.matches["away_team"]` | Canonical team name |
| `home_score` | `int` | `store.matches["home_score"]` | Full-time goals |
| `away_score` | `int` | `store.matches["away_score"]` | Full-time goals |
| `aet` | `bool` | `store.matches["aet"]` | True if extra time played |
| `et_home` | `int \| None` | `store.matches["et_home"]` | AET score |
| `et_away` | `int \| None` | `store.matches["et_away"]` | AET score |
| `pen_home` | `int \| None` | `store.matches["pen_home"]` | Penalty shootout score |
| `pen_away` | `int \| None` | `store.matches["pen_away"]` | Penalty shootout score |

---

### RoundGroup

A named grouping of matches belonging to the same tournament stage.

| Field | Type | Notes |
|-------|------|-------|
| `round_name` | `str` | Display name, e.g. "Group Stage – Matchday 1" or "Quarter-finals" |
| `round_priority` | `int` | Sort key — lower = earlier in the tournament |
| `matches` | `list[MatchRow]` | All matches in this round for the current filter |

---

### TeamProgression

The output of `get_team_progression()`. Ordered sequence of rounds a team played.

| Field | Type | Notes |
|-------|------|-------|
| `year` | `int` | Edition year |
| `team` | `str \| None` | Filtered team name; `None` means "all teams" |
| `rounds` | `list[RoundGroup]` | Ordered by `round_priority` ascending |

---

## Round Priority Table

| Priority | Stage Identifier Pattern | Display Label |
|----------|--------------------------|---------------|
| 0–12 | `Matchday *` | Group Stage |
| 20 | `Round of 16` | Round of 16 |
| 30 | `Quarter-finals` | Quarter-finals |
| 40 | `Semi-finals` | Semi-finals |
| 50 | `Match for third place`, `Third place *`, `Third-place *` | Third Place Play-off |
| 60 | `Final` | Final |
| 99 | Anything else | (stage name as-is) |

Group-stage matchdays use priority = (matchday number × 1), so Matchday 1 → 1,
Matchday 2 → 2, … Matchday 13 → 13. This guarantees group rounds sort before
knockout rounds.

---

## Validation Rules

- `home_score` and `away_score` MUST be non-negative integers.
- `round_name` MUST NOT be empty; default to `"Unknown Stage"` if `stage` field is blank.
- A `TeamProgression` with `team = None` MUST contain all matches in the edition.
- A `TeamProgression` with a specific `team` MUST contain only matches where
  `home_team == team OR away_team == team`.

---

## State Transitions (View Level)

```
User selects edition ──► progression_service called with (year, team=None)
                         ──► RoundGroups rendered in ExpansionTiles

User selects team   ──► progression_service called with (year, team=selected)
                         ──► Only that team's rounds shown

User clears team    ──► progression_service called with (year, team=None)
                         ──► All teams visible again

User switches edition ► progression_service called with (new_year, team=current)
                         ──► Panel refreshes with new edition data
```
