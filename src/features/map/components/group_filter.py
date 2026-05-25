"""Group filter widget — declarative edition (US3).

Renders A–L group chips; clicking one highlights that group on the map.
Clicking an already-active group clears the filter.
Uses @ft.component so chip colours are derived from MapRenderState on each
render — no manual .update() calls.
"""
from __future__ import annotations

import flet as ft

from features.map.models import FIFAGroup, MapRenderState

_CHIP_ACTIVE_BG = "#F39C12"
_CHIP_INACTIVE_BG = "#2C3E50"
_CHIP_TEXT_ACTIVE = "#000000"
_CHIP_TEXT_INACTIVE = "#ECF0F1"


@ft.component
def GroupFilter(
    groups: list[FIFAGroup],
    state: MapRenderState,
) -> ft.Control:
    """Row of group-filter chips.  Derives colours from state on each render.

    Args:
        groups: All 12 FIFA groups (sorted A–L).
        state:  Shared MapRenderState; handler assigns to active_group_filter.
    """

    def _on_click(group_name: str) -> None:
        state.active_group_filter = (
            None if state.active_group_filter == group_name else group_name
        )

    chips = [
        ft.Container(
            content=ft.Text(
                f"Group {g.name}",
                size=12,
                weight=ft.FontWeight.W_500,
                color=(
                    _CHIP_TEXT_ACTIVE
                    if state.active_group_filter == g.name
                    else _CHIP_TEXT_INACTIVE
                ),
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=20,
            bgcolor=(
                _CHIP_ACTIVE_BG
                if state.active_group_filter == g.name
                else _CHIP_INACTIVE_BG
            ),
            on_click=lambda e, name=g.name: _on_click(name),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )
        for g in groups
    ]

    return ft.Row(controls=chips, wrap=True, spacing=6, run_spacing=6)
