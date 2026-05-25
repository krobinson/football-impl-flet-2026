"""Team Performance view – per-team stats and head-to-head comparison."""
from __future__ import annotations

import flet as ft
from features.matches.services import DataStore
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR,
    BAR_COLOURS, build_bar_chart, build_data_table, card, section_title,
    stat_badge, value_text,
)
from features.teams.components import team_stats_row
from core.components import page_header, styled_dropdown


def build_teams_view(store: DataStore) -> ft.Column:
    """Build the Team Performance tab content."""
    all_teams = store.all_teams
    default_team = "Brazil" if "Brazil" in all_teams else (all_teams[0] if all_teams else "")

    # ── Team selectors ────────────────────────────────────────────────────
    team1_dd = styled_dropdown(
        "Primary Team",
        [ft.dropdown.Option(t) for t in all_teams],
        value=default_team,
        width=260,
    )
    team2_dd = styled_dropdown(
        "Compare with (optional)",
        [ft.dropdown.Option("")] + [ft.dropdown.Option(t) for t in all_teams],
        value="",
        width=260,
    )

    content_col = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def _team_stats(team: str):
        df = store.team_standings
        return df[df["team"] == team].sort_values("year").copy()

    def _render(team1: str, team2: str) -> None:
        content_col.controls.clear()

        if not team1:
            content_col.controls.append(ft.Text("Select a team above.", color=TEXT_SECONDARY))
            try:
                content_col.update()
            except Exception:
                pass
            return

        df1 = _team_stats(team1)
        if df1.empty:
            content_col.controls.append(
                ft.Text(f"No World Cup participation found for {team1}.", color=TEXT_SECONDARY)
            )
            try:
                content_col.update()
            except Exception:
                pass
            return

        years = df1["year"].astype(int).tolist()

        content_col.controls += [
            card(team_stats_row(team1, df1)),
            card(build_bar_chart(years, df1["wins"].tolist(),
                                 f"{team1} – Wins per World Cup", "#2CA02C")),
            card(build_bar_chart(years, df1["goals_for"].tolist(),
                                 f"{team1} – Goals Scored per World Cup", "#1F77B4")),
            card(build_bar_chart(years, df1["losses"].tolist(),
                                 f"{team1} – Losses per World Cup", "#D62728")),
        ]

        # Head-to-head
        if team2 and team2 != team1:
            df2 = _team_stats(team2)
            if df2.empty:
                content_col.controls.append(
                    ft.Text(f"No World Cup data for {team2}.", color=TEXT_SECONDARY)
                )
            else:
                import pandas as pd
                merged = pd.merge(
                    df1[["year", "wins"]].rename(columns={"wins": team1}),
                    df2[["year", "wins"]].rename(columns={"wins": team2}),
                    on="year", how="outer",
                ).fillna(0).sort_values("year")
                h2h_col = ft.Column([
                    section_title(f"Head-to-Head Wins: {team1} vs {team2}"),
                    *[
                        ft.Row([
                            ft.Container(
                                ft.Text(str(int(r["year"])), size=11, color=TEXT_SECONDARY),
                                width=50,
                            ),
                            ft.Container(
                                bgcolor="#1F77B4",
                                width=max(2, int(float(r[team1]) / max(merged[team1].max(), 1) * 200)),
                                height=14,
                                border_radius=3,
                            ),
                            ft.Text(f"{team1}: {int(float(r[team1]))}", size=11, color="#1F77B4"),
                            ft.Container(width=16),
                            ft.Container(
                                bgcolor="#D62728",
                                width=max(2, int(float(r[team2]) / max(merged[team2].max(), 1) * 200)),
                                height=14,
                                border_radius=3,
                            ),
                            ft.Text(f"{team2}: {int(float(r[team2]))}", size=11, color="#D62728"),
                        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                        for _, r in merged.iterrows()
                    ],
                ], spacing=4)
                content_col.controls.append(card(h2h_col))

        try:
            content_col.update()
        except Exception:
            pass

    def _on_change(_: ft.ControlEvent) -> None:
        _render(team1_dd.value or "", team2_dd.value or "")

    team1_dd.on_change = _on_change
    team2_dd.on_change = _on_change

    _render(default_team, "")

    return ft.Column(
        [
            page_header("⚽ Team Performance", "Per-team World Cup history and head-to-head comparison"),
            ft.Row([team1_dd, team2_dd], spacing=12, wrap=True),
            content_col,
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
