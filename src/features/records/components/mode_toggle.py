"""Mode toggle widget (Goals / Appearances) for the records tab."""
from __future__ import annotations

from typing import Callable

import flet as ft
from core.ui_helpers import ACCENT, BG_CARD, TEXT_PRIMARY


class ModeToggle:
    """Pair of toggle buttons that switch between 'goals' and 'appearances'."""

    def __init__(self, on_mode_change: Callable[[str], None]) -> None:
        self._on_change = on_mode_change
        self.btn_goals = ft.Button(
            "⚽ Top Scorers",
            bgcolor=ACCENT, color="#000000",
            on_click=lambda _: self._activate("goals"),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        )
        self.btn_app = ft.Button(
            "🏅 Most Appearances",
            bgcolor=BG_CARD, color=TEXT_PRIMARY,
            on_click=lambda _: self._activate("appearances"),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        )
        self.row = ft.Row([self.btn_goals, self.btn_app], spacing=8)

    def _activate(self, mode: str) -> None:
        self.set_active(mode)
        self._on_change(mode)

    def set_active(self, mode: str) -> None:
        """Update button visual state to reflect the active mode."""
        if mode == "goals":
            self.btn_goals.bgcolor = ACCENT
            self.btn_goals.color = "#000000"
            self.btn_app.bgcolor = BG_CARD
            self.btn_app.color = TEXT_PRIMARY
        else:
            self.btn_app.bgcolor = ACCENT
            self.btn_app.color = "#000000"
            self.btn_goals.bgcolor = BG_CARD
            self.btn_goals.color = TEXT_PRIMARY
        try:
            self.btn_goals.update()
            self.btn_app.update()
        except Exception:
            pass
