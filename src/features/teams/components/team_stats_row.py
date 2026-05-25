"""Team summary stats row widget."""
from __future__ import annotations

import flet as ft
from core.ui_helpers import TEXT_SECONDARY, stat_badge


def team_stats_row(team: str, df) -> ft.Row:
    """Return a row of stat badges summarising a team's World Cup history."""
    if df.empty:
        return ft.Row([ft.Text(f"No World Cup data for {team}.", color=TEXT_SECONDARY)])
    total_p = int(df["played"].sum())
    total_w = int(df["wins"].sum())
    total_d = int(df["draws"].sum())
    total_l = int(df["losses"].sum())
    total_gf = int(df["goals_for"].sum())
    total_ga = int(df["goals_against"].sum())
    editions = len(df)
    w_pct = f"{total_w / total_p * 100:.0f}%" if total_p else "0%"
    return ft.Row(
        [
            stat_badge("World Cups", str(editions)),
            stat_badge("Matches", str(total_p)),
            stat_badge(f"Wins ({w_pct})", str(total_w), "#2ECC71"),
            stat_badge("Draws", str(total_d), "#F39C12"),
            stat_badge("Losses", str(total_l), "#E74C3C"),
            stat_badge("Goals For", str(total_gf)),
            stat_badge("Goals Against", str(total_ga)),
            stat_badge("GD", f"{total_gf - total_ga:+d}",
                       "#2ECC71" if total_gf >= total_ga else "#E74C3C"),
        ],
        wrap=True,
        spacing=8,
    )
