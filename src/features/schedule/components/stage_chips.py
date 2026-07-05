"""Stage selector chips for the schedule tab — 017-knockout-stage-results."""
from __future__ import annotations

import flet as ft

from core.ui_helpers import ACCENT

_CHIP_ACTIVE_BG = "#F39C12"
_CHIP_INACTIVE_BG = "#2C3E50"
_CHIP_TEXT_ACTIVE = "#000000"
_CHIP_TEXT_INACTIVE = "#ECF0F1"

_STAGE_OPTIONS = [
    ("All", "ALL"),
    ("Group Stage", "GROUP_STAGE"),
    ("R32", "ROUND_OF_32"),
    ("R16", "ROUND_OF_16"),
    ("QF", "QUARTER_FINAL"),
    ("SF", "SEMI_FINAL"),
    ("Final", "FINAL"),
]


def build_stage_chips(
    active_stage: str,
    on_select,
) -> ft.Row:
    """Return a chip row for tournament stage selection.

    Args:
        active_stage: Currently selected stage value (e.g., "ALL", "GROUP_STAGE")
        on_select: Callback function receiving the selected stage value string

    Returns:
        ft.Row containing stage selector chips
    """
    def _chip(label: str, value: str) -> ft.Container:
        is_active = value == active_stage
        return ft.Container(
            content=ft.Text(
                label,
                size=12,
                weight=ft.FontWeight.W_600,
                color=_CHIP_TEXT_ACTIVE if is_active else _CHIP_TEXT_INACTIVE,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=20,
            bgcolor=_CHIP_ACTIVE_BG if is_active else _CHIP_INACTIVE_BG,
            on_click=lambda e, val=value: on_select(val),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    return ft.Row(
        controls=[_chip(label, value) for label, value in _STAGE_OPTIONS],
        wrap=True,
        spacing=6,
        run_spacing=6,
    )
