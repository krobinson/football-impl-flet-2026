"""Tournament progression service — pure query functions over the DataStore matches DataFrame."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

__all__ = [
    "MatchRow",
    "RoundGroup",
    "TeamProgression",
    "get_team_progression",
    "get_teams_for_year",
]

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Round ordering
# ---------------------------------------------------------------------------

# Normalised key → priority.  Keys are produced by _normalise_stage().
# Lower number = earlier in the tournament.
_KNOCKOUT_PRIORITY: dict[str, int] = {
    # 2026 extra round (48-team format)
    "roundof32": 15,
    # Standard round of 16
    "roundof16": 20,
    # Quarter-finals — "Quarter-finals" → "quarterfinals", "Quarterfinals" → "quarterfinals",
    # "Quarter-final" (2026 singular) → "quarterfinal"
    "quarterfinals": 30,
    "quarterfinal": 30,
    # Semi-finals — "Semi-finals" → "semifinals", "Semifinals" → "semifinals",
    # "Semi-final" (2026 singular) → "semifinal"
    "semifinals": 40,
    "semifinal": 40,
    # Final
    "final": 60,
    # 1950 used "Final Round" (round-robin final stage)
    "finalround": 60,
}

_THIRD_PLACE_RE = re.compile(
    r"^(match for third place|third place|third-place|third-place play-off|third place play-off)",
    re.IGNORECASE,
)
_MATCHDAY_RE = re.compile(r"matchday\s*(\d+)", re.IGNORECASE)


def _normalise_stage(stage: str) -> str:
    """Return a compact lowercase key used for priority lookup.

    Strips whitespace, hyphens, and spaces so that variants like
    ``Quarter-finals``, ``Quarterfinals``, and ``Quarter-final`` all
    collapse to ``quarterfinals``.
    """
    return re.sub(r"[\s\-]", "", stage).lower()


def _round_priority(stage: str) -> int:
    """Return a sort key for *stage*; lower = earlier in the tournament."""
    if not stage:
        return 99
    md = _MATCHDAY_RE.match(stage)
    if md:
        return int(md.group(1))  # 1..17
    if _THIRD_PLACE_RE.match(stage):
        return 50
    key = _normalise_stage(stage)
    return _KNOCKOUT_PRIORITY.get(key, 99)


def _display_name(stage: str) -> str:
    """Human-readable round label for the given stage string."""
    if not stage:
        return "Unknown Stage"
    md = _MATCHDAY_RE.match(stage)
    if md:
        return f"Group Stage – Matchday {md.group(1)}"
    if _THIRD_PLACE_RE.match(stage):
        return "Third Place Play-off"
    # Normalise variant spellings to canonical display names
    key = _normalise_stage(stage)
    _CANONICAL: dict[str, str] = {
        "quarterfinals": "Quarter-finals",
        "quarterfinal": "Quarter-finals",
        "semifinals": "Semi-finals",
        "semifinal": "Semi-finals",
        "roundof16": "Round of 16",
        "roundof32": "Round of 32",
        "final": "Final",
        "finalround": "Final Round",
    }
    return _CANONICAL.get(key, stage)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_team_progression(
    matches_df: pd.DataFrame,
    year: int,
    team: str | None = None,
) -> TeamProgression:
    """Return the ordered round-by-round progression for *year*.

    Parameters
    ----------
    matches_df:
        The ``store.matches`` DataFrame (columns: year, match_id, stage, group,
        home_team, away_team, home_score, away_score, aet, et_home, et_away,
        pen_home, pen_away).
    year:
        World Cup edition year.
    team:
        If given, only matches involving this team are included.
        If ``None``, all matches for the edition are included.

    Returns
    -------
    TeamProgression
        Dataclass with ``rounds`` ordered from earliest to latest stage.
    """
    if matches_df.empty:
        return TeamProgression(year=year, team=team)

    mask = matches_df["year"] == year
    if team is not None:
        mask &= (matches_df["home_team"] == team) | (matches_df["away_team"] == team)

    subset = matches_df[mask]
    if subset.empty:
        return TeamProgression(year=year, team=team)

    # Group by stage
    groups: dict[str, RoundGroup] = {}
    for _, row in subset.iterrows():
        stage = str(row.get("stage") or "").strip() or "Unknown Stage"
        if stage not in groups:
            groups[stage] = RoundGroup(
                round_name=_display_name(stage),
                round_priority=_round_priority(stage),
            )
        groups[stage].matches.append(
            MatchRow(
                match_id=str(row["match_id"]),
                stage=stage,
                group=row.get("group") or None,
                home_team=str(row["home_team"]),
                away_team=str(row["away_team"]),
                home_score=int(row["home_score"]),
                away_score=int(row["away_score"]),
                aet=bool(row.get("aet", False)),
                et_home=_int_or_none(row.get("et_home")),
                et_away=_int_or_none(row.get("et_away")),
                pen_home=_int_or_none(row.get("pen_home")),
                pen_away=_int_or_none(row.get("pen_away")),
            )
        )

    sorted_rounds = sorted(groups.values(), key=lambda rg: rg.round_priority)
    return TeamProgression(year=year, team=team, rounds=sorted_rounds)


def get_teams_for_year(matches_df: pd.DataFrame, year: int) -> list[str]:
    """Return sorted list of canonical team names that played in *year*."""
    mask = matches_df["year"] == year
    subset = matches_df[mask]
    if subset.empty:
        return []
    teams = set(subset["home_team"].tolist()) | set(subset["away_team"].tolist())
    return sorted(teams)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _int_or_none(value) -> int | None:
    try:
        if value is None or (hasattr(value, "__float__") and pd.isna(value)):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
