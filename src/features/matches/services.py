"""DataStore singleton: loads and caches all World Cup historical data as Pandas DataFrames.

Ported from the Panel reference implementation; Panel dependency removed.
Data sourced from openfootball JSON files in data/worldcup/ and FIFA CSVs in data/fifa/.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Team name alias map – normalises historical variants to canonical names
# ---------------------------------------------------------------------------
TEAM_ALIASES: dict[str, str] = {
    "West Germany": "Germany",
    "Federal Republic of Germany": "Germany",
    "German Democratic Republic": "Germany DR",
    "Czechoslovakia": "Czech Republic",
    "Soviet Union": "Russia",
    "Yugoslavia": "Serbia",
    "FR Yugoslavia": "Serbia",
    "Serbia and Montenegro": "Serbia",
    "Dutch East Indies": "Indonesia",
    "Zaire": "DR Congo",
    "China PR": "China",
    "Korea Republic": "South Korea",
    "Korea DPR": "North Korea",
    "Côte d'Ivoire": "Ivory Coast",
    "Trinidad and Tobago": "Trinidad & Tobago",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
}

KNOWN_OUTCOMES: dict[int, dict[str, str]] = {
    1930: {"champion": "Uruguay", "runner_up": "Argentina", "third_place": "United States"},
    1950: {"champion": "Uruguay", "runner_up": "Brazil", "third_place": "Sweden"},
}

_FINAL_ROUNDS = {"Final", "Final Round"}
_THIRD_PLACE_ROUNDS = {
    "Match for third place", "Third place match", "Third place play-off",
    "Third-place match", "Third-place play-off",
}

_KNOWN_HOSTS: dict[int, str] = {
    1930: "Uruguay", 1934: "Italy", 1938: "France", 1950: "Brazil",
    1954: "Switzerland", 1958: "Sweden", 1962: "Chile", 1966: "England",
    1970: "Mexico", 1974: "West Germany", 1978: "Argentina", 1982: "Spain",
    1986: "Mexico", 1990: "Italy", 1994: "United States", 1998: "France",
    2002: "South Korea / Japan", 2006: "Germany", 2010: "South Africa",
    2014: "Brazil", 2018: "Russia", 2022: "Qatar",
}

_DATA_ROOT = Path(__file__).resolve().parents[3] / "data"
_WC_DIR = _DATA_ROOT / "worldcup"
_FIFA_DIR = _DATA_ROOT / "fifa"


def _canonical(name: str) -> str:
    return TEAM_ALIASES.get(name, name)


def _winner(
    score_ft: list[int],
    team1: str,
    team2: str,
    score_et: Optional[list[int]] = None,
    score_p: Optional[list[int]] = None,
) -> tuple[str, str]:
    h, a = score_ft
    if h > a:
        return team1, team2
    if a > h:
        return team2, team1
    if score_et:
        eh, ea = score_et
        if eh > ea:
            return team1, team2
        if ea > eh:
            return team2, team1
    if score_p:
        ph, pa = score_p
        if ph > pa:
            return team1, team2
        if pa > ph:
            return team2, team1
    return team1, team2


def _parse_year(year: int, year_dir: Path) -> tuple[dict, list[dict], list[dict]]:
    json_path = year_dir / "worldcup.json"
    if not json_path.exists():
        return {}, [], []

    with open(json_path, encoding="utf-8") as fh:
        data = json.load(fh)

    raw_matches = data.get("matches", [])
    matches: list[dict] = []
    events: list[dict] = []
    total_goals = 0
    teams_seen: set[str] = set()

    for idx, m in enumerate(raw_matches):
        match_id = f"{year}_{idx:04d}"
        team1 = _canonical(m.get("team1", ""))
        team2 = _canonical(m.get("team2", ""))
        teams_seen.add(team1)
        teams_seen.add(team2)

        score = m.get("score", {})
        ft = score.get("ft", [0, 0])
        et = score.get("et")
        pen = score.get("p")

        home_score, away_score = ft[0], ft[1]
        aet = et is not None
        total_goals += home_score + away_score

        matches.append({
            "year": year,
            "match_id": match_id,
            "stage": m.get("round", ""),
            "group": m.get("group"),
            "date": m.get("date", ""),
            "venue": m.get("ground", ""),
            "home_team": team1,
            "away_team": team2,
            "home_score": home_score,
            "away_score": away_score,
            "aet": aet,
            "et_home": et[0] if et else None,
            "et_away": et[1] if et else None,
            "pen_home": pen[0] if pen else None,
            "pen_away": pen[1] if pen else None,
        })

        for _, goal_list, team in [
            ("goals1", m.get("goals1", []) or [], team1),
            ("goals2", m.get("goals2", []) or [], team2),
        ]:
            for g in goal_list:
                own = g.get("owngoal", False)
                penalty = g.get("penalty", False)
                if own:
                    event_type = "own_goal"
                    credited_team = team2 if team == team1 else team1
                elif penalty:
                    event_type = "penalty_goal"
                    credited_team = team
                else:
                    event_type = "goal"
                    credited_team = team
                events.append({
                    "year": year,
                    "match_id": match_id,
                    "team": credited_team,
                    "player": g.get("name", "Unknown"),
                    "minute": g.get("minute"),
                    "event_type": event_type,
                })

    if year in KNOWN_OUTCOMES:
        champion = KNOWN_OUTCOMES[year]["champion"]
        runner_up = KNOWN_OUTCOMES[year]["runner_up"]
        third_place = KNOWN_OUTCOMES[year]["third_place"]
    else:
        champion = runner_up = third_place = ""
        for md in matches:
            stage = md["stage"]
            if stage in _FINAL_ROUNDS:
                et_ = [md["et_home"], md["et_away"]] if md["aet"] else None
                p_ = [md["pen_home"], md["pen_away"]] if md["pen_home"] is not None else None
                winner, loser = _winner([md["home_score"], md["away_score"]],
                                       md["home_team"], md["away_team"], et_, p_)
                champion, runner_up = winner, loser
            elif stage in _THIRD_PLACE_ROUNDS:
                winner, _ = _winner([md["home_score"], md["away_score"]],
                                    md["home_team"], md["away_team"])
                third_place = winner

    tournament_info = {
        "year": year,
        "host": _KNOWN_HOSTS.get(year, ""),
        "champion": champion,
        "runner_up": runner_up,
        "third_place": third_place,
        "goals": total_goals,
        "matches": len(matches),
        "teams": len(teams_seen),
    }
    return tournament_info, matches, events


class DataStore:
    """Singleton that loads all World Cup data into Pandas DataFrames."""

    _instance: Optional["DataStore"] = None

    def __new__(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self) -> None:
        if self._loaded:
            return

        all_tournaments: list[dict] = []
        all_matches: list[dict] = []
        all_events: list[dict] = []

        if _WC_DIR.exists():
            for entry in sorted(_WC_DIR.iterdir()):
                if not entry.is_dir():
                    continue
                try:
                    year = int(entry.name)
                except ValueError:
                    continue
                if year >= 2026:
                    continue
                t_info, matches, events = _parse_year(year, entry)
                if t_info:
                    all_tournaments.append(t_info)
                    all_matches.extend(matches)
                    all_events.extend(events)

        self.tournaments: pd.DataFrame = (
            pd.DataFrame(all_tournaments).sort_values("year").reset_index(drop=True)
            if all_tournaments
            else pd.DataFrame(columns=["year", "host", "champion", "runner_up",
                                       "third_place", "goals", "matches", "teams"])
        )
        self.matches: pd.DataFrame = (
            pd.DataFrame(all_matches).reset_index(drop=True)
            if all_matches
            else pd.DataFrame(columns=["year", "match_id", "stage", "group", "date",
                                       "venue", "home_team", "away_team",
                                       "home_score", "away_score", "aet",
                                       "et_home", "et_away", "pen_home", "pen_away"])
        )
        self.match_events: pd.DataFrame = (
            pd.DataFrame(all_events).reset_index(drop=True)
            if all_events
            else pd.DataFrame(columns=["year", "match_id", "team", "player",
                                       "minute", "event_type"])
        )

        self.team_standings: pd.DataFrame = self._derive_team_standings()

        top_path = _FIFA_DIR / "top_scorers.csv"
        app_path = _FIFA_DIR / "appearances.csv"
        self.top_scorers: pd.DataFrame = (
            pd.read_csv(top_path) if top_path.exists()
            else pd.DataFrame(columns=["player", "team", "goals", "tournaments", "years"])
        )
        self.appearances: pd.DataFrame = (
            pd.read_csv(app_path) if app_path.exists()
            else pd.DataFrame(columns=["player", "team", "matches", "tournaments"])
        )

        self._loaded = True

    def _derive_team_standings(self) -> pd.DataFrame:
        if self.matches.empty:
            return pd.DataFrame(columns=["year", "team", "played", "wins", "draws",
                                         "losses", "goals_for", "goals_against",
                                         "goal_diff", "stage_reached"])
        rows: list[dict] = []
        for _, m in self.matches.iterrows():
            year = m["year"]
            h, a = m["home_team"], m["away_team"]
            hs, as_ = int(m["home_score"]), int(m["away_score"])
            stage = m["stage"]
            h_res, a_res = (("win", "loss") if hs > as_ else
                            ("loss", "win") if as_ > hs else ("draw", "draw"))
            rows.append({"year": year, "team": h, "result": h_res,
                         "goals_for": hs, "goals_against": as_, "stage": stage})
            rows.append({"year": year, "team": a, "result": a_res,
                         "goals_for": as_, "goals_against": hs, "stage": stage})

        df = pd.DataFrame(rows)
        standings = df.groupby(["year", "team"]).agg(
            played=("result", "count"),
            wins=("result", lambda x: (x == "win").sum()),
            draws=("result", lambda x: (x == "draw").sum()),
            losses=("result", lambda x: (x == "loss").sum()),
            goals_for=("goals_for", "sum"),
            goals_against=("goals_against", "sum"),
        ).reset_index()

        last_stage = (df.groupby(["year", "team"])["stage"]
                      .last().reset_index()
                      .rename(columns={"stage": "stage_reached"}))
        standings = standings.merge(last_stage, on=["year", "team"], how="left")
        standings["goal_diff"] = standings["goals_for"] - standings["goals_against"]
        return standings.sort_values(["year", "team"]).reset_index(drop=True)

    @property
    def all_teams(self) -> list[str]:
        if not self._loaded:
            self.load()
        return sorted(self.team_standings["team"].unique().tolist())

    @property
    def all_years(self) -> list[int]:
        if not self._loaded:
            self.load()
        return sorted(self.tournaments["year"].tolist())


_store_singleton: Optional[DataStore] = None


def get_data_store() -> DataStore:
    """Return the loaded DataStore singleton."""
    global _store_singleton
    if _store_singleton is None:
        _store_singleton = DataStore()
        _store_singleton.load()
    return _store_singleton
