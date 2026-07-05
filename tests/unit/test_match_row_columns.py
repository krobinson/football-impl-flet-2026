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


# ---------------------------------------------------------------------------
# T009-T011 — US1: Group stage match scores display
# ---------------------------------------------------------------------------

class TestGroupStageScores:
    """Verify group stage matches display actual scores and correct status badges."""

    def test_group_stage_match_with_score_displays_xy(self):
        """T009: Group stage match with score shows X-Y in Score column."""
        from features.schedule.components.match_row import match_row
        match = _make_match(score_home=2, score_away=0, status="FINISHED")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        score_texts = _extract_texts(containers[6])
        assert any("2–0" in t for t in score_texts), f"Expected '2–0' in score column: {score_texts}"

    def test_group_stage_match_with_score_shows_ft_status(self):
        """T010: Group stage match with score shows FT status badge."""
        from features.schedule.components.match_row import match_row
        match = _make_match(score_home=1, score_away=1, status="FINISHED")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        status_texts = _extract_texts(containers[7])
        assert any("FT" in t for t in status_texts), f"Expected 'FT' in status column: {status_texts}"

    def test_group_stage_match_without_score_shows_vs_and_scheduled(self):
        """T011: Group stage match without score shows 'vs' and 'Scheduled'."""
        from features.schedule.components.match_row import match_row
        match = _make_match(status="SCHEDULED")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        score_texts = _extract_texts(containers[6])
        status_texts = _extract_texts(containers[7])
        assert any("vs" in t for t in score_texts), f"Expected 'vs' in score column: {score_texts}"
        assert any("Scheduled" in t for t in status_texts), f"Expected 'Scheduled' in status column: {status_texts}"


# ---------------------------------------------------------------------------
# T014-T017 — US2: Knockout stage matches display
# ---------------------------------------------------------------------------

def _make_knockout_match(
    home: str = "South Africa",
    away: str = "Canada",
    score_home: int | None = None,
    score_away: int | None = None,
    status: str = "SCHEDULED",
    venue: str = "Los Angeles (Inglewood)",
    round_display: str = "R32",
    utc_date: str = "2026-06-28T19:00:00Z",
) -> dict:
    """Create a knockout match dict (no group field)."""
    return {
        "id": 73,
        "utcDate": utc_date,
        "status": status,
        "matchday": 99,
        "group": "",
        "venue": venue,
        "homeTeam": {"name": home, "tla": None},
        "awayTeam": {"name": away, "tla": None},
        "score": {"fullTime": {"home": score_home, "away": score_away}} if score_home is not None else None,
        "stage": "ROUND_OF_32",
        "round_display": round_display,
    }


class TestKnockoutMatches:
    """Verify knockout matches display round labels and scores correctly."""

    def test_knockout_match_displays_round_label_in_group_column(self):
        """T014: Knockout match shows round label (e.g., 'R32') in Group column."""
        from features.schedule.components.match_row import match_row
        match = _make_knockout_match(round_display="R32")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        group_texts = _extract_texts(containers[3])
        assert any("R32" in t for t in group_texts), f"Expected 'R32' in group column: {group_texts}"

    def test_knockout_match_with_score_displays_score_and_ft(self):
        """T015: Knockout match with score shows score and FT status."""
        from features.schedule.components.match_row import match_row
        match = _make_knockout_match(score_home=0, score_away=1, status="FINISHED")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        score_texts = _extract_texts(containers[6])
        status_texts = _extract_texts(containers[7])
        assert any("0–1" in t for t in score_texts), f"Expected '0–1' in score column: {score_texts}"
        assert any("FT" in t for t in status_texts), f"Expected 'FT' in status column: {status_texts}"

    def test_knockout_match_without_score_shows_vs_and_scheduled(self):
        """T016: Knockout match without score shows 'vs' and 'Scheduled'."""
        from features.schedule.components.match_row import match_row
        match = _make_knockout_match(status="SCHEDULED")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        score_texts = _extract_texts(containers[6])
        status_texts = _extract_texts(containers[7])
        assert any("vs" in t for t in score_texts), f"Expected 'vs' in score column: {score_texts}"
        assert any("Scheduled" in t for t in status_texts), f"Expected 'Scheduled' in status column: {status_texts}"

    def test_knockout_match_with_placeholder_team_names(self):
        """T017: Knockout match with placeholder team names displays placeholder text."""
        from features.schedule.components.match_row import match_row
        match = _make_knockout_match(home="1A", away="2B")
        row = match_row(match, 0)
        containers = _get_row_containers(row)
        home_texts = _extract_texts(containers[4])
        away_texts = _extract_texts(containers[5])
        assert any("1A" in t for t in home_texts), f"Expected '1A' in home column: {home_texts}"
        assert any("2B" in t for t in away_texts), f"Expected '2B' in away column: {away_texts}"
