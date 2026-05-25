"""page_header: standard bold title + subtitle + optional divider."""
from __future__ import annotations

import flet as ft
from core.ui_helpers import BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY


def page_header(title: str, subtitle: str, *, divider: bool = True) -> ft.Column:
    """Return a Column with a bold 22 px title, 13 px subtitle, and optional Divider."""
    controls: list[ft.Control] = [
        ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
        ft.Text(subtitle, size=13, color=TEXT_SECONDARY),
    ]
    if divider:
        controls.append(ft.Divider(color=BORDER_COLOR, height=1))
    return ft.Column(controls, spacing=4)
