"""Unit tests for stage chips component — 017-knockout-stage-results.

TDD: tests written before implementation. Run with:
    uv run pytest tests/unit/test_stage_chips.py -v
"""
from __future__ import annotations

import pytest
import flet as ft


# ---------------------------------------------------------------------------
# T021-T022 — build_stage_chips() tests
# ---------------------------------------------------------------------------

class TestBuildStageChips:
    """Tests for build_stage_chips() function."""

    def test_returns_7_chips(self):
        """T021: build_stage_chips returns 7 chips."""
        from features.schedule.components.stage_chips import build_stage_chips
        row = build_stage_chips("ALL", lambda x: None)
        assert len(row.controls) == 7

    def test_chip_labels_correct(self):
        """T021: Chips have correct labels."""
        from features.schedule.components.stage_chips import build_stage_chips
        row = build_stage_chips("ALL", lambda x: None)
        labels = []
        for ctrl in row.controls:
            if isinstance(ctrl, ft.Container) and isinstance(ctrl.content, ft.Text):
                labels.append(ctrl.content.value)
        expected = ["All", "Group Stage", "R32", "R16", "QF", "SF", "Final"]
        assert labels == expected, f"Expected {expected}, got {labels}"

    def test_active_chip_highlighted(self):
        """T022: Active chip is highlighted."""
        from features.schedule.components.stage_chips import build_stage_chips
        row = build_stage_chips("ROUND_OF_32", lambda x: None)
        # Find the R32 chip (index 2)
        r32_chip = row.controls[2]
        # Active chip should have different background color
        assert r32_chip.bgcolor is not None

    def test_inactive_chips_not_highlighted(self):
        """T022: Inactive chips are not highlighted."""
        from features.schedule.components.stage_chips import build_stage_chips
        row = build_stage_chips("ALL", lambda x: None)
        # Check that R32 chip (index 2) is not active
        r32_chip = row.controls[2]
        all_chip = row.controls[0]
        # They should have different styling
        assert r32_chip.bgcolor != all_chip.bgcolor or r32_chip is all_chip
