"""Shared UI helpers for the Flet World Cup Explorer views."""
from __future__ import annotations

import flet as ft

# ── Colour palette ────────────────────────────────────────────────────────────
BG_CARD = "#16213E"
BG_PAGE = "#1A1A2E"
ACCENT = "#F4A261"
GREEN = "#1a472a"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#B0B8C8"
BORDER_COLOR = "#2C3E50"

BAR_COLOURS = [
    "#2ECC71", "#3498DB", "#E74C3C", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E67E22", "#34495E",
]


def card(content: ft.Control, padding: int = 16) -> ft.Container:
    """Wrap a control in a styled card container."""
    return ft.Container(
        content=content,
        bgcolor=BG_CARD,
        border_radius=8,
        padding=padding,
        margin=ft.Margin.only(bottom=8),
    )


def section_title(text: str) -> ft.Text:
    return ft.Text(text, size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)


def label(text: str) -> ft.Text:
    return ft.Text(text, size=13, color=TEXT_SECONDARY)


def value_text(text: str, size: int = 14) -> ft.Text:
    return ft.Text(str(text), size=size, color=TEXT_PRIMARY)


def stat_badge(label_: str, value: str, colour: str = ACCENT) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=colour),
                ft.Text(label_, size=11, color=TEXT_SECONDARY),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        bgcolor=BG_PAGE,
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        border=ft.Border.all(1, BORDER_COLOR),
    )


def build_bar_chart(
    labels: list[str],
    values: list[float],
    title: str,
    colour: str = "#2ECC71",
    bar_height: int = 18,
    max_width: int = 400,
) -> ft.Column:
    """Build a simple horizontal bar chart from labels + values."""
    if not values:
        return ft.Column([ft.Text("No data", color=TEXT_SECONDARY)])

    max_val = max(values) or 1
    rows: list[ft.Control] = [section_title(title)]

    for lbl, val in zip(labels, values):
        bar_w = max(2, int(val / max_val * max_width))
        rows.append(
            ft.Row(
                [
                    ft.Container(
                        ft.Text(str(lbl), size=11, color=TEXT_SECONDARY),
                        width=50,
                    ),
                    ft.Container(
                        bgcolor=colour,
                        width=bar_w,
                        height=bar_height,
                        border_radius=3,
                    ),
                    ft.Text(f"{val:.0f}", size=11, color=TEXT_SECONDARY),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    return ft.Column(rows, spacing=4, scroll=ft.ScrollMode.AUTO)


def build_data_table(
    columns: list[str],
    rows: list[list[str]],
    on_select: "callable[[int], None] | None" = None,
) -> ft.DataTable:
    """Build a styled ft.DataTable."""
    def _make_row(idx: int, cells: list[str]) -> ft.DataRow:
        return ft.DataRow(
            cells=[ft.DataCell(ft.Text(str(c), size=12, color=TEXT_PRIMARY)) for c in cells],
            on_select_change=(lambda e, i=idx: on_select(i)) if on_select else None,
        )

    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(c, size=12, weight=ft.FontWeight.BOLD, color=ACCENT))
            for c in columns
        ],
        rows=[_make_row(i, r) for i, r in enumerate(rows)],
        bgcolor=BG_CARD,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=8,
        heading_row_color=BG_PAGE,
        data_row_min_height=32,
        column_spacing=16,
    )


def scrollable_card(content: ft.Control, height: int = 350) -> ft.Container:
    return ft.Container(
        content=ft.Column([content], scroll=ft.ScrollMode.AUTO, expand=True),
        bgcolor=BG_CARD,
        border_radius=8,
        padding=12,
        height=height,
        border=ft.Border.all(1, BORDER_COLOR),
    )
