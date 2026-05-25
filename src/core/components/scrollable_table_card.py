"""scrollable_table_card: bordered scrollable card for data tables."""
from __future__ import annotations

import flet as ft
from core.ui_helpers import BG_CARD, BORDER_COLOR


def scrollable_table_card(
    content: ft.Control,
    height: int = 380,
    padding: int = 12,
) -> ft.Container:
    """Return the standard bordered scrollable card used for data tables."""
    return ft.Container(
        content=ft.Column([content], scroll=ft.ScrollMode.AUTO, expand=True),
        bgcolor=BG_CARD,
        border_radius=8,
        padding=padding,
        height=height,
        border=ft.Border.all(1, BORDER_COLOR),
    )
