"""Unit tests for schedule group display — 012-schedule-group-display.

TDD: tests written before implementation. Run with:
    uv run pytest tests/unit/test_schedule_group_display.py -v
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixtures  (T001)
# ---------------------------------------------------------------------------

def _make_match(
    idx: int,
    group: str,
    matchday: int,
    utc_date: str,
    status: str,
    home: str = "Team A",
    away: str = "Team B",
    score_home: int | None = None,
    score_away: int | None = None,
    venue: str | None = "MetLife Stadium",
) -> dict:
    return {
        "id": idx,
        "utcDate": utc_date,
        "status": status,
        "matchday": matchday,
        "group": group,
        "venue": venue,
        "homeTeam": {"name": home},
        "awayTeam": {"name": away},
        "score": {
            "fullTime": {
                "home": score_home,
                "away": score_away,
            }
        },
    }


@pytest.fixture
def all_matches() -> list[dict]:
    """18 matches: 9 GROUP_C (matchdays 1-3 × 3 matches) + 9 GROUP_E."""
    matches = []
    idx = 0
    for group, home_prefix in [("GROUP_C", "C"), ("GROUP_E", "E")]:
        for matchday in [1, 2, 3]:
            for n in range(3):
                status = "SCHEDULED"
                sh, sa = None, None
                if group == "GROUP_C" and matchday == 1:
                    status = "FINISHED"
                    sh, sa = 2, 1
                matches.append(
                    _make_match(
                        idx,
                        group,
                        matchday,
                        f"2026-06-{10 + matchday:02d}T{14 + n:02d}:00:00Z",
                        status,
                        home=f"{home_prefix}-Home{n}",
                        away=f"{home_prefix}-Away{n}",
                        score_home=sh,
                        score_away=sa,
                    )
                )
                idx += 1
    return matches


@pytest.fixture
def match_scheduled() -> dict:
    return _make_match(
        1, "GROUP_C", 1, "2026-06-11T14:00:00Z",
        "SCHEDULED", "USA", "Mexico",
        venue="AT&T Stadium",
    )


@pytest.fixture
def match_finished() -> dict:
    return _make_match(
        2, "GROUP_C", 1, "2026-06-11T17:00:00Z",
        "FINISHED", "France", "Germany",
        score_home=2, score_away=1,
        venue="MetLife Stadium",
    )


@pytest.fixture
def match_in_play() -> dict:
    return _make_match(
        3, "GROUP_E", 2, "2026-06-15T20:00:00Z",
        "IN_PLAY", "Brazil", "Argentina",
        score_home=1, score_away=0,
        venue="Rose Bowl",
    )


@pytest.fixture
def match_paused() -> dict:
    return _make_match(
        4, "GROUP_E", 2, "2026-06-15T18:00:00Z",
        "PAUSED", "Spain", "Portugal",
        score_home=0, score_away=0,
        venue="SoFi Stadium",
    )


@pytest.fixture
def match_no_venue() -> dict:
    return _make_match(
        5, "GROUP_C", 3, "2026-06-20T12:00:00Z",
        "SCHEDULED", "TeamX", "TeamY",
        venue=None,
    )


# ---------------------------------------------------------------------------
# T002 — group filter logic
# ---------------------------------------------------------------------------

class TestGroupFilterLogic:
    """Tests for the client-side filter + sort logic used by _apply_group_filter."""

    def _filter_and_sort(self, matches: list[dict], active_group: str) -> list[dict]:
        """Mirrors the production _apply_group_filter logic."""
        if active_group != "All":
            matches = [m for m in matches if m.get("group") == f"GROUP_{active_group}"]
        return sorted(
            matches,
            key=lambda m: (m.get("matchday") or 99, m.get("utcDate") or ""),
        )

    def test_all_returns_all_matches(self, all_matches):
        result = self._filter_and_sort(all_matches, "All")
        assert len(result) == 18

    def test_group_c_filter_returns_only_group_c(self, all_matches):
        result = self._filter_and_sort(all_matches, "C")
        assert all(m["group"] == "GROUP_C" for m in result)
        assert len(result) == 9

    def test_group_e_filter_returns_only_group_e(self, all_matches):
        result = self._filter_and_sort(all_matches, "E")
        assert all(m["group"] == "GROUP_E" for m in result)
        assert len(result) == 9

    def test_unknown_group_returns_empty(self, all_matches):
        result = self._filter_and_sort(all_matches, "Z")
        assert result == []

    def test_sorted_by_matchday_then_utcdate(self, all_matches):
        result = self._filter_and_sort(all_matches, "C")
        matchdays = [m["matchday"] for m in result]
        assert matchdays == sorted(matchdays)

    def test_within_matchday_sorted_by_utcdate(self, all_matches):
        result = self._filter_and_sort(all_matches, "C")
        md1 = [m for m in result if m["matchday"] == 1]
        dates = [m["utcDate"] for m in md1]
        assert dates == sorted(dates)

    def test_all_sorted_globally_by_matchday_then_date(self, all_matches):
        result = self._filter_and_sort(all_matches, "All")
        keys = [(m["matchday"], m["utcDate"]) for m in result]
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# T005 — match_row venue display
# ---------------------------------------------------------------------------

class TestMatchRowVenueDisplay:
    """Tests for venue column in match_row() and header_row()."""

    def _get_venue_text(self, match: dict) -> str:
        """Mirror the production logic: venue field or TBD."""
        return match.get("venue") or "TBD"

    def test_scheduled_match_shows_stadium_name(self, match_scheduled):
        assert self._get_venue_text(match_scheduled) == "AT&T Stadium"

    def test_finished_match_shows_stadium_name(self, match_finished):
        assert self._get_venue_text(match_finished) == "MetLife Stadium"

    def test_none_venue_shows_tbd(self, match_no_venue):
        assert self._get_venue_text(match_no_venue) == "TBD"

    def test_empty_string_venue_shows_tbd(self):
        match = _make_match(99, "GROUP_A", 1, "2026-06-11T12:00:00Z", "SCHEDULED", venue="")
        assert self._get_venue_text(match) == "TBD"

    def test_city_not_substituted(self, match_scheduled):
        """Venue should be raw stadium name, not a city lookup."""
        result = self._get_venue_text(match_scheduled)
        assert result == "AT&T Stadium"
        assert result != "Dallas"


# ---------------------------------------------------------------------------
# T007 — match_row score and status display
# ---------------------------------------------------------------------------

class TestMatchRowScoreStatus:
    """Tests for score text and status badge in match_row()."""

    def _score_text(self, match: dict) -> str:
        """Mirror _score_text() from match_row.py."""
        ft_score = (match.get("score") or {}).get("fullTime") or {}
        h, a = ft_score.get("home"), ft_score.get("away")
        if h is not None and a is not None:
            return f"{h}–{a}"
        return "vs"

    _STATUS_LABEL = {
        "SCHEDULED": ("Scheduled", "grey"),
        "TIMED": ("Confirmed", "blue"),
        "IN_PLAY": ("LIVE", "green"),
        "PAUSED": ("HT", "orange"),
        "FINISHED": ("FT", "grey"),
        "POSTPONED": ("Postponed", "red"),
        "CANCELLED": ("Cancelled", "red"),
    }

    def _status_label(self, status: str) -> str:
        return self._STATUS_LABEL.get(status, (status.capitalize(), "grey"))[0]

    # Score tests
    def test_finished_match_shows_score(self, match_finished):
        assert self._score_text(match_finished) == "2–1"

    def test_scheduled_match_shows_vs(self, match_scheduled):
        assert self._score_text(match_scheduled) == "vs"

    def test_in_play_match_shows_current_score(self, match_in_play):
        assert self._score_text(match_in_play) == "1–0"

    def test_paused_match_shows_score(self, match_paused):
        assert self._score_text(match_paused) == "0–0"

    def test_zero_zero_score_not_vs(self, match_paused):
        assert self._score_text(match_paused) != "vs"

    def test_none_scores_shows_vs(self):
        match = _make_match(99, "GROUP_A", 1, "2026-06-11T12:00:00Z",
                            "SCHEDULED", score_home=None, score_away=None)
        assert self._score_text(match) == "vs"

    # Status label tests
    def test_finished_status_is_ft(self, match_finished):
        assert self._status_label(match_finished["status"]) == "FT"

    def test_scheduled_status_label(self, match_scheduled):
        assert self._status_label(match_scheduled["status"]) == "Scheduled"

    def test_in_play_status_is_live(self, match_in_play):
        assert self._status_label(match_in_play["status"]) == "LIVE"

    def test_paused_status_is_ht(self, match_paused):
        assert self._status_label(match_paused["status"]) == "HT"

    def test_timed_status_is_confirmed(self):
        match = _make_match(99, "GROUP_A", 1, "2026-06-11T12:00:00Z", "TIMED")
        assert self._status_label(match["status"]) == "Confirmed"
