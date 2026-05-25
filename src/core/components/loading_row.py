"""loading_row: notice text + spinner row dataclass factory."""
from __future__ import annotations

from dataclasses import dataclass

import flet as ft
from core.ui_helpers import TEXT_SECONDARY


@dataclass
class LoadingRow:
    """Holds the three controls that together form a loading indicator row."""
    notice: ft.Text
    ring: ft.ProgressRing
    row: ft.Row  # embed in layout; contains ring + any prefix controls


def loading_row(
    prefix_controls: list[ft.Control] | None = None,
) -> LoadingRow:
    """Return a LoadingRow with a hidden notice text and a hidden spinner row."""
    notice = ft.Text("", size=12, color=TEXT_SECONDARY, visible=False)
    ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
    row = ft.Row(
        [*(prefix_controls or []), ring],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return LoadingRow(notice=notice, ring=ring, row=row)
