"""Records & Top Scorers view – all-time leaders in goals and appearances."""
from __future__ import annotations

import flet as ft
from features.matches.services import DataStore
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR, GREEN,
    build_bar_chart, build_data_table, card, section_title,
)
from features.records.components import ModeToggle
from core.components import scrollable_table_card


def build_records_view(store: DataStore) -> ft.Column:
    """Build the Records & Top Scorers tab content."""

    _state: dict = {"mode": "goals", "selected_idx": None}

    # ── Toggle buttons ────────────────────────────────────────────────────
    def _on_mode_change(mode: str) -> None:
        _state["mode"] = mode
        _state["selected_idx"] = None
        _render_table(mode)

    toggle = ModeToggle(on_mode_change=_on_mode_change)

    subtitle_text = ft.Text("", size=12, color=TEXT_SECONDARY)
    table_container = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
    chart_container = ft.Column([], spacing=6)
    detail_container = ft.Column([], spacing=6)

    # ── Goals leaderboard ─────────────────────────────────────────────────
    def _render_goal_table() -> None:
        df = store.top_scorers.copy()
        if df.empty:
            subtitle_text.value = "No data available."
            table_container.controls = [ft.Text("No data.", color=TEXT_SECONDARY)]
            return

        df = df.sort_values("goals", ascending=False).reset_index(drop=True)
        subtitle_text.value = f"{len(df)} players with World Cup goals on record"

        cols = ["Rank", "Player", "Team", "Goals", "Tournaments"]
        rows: list[list[str]] = []
        for i, r in df.iterrows():
            rows.append([
                str(int(i) + 1),
                str(r.get("name", r.get("player", "Unknown"))),
                str(r.get("team", "")),
                str(int(r["goals"])),
                str(int(r.get("tournaments", 1))),
            ])

        table = build_data_table(cols, rows, on_select=_on_row_select)
        table_container.controls = [table]
        chart_container.controls.clear()
        detail_container.controls.clear()
        try:
            subtitle_text.update()
            table_container.update()
            chart_container.update()
            detail_container.update()
        except Exception:
            pass

    def _render_appearance_table() -> None:
        df = store.appearances.copy()
        if df.empty:
            subtitle_text.value = "No data available."
            table_container.controls = [ft.Text("No data.", color=TEXT_SECONDARY)]
            return

        df = df.sort_values("matches", ascending=False).reset_index(drop=True)
        subtitle_text.value = f"{len(df)} players with World Cup appearance data"

        cols = ["Rank", "Player", "Team", "Matches", "Tournaments"]
        rows: list[list[str]] = []
        for i, r in df.iterrows():
            rows.append([
                str(int(i) + 1),
                str(r.get("name", r.get("player", "Unknown"))),
                str(r.get("team", "")),
                str(int(r["matches"])),
                str(int(r.get("tournaments", 1))),
            ])

        table = build_data_table(cols, rows, on_select=_on_row_select)
        table_container.controls = [table]
        chart_container.controls.clear()
        detail_container.controls.clear()
        try:
            subtitle_text.update()
            table_container.update()
            chart_container.update()
            detail_container.update()
        except Exception:
            pass

    def _render_table(mode: str) -> None:
        if mode == "goals":
            _render_goal_table()
        else:
            _render_appearance_table()

    def _on_row_select(idx: int) -> None:
        _state["selected_idx"] = idx
        mode = _state["mode"]
        detail_container.controls.clear()
        chart_container.controls.clear()

        if mode == "goals":
            df = store.top_scorers.sort_values("goals", ascending=False).reset_index(drop=True)
            if idx >= len(df):
                return
            row = df.iloc[idx]
            name = str(row.get("name", row.get("player", "Unknown")))
            team = str(row.get("team", ""))
            goals = int(row["goals"])

            detail_container.controls += [
                section_title(f"🔍 {name}"),
                ft.Text(f"Team: {team}", size=13, color=TEXT_SECONDARY),
                ft.Text(f"Total WC goals: {goals}", size=13, color=ACCENT),
            ]

            # Per-tournament goals from match_events (if available)
            if not store.match_events.empty:
                import re
                ev = store.match_events.copy()
                # filter to goal events for this player
                player_col = "player"
                ev = ev[ev[player_col].str.lower().str.contains(name.split()[0].lower(), na=False)]
                ev = ev[ev["event_type"].isin(["goal", "penalty_goal"])]
                if not ev.empty:
                    by_year = ev.groupby("year").size().reset_index(name="goals")
                    labels = [str(int(r["year"])) for _, r in by_year.iterrows()]
                    values = [int(r["goals"]) for _, r in by_year.iterrows()]
                    chart = build_bar_chart(labels, values, f"Goals by Tournament", ACCENT, max_width=300)
                    chart_container.controls.append(chart)

        else:
            df = store.appearances.sort_values("matches", ascending=False).reset_index(drop=True)
            if idx >= len(df):
                return
            row = df.iloc[idx]
            name = str(row.get("name", row.get("player", "Unknown")))
            team = str(row.get("team", ""))
            matches = int(row["matches"])

            detail_container.controls += [
                section_title(f"🔍 {name}"),
                ft.Text(f"Team: {team}", size=13, color=TEXT_SECONDARY),
                ft.Text(f"Total WC matches: {matches}", size=13, color=ACCENT),
            ]

            # Tournaments from appearances columns (if granular data exists)
            tournaments_col = "tournament_year"
            if tournaments_col in row.index and row[tournaments_col]:
                try:
                    years = sorted(set(str(y).strip() for y in str(row[tournaments_col]).split(",")))
                    values = [1] * len(years)
                    chart = build_bar_chart(years, values, "Appeared In", ACCENT, bar_height=20, max_width=200)
                    chart_container.controls.append(chart)
                except Exception:
                    pass

        try:
            detail_container.update()
            chart_container.update()
        except Exception:
            pass

    # Initial render
    _render_table("goals")

    return ft.Column(
        [
            ft.Text("📊 Records & Leaders", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            subtitle_text,
            ft.Divider(color=BORDER_COLOR, height=1),
            toggle.row,
            scrollable_table_card(table_container, height=380),
            card(
                ft.Column([
                    ft.Row([detail_container, chart_container], spacing=24, wrap=True),
                ]),
                padding=14,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
