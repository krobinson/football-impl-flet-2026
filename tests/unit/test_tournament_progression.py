"""Unit tests for features.tournament.services — tournament progression queries.

TDD: tests written before implementation is finalised. Run with:
    uv run pytest tests/unit/test_tournament_progression.py -v
"""
from __future__ import annotations

import pandas as pd
import pytest

from features.tournament.services import (
    MatchRow,
    RoundGroup,
    TeamProgression,
    get_team_progression,
    get_teams_for_year,
    _round_priority,
    _display_name,
)


# ---------------------------------------------------------------------------
# Fixtures  (T004)
# ---------------------------------------------------------------------------

def _make_match(
    year: int,
    idx: int,
    stage: str,
    home: str,
    away: str,
    hs: int = 1,
    as_: int = 0,
    aet: bool = False,
    et_home=None,
    et_away=None,
    pen_home=None,
    pen_away=None,
    group=None,
) -> dict:
    return {
        "year": year,
        "match_id": f"{year}_{idx:04d}",
        "stage": stage,
        "group": group,
        "home_team": home,
        "away_team": away,
        "home_score": hs,
        "away_score": as_,
        "aet": aet,
        "et_home": et_home,
        "et_away": et_away,
        "pen_home": pen_home,
        "pen_away": pen_away,
    }


@pytest.fixture
def matches_2022() -> pd.DataFrame:
    """Minimal 2022-like dataset: Argentina journey + some other teams."""
    rows = [
        # Group stage – Argentina
        _make_match(2022, 0, "Matchday 1", "Argentina", "Saudi Arabia", 1, 2, group="C"),
        _make_match(2022, 1, "Matchday 2", "Argentina", "Mexico",       2, 0, group="C"),
        _make_match(2022, 2, "Matchday 3", "Argentina", "Poland",       2, 0, group="C"),
        # Group stage – other teams (Saudi Arabia only group stage)
        _make_match(2022, 3, "Matchday 1", "France",    "Australia",    4, 1, group="D"),
        _make_match(2022, 4, "Matchday 2", "France",    "Denmark",      2, 1, group="D"),
        _make_match(2022, 5, "Matchday 3", "France",    "Tunisia",      0, 1, group="D"),
        # Knockout
        _make_match(2022, 6, "Round of 16",   "Argentina", "Australia",  2, 1),
        _make_match(2022, 7, "Quarter-finals", "Argentina", "Netherlands", 2, 2,
                    aet=True, et_home=2, et_away=2, pen_home=4, pen_away=3),
        _make_match(2022, 8, "Semi-finals",    "Argentina", "Croatia",    3, 0),
        _make_match(2022, 9, "Final",          "Argentina", "France",     3, 3,
                    aet=True, et_home=3, et_away=3, pen_home=4, pen_away=2),
        # Third place
        _make_match(2022, 10, "Match for third place", "Croatia", "Morocco", 2, 1),
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def matches_2018() -> pd.DataFrame:
    """Minimal 2018-like dataset: Germany exits group stage."""
    rows = [
        _make_match(2018, 0, "Matchday 1", "Germany", "Mexico",    0, 1, group="F"),
        _make_match(2018, 1, "Matchday 2", "Germany", "Sweden",    2, 1, group="F"),
        _make_match(2018, 2, "Matchday 3", "Germany", "South Korea", 0, 2, group="F"),
        _make_match(2018, 3, "Round of 16",  "France",  "Argentina", 4, 3),
        _make_match(2018, 4, "Final",        "France",  "Croatia",   4, 2),
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def matches_combined(matches_2022, matches_2018) -> pd.DataFrame:
    return pd.concat([matches_2022, matches_2018], ignore_index=True)


# ---------------------------------------------------------------------------
# _round_priority helpers
# ---------------------------------------------------------------------------

class TestRoundPriority:
    def test_matchday_1(self):
        assert _round_priority("Matchday 1") == 1

    def test_matchday_13(self):
        assert _round_priority("Matchday 13") == 13

    def test_matchday_15(self):
        """32-team tournaments use up to Matchday 15."""
        assert _round_priority("Matchday 15") == 15

    def test_matchday_17(self):
        """2026 48-team tournament uses up to Matchday 17."""
        assert _round_priority("Matchday 17") == 17

    def test_round_of_32(self):
        """2026 extra knockout round must sort before Round of 16."""
        assert _round_priority("Round of 32") == 15
        assert _round_priority("Round of 32") < _round_priority("Round of 16")

    def test_round_of_16(self):
        assert _round_priority("Round of 16") == 20

    def test_quarter_finals_hyphenated(self):
        assert _round_priority("Quarter-finals") == 30

    def test_quarter_finals_no_hyphen(self):
        """2006/2010 data uses 'Quarterfinals' (no hyphen)."""
        assert _round_priority("Quarterfinals") == 30

    def test_quarter_final_singular(self):
        """2026 data uses 'Quarter-final' (singular)."""
        assert _round_priority("Quarter-final") == 30

    def test_semi_finals_hyphenated(self):
        assert _round_priority("Semi-finals") == 40

    def test_semi_finals_no_hyphen(self):
        """2006/2010 data uses 'Semifinals' (no hyphen)."""
        assert _round_priority("Semifinals") == 40

    def test_semi_final_singular(self):
        """2026 data uses 'Semi-final' (singular)."""
        assert _round_priority("Semi-final") == 40

    def test_knockout_order(self):
        """All knockout rounds sort in correct tournament order."""
        stages = ["Final", "Semi-finals", "Quarter-finals", "Round of 16",
                  "Matchday 3", "Matchday 1"]
        expected = ["Matchday 1", "Matchday 3", "Round of 16",
                    "Quarter-finals", "Semi-finals", "Final"]
        assert sorted(stages, key=_round_priority) == expected

    def test_third_place_variants(self):
        assert _round_priority("Match for third place") == 50
        assert _round_priority("Third place match") == 50
        assert _round_priority("Third-place match") == 50
        assert _round_priority("Third place play-off") == 50
        assert _round_priority("Third-place play-off") == 50

    def test_final(self):
        assert _round_priority("Final") == 60

    def test_final_round_1950(self):
        """1950 'Final Round' (round-robin final group) should sort as Final."""
        assert _round_priority("Final Round") == 60

    def test_unknown_stage(self):
        assert _round_priority("Group stage round robin") == 99

    def test_blank_stage(self):
        assert _round_priority("") == 99


class TestDisplayName:
    def test_matchday(self):
        assert _display_name("Matchday 1") == "Group Stage – Matchday 1"

    def test_blank(self):
        assert _display_name("") == "Unknown Stage"

    def test_known_knockout(self):
        assert _display_name("Quarter-finals") == "Quarter-finals"

    def test_quarterfinals_no_hyphen(self):
        """2006/2010 variant normalises to canonical name."""
        assert _display_name("Quarterfinals") == "Quarter-finals"

    def test_quarter_final_singular(self):
        """2026 singular variant normalises to canonical name."""
        assert _display_name("Quarter-final") == "Quarter-finals"

    def test_semifinals_no_hyphen(self):
        assert _display_name("Semifinals") == "Semi-finals"

    def test_semi_final_singular(self):
        assert _display_name("Semi-final") == "Semi-finals"

    def test_round_of_32(self):
        assert _display_name("Round of 32") == "Round of 32"

    def test_third_place(self):
        assert _display_name("Match for third place") == "Third Place Play-off"

    def test_third_place_variants_all_same(self):
        for v in ["Third place match", "Third-place match", "Third place play-off",
                  "Third-place play-off"]:
            assert _display_name(v) == "Third Place Play-off", f"failed for: {v}"


# ---------------------------------------------------------------------------
# T005 — get_team_progression all-teams (US1)
# ---------------------------------------------------------------------------

class TestGetTeamProgressionAllTeams:
    def test_returns_team_progression_type(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        assert isinstance(prog, TeamProgression)

    def test_year_set(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        assert prog.year == 2022

    def test_team_is_none(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        assert prog.team is None

    def test_rounds_non_empty(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        assert len(prog.rounds) > 0

    def test_rounds_sorted_by_priority(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        priorities = [rg.round_priority for rg in prog.rounds]
        assert priorities == sorted(priorities)

    def test_group_stage_before_knockout(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        names = [rg.round_name for rg in prog.rounds]
        final_idx = next(i for i, n in enumerate(names) if n == "Final")
        group_idx = next(i for i, n in enumerate(names) if "Matchday" in n)
        assert group_idx < final_idx

    def test_all_matches_included(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        total = sum(len(rg.matches) for rg in prog.rounds)
        assert total == len(matches_2022)

    def test_match_row_fields(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        final_rg = next(rg for rg in prog.rounds if rg.round_name == "Final")
        m = final_rg.matches[0]
        assert isinstance(m, MatchRow)
        assert m.home_team == "Argentina"
        assert m.away_team == "France"
        assert m.home_score == 3
        assert m.away_score == 3
        assert m.aet is True
        assert m.pen_home == 4
        assert m.pen_away == 2

    def test_third_place_display_name(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        names = [rg.round_name for rg in prog.rounds]
        assert "Third Place Play-off" in names

    def test_empty_dataframe_returns_empty_rounds(self):
        empty_df = pd.DataFrame(columns=["year", "match_id", "stage", "group",
                                         "home_team", "away_team", "home_score",
                                         "away_score", "aet", "et_home", "et_away",
                                         "pen_home", "pen_away"])
        prog = get_team_progression(empty_df, year=2022)
        assert prog.rounds == []

    def test_year_not_in_data_returns_empty_rounds(self, matches_2022):
        prog = get_team_progression(matches_2022, year=1900)
        assert prog.rounds == []


# ---------------------------------------------------------------------------
# T006 — edge cases (US1)
# ---------------------------------------------------------------------------

class TestGetTeamProgressionEdgeCases:
    def test_blank_stage_becomes_unknown(self):
        rows = [_make_match(2022, 0, "", "TeamA", "TeamB")]
        df = pd.DataFrame(rows)
        prog = get_team_progression(df, year=2022)
        assert len(prog.rounds) == 1
        assert prog.rounds[0].round_name == "Unknown Stage"

    def test_none_stage_becomes_unknown(self):
        row = _make_match(2022, 0, "", "TeamA", "TeamB")
        row["stage"] = None
        df = pd.DataFrame([row])
        prog = get_team_progression(df, year=2022)
        assert prog.rounds[0].round_name == "Unknown Stage"

    def test_et_and_pen_none_for_normal_match(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022)
        md1 = next(rg for rg in prog.rounds if "Matchday 1" in rg.round_name)
        m = md1.matches[0]
        assert m.aet is False
        assert m.et_home is None
        assert m.pen_home is None

    def test_only_current_year_returned(self, matches_combined):
        prog = get_team_progression(matches_combined, year=2022)
        for rg in prog.rounds:
            for m in rg.matches:
                assert m.match_id.startswith("2022")


# ---------------------------------------------------------------------------
# T012 — team filter (US2)
# ---------------------------------------------------------------------------

class TestGetTeamProgressionFiltered:
    def test_only_team_matches_included(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Argentina")
        for rg in prog.rounds:
            for m in rg.matches:
                assert m.home_team == "Argentina" or m.away_team == "Argentina"

    def test_team_set_on_result(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Argentina")
        assert prog.team == "Argentina"

    def test_argentina_reaches_final(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Argentina")
        names = [rg.round_name for rg in prog.rounds]
        assert "Final" in names

    def test_france_reaches_final(self, matches_2022):
        """France has group-stage and Final matches in the fixture."""
        prog = get_team_progression(matches_2022, year=2022, team="France")
        names = [rg.round_name for rg in prog.rounds]
        assert "Final" in names
        assert any("Matchday" in n for n in names)

    def test_saudi_arabia_only_group_stage_rounds(self, matches_2022):
        """Saudi Arabia only has one group-stage match in the fixture."""
        prog = get_team_progression(matches_2022, year=2022, team="Saudi Arabia")
        for rg in prog.rounds:
            assert "Matchday" in rg.round_name

    def test_rounds_still_sorted_when_filtered(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Argentina")
        priorities = [rg.round_priority for rg in prog.rounds]
        assert priorities == sorted(priorities)

    def test_correct_match_count_for_argentina(self, matches_2022):
        """Argentina plays 7 matches in the fixture (3 group + R16 + QF + SF + F)."""
        prog = get_team_progression(matches_2022, year=2022, team="Argentina")
        total = sum(len(rg.matches) for rg in prog.rounds)
        assert total == 7


# ---------------------------------------------------------------------------
# T013 — nonexistent team (US2)
# ---------------------------------------------------------------------------

class TestNonexistentTeam:
    def test_empty_rounds_for_unknown_team(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Nonexistent FC")
        assert prog.rounds == []

    def test_team_still_set_even_when_no_matches(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Nonexistent FC")
        assert prog.team == "Nonexistent FC"


# ---------------------------------------------------------------------------
# T017 — team didn't participate in edition (US3)
# ---------------------------------------------------------------------------

class TestTeamNotParticipating:
    def test_germany_not_in_2022_fixture(self, matches_2022):
        """Germany has no rows in the 2022 fixture data."""
        prog = get_team_progression(matches_2022, year=2022, team="Germany")
        assert prog.rounds == []

    def test_year_with_no_data_returns_empty(self, matches_combined):
        prog = get_team_progression(matches_combined, year=1934, team="Germany")
        assert prog.rounds == []

    def test_team_name_preserved_on_empty_result(self, matches_2022):
        prog = get_team_progression(matches_2022, year=2022, team="Germany")
        assert prog.team == "Germany"
        assert prog.year == 2022


# ---------------------------------------------------------------------------
# get_teams_for_year
# ---------------------------------------------------------------------------

class TestGetTeamsForYear:
    def test_returns_sorted_list(self, matches_2022):
        teams = get_teams_for_year(matches_2022, year=2022)
        assert teams == sorted(teams)

    def test_all_teams_present(self, matches_2022):
        teams = get_teams_for_year(matches_2022, year=2022)
        assert "Argentina" in teams
        assert "France" in teams
        assert "Croatia" in teams

    def test_empty_for_missing_year(self, matches_2022):
        teams = get_teams_for_year(matches_2022, year=1900)
        assert teams == []


# ---------------------------------------------------------------------------
# Regression: stage name variants from real data (2006/2010/2026)
# ---------------------------------------------------------------------------

class TestStageVariantSorting:
    """Ensure stages from different era data files sort in correct order."""

    @pytest.fixture
    def matches_2006_style(self) -> pd.DataFrame:
        """2006/2010 data uses Quarterfinals / Semifinals (no hyphen)."""
        rows = [
            _make_match(2006, 0, "Matchday 3", "Germany", "Ecuador", 3, 0),
            _make_match(2006, 1, "Round of 16", "Germany", "Sweden", 2, 0),
            _make_match(2006, 2, "Quarterfinals", "Germany", "Argentina", 1, 1,
                        aet=True, pen_home=4, pen_away=2),
            _make_match(2006, 3, "Semifinals", "Germany", "Italy", 0, 2),
            _make_match(2006, 4, "Third-place play-off", "Germany", "Portugal", 3, 1),
        ]
        return pd.DataFrame(rows)

    @pytest.fixture
    def matches_2026_style(self) -> pd.DataFrame:
        """2026 data uses Quarter-final / Semi-final (singular) and Round of 32."""
        rows = [
            _make_match(2026, 0, "Matchday 1", "Spain", "Brazil", 2, 1),
            _make_match(2026, 1, "Round of 32", "Spain", "Morocco", 1, 0),
            _make_match(2026, 2, "Round of 16", "Spain", "France", 2, 1),
            _make_match(2026, 3, "Quarter-final", "Spain", "England", 3, 1),
            _make_match(2026, 4, "Semi-final", "Spain", "Germany", 2, 0),
            _make_match(2026, 5, "Final", "Spain", "Argentina", 1, 0),
        ]
        return pd.DataFrame(rows)

    def test_2006_style_sorts_correctly(self, matches_2006_style):
        prog = get_team_progression(matches_2006_style, year=2006, team="Germany")
        names = [rg.round_name for rg in prog.rounds]
        expected = [
            "Group Stage – Matchday 3",
            "Round of 16",
            "Quarter-finals",
            "Semi-finals",
            "Third Place Play-off",
        ]
        assert names == expected

    def test_2026_style_sorts_correctly(self, matches_2026_style):
        prog = get_team_progression(matches_2026_style, year=2026, team="Spain")
        names = [rg.round_name for rg in prog.rounds]
        expected = [
            "Group Stage – Matchday 1",
            "Round of 32",
            "Round of 16",
            "Quarter-finals",
            "Semi-finals",
            "Final",
        ]
        assert names == expected

    def test_quarterfinals_no_hyphen_display(self, matches_2006_style):
        """'Quarterfinals' in data must show as 'Quarter-finals' in UI."""
        prog = get_team_progression(matches_2006_style, year=2006, team="Germany")
        names = [rg.round_name for rg in prog.rounds]
        assert "Quarter-finals" in names
        assert "Quarterfinals" not in names

    def test_semifinals_no_hyphen_display(self, matches_2006_style):
        prog = get_team_progression(matches_2006_style, year=2006, team="Germany")
        names = [rg.round_name for rg in prog.rounds]
        assert "Semi-finals" in names
        assert "Semifinals" not in names
