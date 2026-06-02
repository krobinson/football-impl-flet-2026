"""Tournament History view – browse all FIFA World Cup editions (1930–2022)."""
from __future__ import annotations

import flet as ft
from features.matches.services import DataStore
from features.tournament.services import (
    TeamProgression,
    MatchRow,
    get_team_progression,
    get_teams_for_year,
)
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR,
    build_bar_chart, build_data_table, card, scrollable_card,
    section_title, stat_badge, value_text,
)
from core.components import page_header, styled_dropdown


# ---------------------------------------------------------------------------
# Score/match formatting helpers  (T008)
# ---------------------------------------------------------------------------

def _format_score(m: MatchRow) -> str:
    """Return a human-readable score string for a match row.

    Examples:
        normal    →  "2 – 1"
        AET only  →  "2 – 2 (AET)"
        AET + pen →  "3 – 3 (AET, 4–2 pens)"
    """
    base = f"{m.home_score} – {m.away_score}"
    if not m.aet:
        return base
    suffix = "AET"
    if m.pen_home is not None and m.pen_away is not None:
        suffix += f", {int(m.pen_home)}–{int(m.pen_away)} pens"
    return f"{base} ({suffix})"


def _build_match_tile(m: MatchRow) -> ft.Container:  # T009
    """Single match row: 'Home  score  Away'."""
    score_text = _format_score(m)
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(m.home_team, width=160, color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.RIGHT, size=13),
                ft.Text(score_text, width=130, color=ACCENT,
                        text_align=ft.TextAlign.CENTER, size=13,
                        weight=ft.FontWeight.BOLD),
                ft.Text(m.away_team, width=160, color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.LEFT, size=13),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(vertical=4, horizontal=8),
    )


def _build_progression_panel(progression: TeamProgression) -> ft.Column:  # T010
    """Build an expandable round-by-round progression column."""
    if not progression.rounds:
        team_label = progression.team or "this edition"
        return ft.Column(
            [ft.Text(
                f"No matches found for {team_label}.",
                color=TEXT_SECONDARY, italic=True, size=13,
            )],
            spacing=4,
        )

    panels: list[ft.Control] = []
    for rg in progression.rounds:
        header = ft.Text(
            rg.round_name,
            size=13,
            weight=ft.FontWeight.W_600,
            color=TEXT_PRIMARY,
        )
        tiles = ft.Column(
            [_build_match_tile(m) for m in rg.matches],
            spacing=2,
        )
        panels.append(
            ft.ExpansionTile(
                title=header,
                expanded=True,
                controls=[tiles],
                icon_color=TEXT_SECONDARY,
                collapsed_icon_color=TEXT_SECONDARY,
                tile_padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            )
        )

    return ft.Column(panels, spacing=2)


def build_tournament_view(store: DataStore) -> ft.Column:
    """Build the Tournament History tab content."""
    years = store.all_years
    df = store.tournaments
    matches_df = store.matches  # full match-level DataFrame

    # ── Year selector ─────────────────────────────────────────────────────
    year_dd = styled_dropdown(
        "Select Edition",
        [ft.dropdown.Option(str(y)) for y in years],
        value=str(years[-1]) if years else None,
        width=200,
    )

    # ── Team selector (US2/US3)  ──────────────────────────────────────────
    team_dd = styled_dropdown(
        "All Teams",
        [],   # populated on year change
        value=None,
        width=220,
    )

    # ── Detail card (updated on year change) ─────────────────────────────
    detail_col = ft.Column([], spacing=8)

    # ── Progression panel (updated on year/team change) ───────────────────
    progression_col = ft.Column([], spacing=4)

    def _render_progression(year: int, team: str | None) -> None:
        progression_col.controls.clear()
        prog = get_team_progression(matches_df, year=year, team=team or None)
        panel = _build_progression_panel(prog)
        title = "All Teams" if team is None else team
        progression_col.controls += [
            section_title(f"🔁 Team Progression — {title}"),
            panel,
        ]
        try:
            progression_col.update()
        except Exception:
            pass

    def _populate_team_dropdown(year: int) -> None:
        teams = get_teams_for_year(matches_df, year)
        team_dd.options = [ft.dropdown.Option("", "All Teams")] + [
            ft.dropdown.Option(t) for t in teams
        ]
        team_dd.value = None
        try:
            team_dd.update()
        except Exception:
            pass

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
            yr = int(year_dd.value)
            _render_detail(yr)
            _populate_team_dropdown(yr)
            _render_progression(yr, None)
            # reset team selection silently
            team_dd.value = None

    def _on_team_change(_: ft.ControlEvent) -> None:
        if year_dd.value:
            yr = int(year_dd.value)
            team = team_dd.value if team_dd.value else None
            _render_progression(yr, team)

    year_dd.on_change = _on_year_change
    team_dd.on_change = _on_team_change

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
        yr0 = years[-1]
        _render_detail(yr0)
        _populate_team_dropdown(yr0)
        _render_progression(yr0, None)

    return ft.Column(
        [
            page_header("🏆 Tournament History", "All FIFA World Cup editions 1930–2022"),
            ft.Row([year_dd, team_dd], spacing=12, wrap=True),
            card(detail_col),
            card(ft.Column([progression_col], scroll=ft.ScrollMode.AUTO), padding=12),
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
