"""Unit tests for WorldCupJsonService — 017-knockout-stage-results.

TDD: tests written before implementation. Run with:
    uv run pytest tests/unit/test_worldcup_json_service.py -v
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# classify_stage() tests (T005)
# ---------------------------------------------------------------------------

class TestClassifyStage:
    """Tests for classify_stage() function."""

    def _fn(self):
        from features.schedule.services.worldcup_json_service import classify_stage
        return classify_stage

    def test_group_stage_match(self):
        match = {"group": "Group A", "round": "Matchday 1"}
        assert self._fn()(match) == "GROUP_STAGE"

    def test_group_stage_all_groups(self):
        fn = self._fn()
        for letter in "ABCDEFGHIJKL":
            match = {"group": f"Group {letter}", "round": "Matchday 1"}
            assert fn(match) == "GROUP_STAGE", f"Group {letter} should be GROUP_STAGE"

    def test_round_of_32(self):
        match = {"round": "Round of 32"}
        assert self._fn()(match) == "ROUND_OF_32"

    def test_round_of_16(self):
        match = {"round": "Round of 16"}
        assert self._fn()(match) == "ROUND_OF_16"

    def test_quarter_final(self):
        match = {"round": "Quarter-final"}
        assert self._fn()(match) == "QUARTER_FINAL"

    def test_semi_final(self):
        match = {"round": "Semi-final"}
        assert self._fn()(match) == "SEMI_FINAL"

    def test_final(self):
        match = {"round": "Final"}
        assert self._fn()(match) == "FINAL"

    def test_third_place_match(self):
        match = {"round": "Match for third place"}
        assert self._fn()(match) == "FINAL"

    def test_unknown_round(self):
        match = {"round": "Unknown Round"}
        assert self._fn()(match) == "UNKNOWN"

    def test_empty_match(self):
        match = {}
        assert self._fn()(match) == "UNKNOWN"


# ---------------------------------------------------------------------------
# round_display_label() tests (T006)
# ---------------------------------------------------------------------------

class TestRoundDisplayLabel:
    """Tests for round_display_label() function."""

    def _fn(self):
        from features.schedule.services.worldcup_json_service import round_display_label
        return round_display_label

    def test_group_stage_returns_empty(self):
        match = {"group": "Group A", "round": "Matchday 1"}
        assert self._fn()(match) == ""

    def test_round_of_32(self):
        match = {"round": "Round of 32"}
        assert self._fn()(match) == "R32"

    def test_round_of_16(self):
        match = {"round": "Round of 16"}
        assert self._fn()(match) == "R16"

    def test_quarter_final(self):
        match = {"round": "Quarter-final"}
        assert self._fn()(match) == "QF"

    def test_semi_final(self):
        match = {"round": "Semi-final"}
        assert self._fn()(match) == "SF"

    def test_final(self):
        match = {"round": "Final"}
        assert self._fn()(match) == "F"

    def test_third_place_match(self):
        match = {"round": "Match for third place"}
        assert self._fn()(match) == "3rd"

    def test_unknown_round_returns_empty(self):
        match = {"round": "Unknown Round"}
        assert self._fn()(match) == ""

    def test_empty_match(self):
        match = {}
        assert self._fn()(match) == ""


# ---------------------------------------------------------------------------
# get_all_matches() tests (T007)
# ---------------------------------------------------------------------------

class TestGetAllMatches:
    """Tests for get_all_matches() method."""

    def test_returns_all_matches_including_knockout(self):
        from features.schedule.services.worldcup_json_service import WorldCupJsonService
        service = WorldCupJsonService()
        matches = service.get_all_matches()
        # Should return 104 matches (72 group + 32 knockout)
        assert len(matches) == 104

    def test_all_matches_have_stage_field(self):
        from features.schedule.services.worldcup_json_service import WorldCupJsonService
        service = WorldCupJsonService()
        matches = service.get_all_matches()
        for match in matches:
            assert "stage" in match, "All matches must have 'stage' field"

    def test_all_matches_have_round_display_field(self):
        from features.schedule.services.worldcup_json_service import WorldCupJsonService
        service = WorldCupJsonService()
        matches = service.get_all_matches()
        for match in matches:
            assert "round_display" in match, "All matches must have 'round_display' field"

    def test_knockout_matches_included(self):
        from features.schedule.services.worldcup_json_service import WorldCupJsonService
        service = WorldCupJsonService()
        matches = service.get_all_matches()
        knockout_stages = {"ROUND_OF_32", "ROUND_OF_16", "QUARTER_FINAL", "SEMI_FINAL", "FINAL"}
        knockout_matches = [m for m in matches if m["stage"] in knockout_stages]
        assert len(knockout_matches) == 32

    def test_group_stage_matches_included(self):
        from features.schedule.services.worldcup_json_service import WorldCupJsonService
        service = WorldCupJsonService()
        matches = service.get_all_matches()
        group_matches = [m for m in matches if m["stage"] == "GROUP_STAGE"]
        assert len(group_matches) == 72

    def test_matches_sorted_by_date(self):
        from features.schedule.services.worldcup_json_service import WorldCupJsonService
        service = WorldCupJsonService()
        matches = service.get_all_matches()
        dates = [m.get("utcDate", "") for m in matches]
        assert dates == sorted(dates), "Matches should be sorted by date"
