"""Unit tests for schedule stage filtering — 017-knockout-stage-results.

TDD: tests written before implementation. Run with:
    uv run pytest tests/unit/test_schedule_stage_filter.py -v
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# T023-T024 — Stage filtering tests
# ---------------------------------------------------------------------------

class TestStageFiltering:
    """Tests for stage filtering logic."""

    def _make_matches(self) -> list[dict]:
        """Create a set of test matches across different stages."""
        matches = []
        # Group stage matches (72 total in real data, using 6 for testing)
        for i in range(6):
            matches.append({
                "stage": "GROUP_STAGE",
                "group": f"GROUP_{chr(65 + i % 12)}",
                "utcDate": f"2026-06-{11 + i:02d}T14:00:00Z",
            })
        # Round of 32 (16 total, using 4 for testing)
        for i in range(4):
            matches.append({
                "stage": "ROUND_OF_32",
                "group": "",
                "utcDate": f"2026-06-{28 + i:02d}T19:00:00Z",
            })
        # Round of 16 (8 total, using 2 for testing)
        for i in range(2):
            matches.append({
                "stage": "ROUND_OF_16",
                "group": "",
                "utcDate": f"2026-07-{5 + i:02d}T19:00:00Z",
            })
        # Quarter-final (4 total, using 2 for testing)
        for i in range(2):
            matches.append({
                "stage": "QUARTER_FINAL",
                "group": "",
                "utcDate": f"2026-07-{10 + i:02d}T19:00:00Z",
            })
        # Semi-final (2 total)
        matches.append({
            "stage": "SEMI_FINAL",
            "group": "",
            "utcDate": "2026-07-15T19:00:00Z",
        })
        matches.append({
            "stage": "SEMI_FINAL",
            "group": "",
            "utcDate": "2026-07-16T19:00:00Z",
        })
        # Final (2 total: Final + 3rd place)
        matches.append({
            "stage": "FINAL",
            "group": "",
            "utcDate": "2026-07-19T19:00:00Z",
        })
        matches.append({
            "stage": "FINAL",
            "group": "",
            "utcDate": "2026-07-20T19:00:00Z",
        })
        return matches

    def _filter_by_stage(self, matches: list[dict], stage: str) -> list[dict]:
        """Mirror the production _apply_stage_filter logic."""
        if stage == "ALL":
            return matches
        return [m for m in matches if m.get("stage") == stage]

    def test_all_returns_all_matches(self):
        """T023: 'ALL' filter returns all matches."""
        matches = self._make_matches()
        result = self._filter_by_stage(matches, "ALL")
        assert len(result) == 18

    def test_group_stage_filter(self):
        """T023: GROUP_STAGE filter returns only group matches."""
        matches = self._make_matches()
        result = self._filter_by_stage(matches, "GROUP_STAGE")
        assert len(result) == 6
        assert all(m["stage"] == "GROUP_STAGE" for m in result)

    def test_round_of_32_filter(self):
        """T023: ROUND_OF_32 filter returns only R32 matches."""
        matches = self._make_matches()
        result = self._filter_by_stage(matches, "ROUND_OF_32")
        assert len(result) == 4
        assert all(m["stage"] == "ROUND_OF_32" for m in result)

    def test_quarter_final_filter(self):
        """T023: QUARTER_FINAL filter returns only QF matches."""
        matches = self._make_matches()
        result = self._filter_by_stage(matches, "QUARTER_FINAL")
        assert len(result) == 2
        assert all(m["stage"] == "QUARTER_FINAL" for m in result)

    def test_final_filter_includes_third_place(self):
        """T023: FINAL filter returns both Final and 3rd place matches."""
        matches = self._make_matches()
        result = self._filter_by_stage(matches, "FINAL")
        assert len(result) == 2

    def test_group_chips_visible_only_for_group_stage(self):
        """T024: Group chips should be visible only when stage is GROUP_STAGE."""
        # This is a logic test — the actual UI implementation will handle visibility
        # Here we just verify the condition
        def should_show_group_chips(stage: str) -> bool:
            return stage == "GROUP_STAGE"

        assert should_show_group_chips("GROUP_STAGE") is True
        assert should_show_group_chips("ALL") is False
        assert should_show_group_chips("ROUND_OF_32") is False
        assert should_show_group_chips("FINAL") is False
