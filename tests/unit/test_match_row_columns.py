"""Unit tests for split match columns — 016-group-stage-match-details.

TDD: tests written before implementation. Run with:
    uv run pytest tests/unit/test_match_row_columns.py -v
"""
from __future__ import annotations

import pytest
import flet as ft


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_match(
    home: str = "USA",
    home_tla: str | None = "USA",
    away: str = "Mexico",
    away_tla: str | None = "MEX",
    score_home: int | None = None,
    score_away: int | None = None,
    status: str = "SCHEDULED",
    venue: str = "AT&T Stadium",
    group: str = "GROUP_A",
    matchday: int = 1,
    utc_date: str = "2026-06-11T14:00:00Z",
) -> dict:
    return {
        "id": 1,
        "utcDate": utc_date,
        "status": status,
        "matchday": matchday,
        "group": group,
        "venue": venue,
        "homeTeam": {"name": home, "tla": home_tla},
        "awayTeam": {"name": away, "tla": away_tla},
        "score": {"fullTime": {"home": score_home, "away": score_away}},
    }


def _extract_texts(ctrl) -> list[str]:
    """Recursively collect all Text.value strings from a Flet control tree."""
    texts = []

    def _walk(c):
        if isinstance(c, ft.Text):
            texts.append(c.value or "")
        for attr in ("content", "controls", "actions"):
            child = getattr(c, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    _walk(item)
            else:
                _walk(child)

    _walk(ctrl)
    return texts


def _get_row_containers(row) -> list[ft.Container]:
    """Get the direct child containers from the Row inside the match_row Container."""
    inner_row = row.content
    if isinstance(inner_row, ft.Row):
        return [c for c in inner_row.controls if isinstance(c, ft.Container)]
    return []


# ---------------------------------------------------------------------------
# T004 — match_row renders separate Home, Away, Score columns
# ---------------------------------------------------------------------------

class TestMatchRowSplitColumns:
    """Verify match_row renders home team, away team, and score as separate columns."""

    def test_home_team_name_in_separate_column(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(home="Brazil"), 0)
        containers = _get_row_containers(row)
        home_texts = _extract_texts(containers[4])
        assert any("Brazil" in t for t in home_texts), f"Expected 'Brazil' in home column: {home_texts}"

    def test_away_team_name_in_separate_column(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(away="Argentina"), 0)
        containers = _get_row_containers(row)
        away_texts = _extract_texts(containers[5])
        assert any("Argentina" in t for t in away_texts), f"Expected 'Argentina' in away column: {away_texts}"

    def test_score_in_separate_column(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(score_home=2, score_away=1, status="FINISHED"), 0)
        containers = _get_row_containers(row)
        score_texts = _extract_texts(containers[6])
        assert any("2–1" in t for t in score_texts), f"Expected '2–1' in score column: {score_texts}"

    def test_scheduled_match_shows_vs_in_score_column(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(), 0)
        containers = _get_row_containers(row)
        score_texts = _extract_texts(containers[6])
        assert any("vs" in t for t in score_texts), f"Expected 'vs' in score column: {score_texts}"

    def test_home_flag_present_when_tla_known(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(home="USA", home_tla="USA"), 0)
        containers = _get_row_containers(row)
        home_texts = _extract_texts(containers[4])
        assert any("🇺🇸" in t for t in home_texts), f"Expected US flag in home column: {home_texts}"

    def test_away_flag_present_when_tla_known(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(away="Mexico", away_tla="MEX"), 0)
        containers = _get_row_containers(row)
        away_texts = _extract_texts(containers[5])
        assert any("🇲🇽" in t for t in away_texts), f"Expected Mexico flag in away column: {away_texts}"

    def test_no_combined_match_text(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(home="USA", away="Mexico"), 0)
        all_texts = _extract_texts(row)
        combined = "USA  vs  Mexico"
        assert combined not in all_texts, f"Combined match text should not exist: {all_texts}"

    def test_row_has_at_least_9_columns(self):
        from features.schedule.components.match_row import match_row
        row = match_row(_make_match(), 0)
        containers = _get_row_containers(row)
        assert len(containers) >= 9, f"Expected at least 9 columns, got {len(containers)}"


# ---------------------------------------------------------------------------
# T005 — header_row renders Home, Away, Score headers
# ---------------------------------------------------------------------------

class TestHeaderRowSplitColumns:
    """Verify header_row renders separate Home, Away, Score headers."""

    def test_home_header_present(self):
        from features.schedule.components.match_row import header_row
        hdr = header_row()
        texts = _extract_texts(hdr)
        assert any("Home" in t for t in texts), f"Expected 'Home' header: {texts}"

    def test_away_header_present(self):
        from features.schedule.components.match_row import header_row
        hdr = header_row()
        texts = _extract_texts(hdr)
        assert any("Away" in t for t in texts), f"Expected 'Away' header: {texts}"

    def test_score_header_present(self):
        from features.schedule.components.match_row import header_row
        hdr = header_row()
        texts = _extract_texts(hdr)
        assert any("Score" in t for t in texts), f"Expected 'Score' header: {texts}"

    def test_no_combined_match_header(self):
        from features.schedule.components.match_row import header_row
        hdr = header_row()
        texts = _extract_texts(hdr)
        assert not any(t == "Match" for t in texts), f"'Match' header should not exist: {texts}"

    def test_header_has_at_least_9_columns(self):
        from features.schedule.components.match_row import header_row
        hdr = header_row()
        inner_row = hdr.content
        if isinstance(inner_row, ft.Row):
            containers = [c for c in inner_row.controls if isinstance(c, ft.Container)]
            assert len(containers) >= 9, f"Expected at least 9 header columns, got {len(containers)}"
