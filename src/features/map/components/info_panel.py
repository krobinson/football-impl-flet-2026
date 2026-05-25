"""Country detail info panel — declarative edition (US2).

Shows flag, name, group, and World Cup appearance count for the selected
country.  Re-renders automatically whenever MapRenderState.selected_country
changes — no .update() calls needed.
"""
from __future__ import annotations

import flet as ft

from features.map.models import MapRenderState

_PANEL_BG = "#16213E"
_ACCENT = "#2ECC71"


@ft.component
def InfoPanel(state: MapRenderState) -> ft.Control:
    """Display panel for the currently selected country.

    Args:
        state: Shared MapRenderState; reads selected_country on each render.
    """
    country = state.selected_country

    if country is None:
        flag = "🌍"
        name = "Select a country"
        group_txt = ""
        appear_txt = ""
        badge_visible = False
    else:
        flag = country.flag_emoji
        name = country.name
        group_txt = f"Group {country.group}"
        appear_txt = f"World Cup appearances: {country.appearances}"
        badge_visible = True

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(flag, size=48),
                ft.Text(name, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(group_txt, size=14, color=ft.Colors.GREY_300),
                ft.Text(appear_txt, size=13, color=ft.Colors.GREY_400),
                ft.Container(
                    content=ft.Text(
                        "✓ FIFA WC 2026",
                        size=12,
                        color=_ACCENT,
                        weight=ft.FontWeight.BOLD,
                    ),
                    visible=badge_visible,
                ),
            ],
            spacing=4,
        ),
        padding=16,
        bgcolor=_PANEL_BG,
        border_radius=8,
        width=280,
    )
