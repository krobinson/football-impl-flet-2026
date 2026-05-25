"""Tournament History view – browse all FIFA World Cup editions (1930–2022)."""
from __future__ import annotations

import flet as ft
from features.matches.services import DataStore
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR,
    build_bar_chart, build_data_table, card, scrollable_card,
    section_title, stat_badge, value_text,
)
from core.components import page_header, styled_dropdown


def build_tournament_view(store: DataStore) -> ft.Column:
    """Build the Tournament History tab content."""
    years = store.all_years
    df = store.tournaments

    # ── Year selector ─────────────────────────────────────────────────────
    year_dd = styled_dropdown(
        "Select Edition",
        [ft.dropdown.Option(str(y)) for y in years],
        value=str(years[-1]) if years else None,
        width=200,
    )

    # ── Detail card (updated on year change) ─────────────────────────────
    detail_col = ft.Column([], spacing=8)

    def _render_detail(year: int) -> None:
        detail_col.controls.clear()
        row = df[df["year"] == year]
        if row.empty:
            detail_col.controls.append(ft.Text("No data.", color=TEXT_SECONDARY))
        else:
            r = row.iloc[0]
            detail_col.controls += [
                section_title(f"📋 {int(r['year'])} Edition — {r['host']}"),
                ft.Row(
                    [
                        stat_badge("Champion", str(r["champion"]), "#FFD700"),
                        stat_badge("Runner-up", str(r["runner_up"]), "#C0C0C0"),
                        stat_badge("Third Place", str(r["third_place"]), "#CD7F32"),
                        stat_badge("Goals", str(int(r["goals"]))),
                        stat_badge("Matches", str(int(r["matches"]))),
                        stat_badge("Teams", str(int(r["teams"]))),
                    ],
                    wrap=True,
                    spacing=8,
                ),
            ]
        try:
            detail_col.update()
        except Exception:
            pass

    def _on_year_change(_: ft.ControlEvent) -> None:
        if year_dd.value:
            _render_detail(int(year_dd.value))

    year_dd.on_change = _on_year_change

    # ── Goals bar chart ───────────────────────────────────────────────────
    if not df.empty:
        chart = build_bar_chart(
            labels=df["year"].astype(int).tolist(),
            values=df["goals"].astype(float).tolist(),
            title="⚽ Total Goals per World Cup Edition",
            colour="#1a472a",
            max_width=500,
        )
    else:
        chart = ft.Text("No tournament data.", color=TEXT_SECONDARY)

    # ── Summary table ─────────────────────────────────────────────────────
    if not df.empty:
        tbl_cols = ["Year", "Host", "Champion", "Runner-up", "3rd Place", "Goals", "Matches"]
        tbl_rows = [
            [
                str(int(r["year"])),
                str(r["host"]),
                str(r["champion"]),
                str(r["runner_up"]),
                str(r["third_place"]),
                str(int(r["goals"])),
                str(int(r["matches"])),
            ]
            for _, r in df.iterrows()
        ]
        table = build_data_table(tbl_cols, tbl_rows)
    else:
        table = ft.Text("No data.", color=TEXT_SECONDARY)

    # Initial render
    if years:
        _render_detail(years[-1])

    return ft.Column(
        [
            page_header("🏆 Tournament History", "All FIFA World Cup editions 1930–2022"),
            year_dd,
            card(detail_col),
            card(chart, padding=16),
            ft.Text("All Editions", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(
                ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True),
                bgcolor=BG_CARD,
                border_radius=8,
                padding=12,
                border=ft.Border.all(1, BORDER_COLOR),
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
