# Interface Contract: `get_team_progression`

**Module**: `src/features/tournament/services`  
**Type**: Pure Python function — no side effects, no I/O  
**Consumer**: `src/features/tournament/views/tournament_view.py`

---

## Signature

```python
from __future__ import annotations

import pandas as pd
from dataclasses import dataclass, field


@dataclass
class MatchRow:
    match_id: str
    stage: str
    group: str | None
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    aet: bool
    et_home: int | None
    et_away: int | None
    pen_home: int | None
    pen_away: int | None


@dataclass
class RoundGroup:
    round_name: str
    round_priority: int
    matches: list[MatchRow] = field(default_factory=list)


@dataclass
class TeamProgression:
    year: int
    team: str | None
    rounds: list[RoundGroup] = field(default_factory=list)


def get_team_progression(
    matches_df: pd.DataFrame,
    year: int,
    team: str | None = None,
) -> TeamProgression:
    """
    Return the ordered round-by-round progression for `year`.

    Parameters
    ----------
    matches_df:
        The ``store.matches`` DataFrame.
    year:
        World Cup edition year.
    team:
        If given, only matches involving this team are included.
        If None, all matches for the edition are included.

    Returns
    -------
    TeamProgression
        Dataclass with ``rounds`` ordered from earliest to latest stage.
    """
    ...
```

---

## Behaviour Contract

| Precondition | Postcondition |
|---|---|
| `matches_df` is a valid DataFrame with expected columns | Function returns without raising |
| `year` is present in `matches_df["year"]` | `TeamProgression.rounds` is non-empty |
| `year` is NOT present in `matches_df["year"]` | `TeamProgression.rounds` is empty list |
| `team` is `None` | All matches for `year` are included across all rounds |
| `team` is a valid team name for the year | Only that team's matches appear |
| `team` is a name that played no matches in `year` | `TeamProgression.rounds` is empty list |
| Any `stage` field is blank/None | It is replaced with `"Unknown Stage"` |

---

## Round Priority Rules

- Stage strings starting with `"Matchday"` → group stage; priority = matchday number (1–13).
- `"Round of 16"` → priority 20
- `"Quarter-finals"` → priority 30
- `"Semi-finals"` → priority 40
- Strings matching `"Match for third place"` / `"Third place*"` / `"Third-place*"` → priority 50
- `"Final"` → priority 60
- Anything else → priority 99, label = original string

---

## Example Usage

```python
store = get_data_store()
prog = get_team_progression(store.matches, year=2022, team="Argentina")
for rg in prog.rounds:
    print(rg.round_name)
    for m in rg.matches:
        print(f"  {m.home_team} {m.home_score}–{m.away_score} {m.away_team}")
```

Expected output (abbreviated):
```
Group Stage – Matchday 1
  Argentina 1–2 Saudi Arabia
Group Stage – Matchday 2
  ...
Round of 16
  ...
Final
  Argentina 3–3 France  (AET, pens 4–2)
```
