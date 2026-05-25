"""styled_dropdown: ft.Dropdown with project colour props pre-applied."""
from __future__ import annotations

from typing import Callable

import flet as ft
from core.ui_helpers import ACCENT, BG_CARD, BORDER_COLOR, TEXT_PRIMARY


def styled_dropdown(
    label: str,
    options: list[ft.dropdown.Option],
    value: str | None = None,
    width: int = 200,
    on_change: Callable | None = None,
) -> ft.Dropdown:
    """Return a Dropdown with standard project colour props."""
    dd = ft.Dropdown(
        label=label,
        options=options,
        value=value,
        width=width,
        bgcolor=BG_CARD,
        color=TEXT_PRIMARY,
        focused_border_color=ACCENT,
        border_color=BORDER_COLOR,
    )
    if on_change is not None:
        dd.on_change = on_change
    return dd
