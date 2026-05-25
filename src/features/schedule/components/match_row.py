"""Match row and header row widgets for the schedule tab."""
from __future__ import annotations

from datetime import datetime

import flet as ft

from core.venue_data import venue_to_city
from core.ui_helpers import ACCENT, TEXT_PRIMARY, TEXT_SECONDARY

# ── Helpers ───────────────────────────────────────────────────────────────────

_STATUS_LABEL: dict[str, tuple[str, str]] = {
    # status → (display text, colour)
    "SCHEDULED":  ("Scheduled",    ft.Colors.GREY_500),
    "TIMED":      ("Confirmed",    ft.Colors.BLUE_400),
    "IN_PLAY":    ("LIVE",         ft.Colors.GREEN_400),
    "PAUSED":     ("HT",           ft.Colors.ORANGE_400),
    "FINISHED":   ("FT",           ft.Colors.GREY_400),
    "POSTPONED":  ("Postponed",    ft.Colors.RED_400),
    "CANCELLED":  ("Cancelled",    ft.Colors.RED_600),
    "SUSPENDED":  ("Suspended",    ft.Colors.RED_400),
    "AWARDED":    ("Awarded",      ft.Colors.PURPLE_400),
}

_GROUP_COLOURS: list[str] = [
    ft.Colors.BLUE_200, ft.Colors.GREEN_200, ft.Colors.ORANGE_200,
    ft.Colors.PURPLE_200, ft.Colors.CYAN_200, ft.Colors.YELLOW_200,
    ft.Colors.RED_200, ft.Colors.TEAL_200, ft.Colors.PINK_200,
    ft.Colors.LIME_200, ft.Colors.AMBER_200, ft.Colors.INDIGO_200,
]


def _group_colour(letter: str) -> str:
    idx = (ord(letter.upper()) - ord("A")) % len(_GROUP_COLOURS)
    return _GROUP_COLOURS[idx]


def _fmt_utc(utc_str: str) -> tuple[str, str]:
    """Return (date_str, time_str) from an ISO-8601 UTC date string."""
    if not utc_str:
        return ("—", "—")
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")
    except ValueError:
        parts = utc_str[:16].split("T")
        return parts[0], parts[1] if len(parts) > 1 else "—"


def _score_text(match: dict) -> str:
    ft_score = (match.get("score") or {}).get("fullTime") or {}
    h, a = ft_score.get("home"), ft_score.get("away")
    if h is not None and a is not None:
        return f"{h}–{a}"
    return "vs"


# ── Public widgets ────────────────────────────────────────────────────────────

def match_row(match: dict, row_idx: int) -> ft.Container:
    """Return a styled row container for a single match."""
    date_str, time_str = _fmt_utc(match.get("utcDate", ""))
    group_raw = match.get("group") or ""
    group_letter = group_raw.replace("GROUP_", "")
    home = (match.get("homeTeam") or {}).get("name", "TBD")
    away = (match.get("awayTeam") or {}).get("name", "TBD")
    score = _score_text(match)
    status_raw = match.get("status", "")
    status_label, status_colour = _STATUS_LABEL.get(
        status_raw, (status_raw.capitalize(), ft.Colors.GREY_500)
    )
    city = venue_to_city(match.get("venue") or "")
    matchday = str(match.get("matchday") or "—")
    grp_col = _group_colour(group_letter) if group_letter else ft.Colors.GREY_400

    row_bg = ft.Colors.with_opacity(0.04 if row_idx % 2 == 0 else 0.0, ft.Colors.WHITE)

    return ft.Container(
        content=ft.Row(
            [
                # Matchday
                ft.Container(
                    ft.Text(matchday, size=12, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                    width=60,
                ),
                # Date
                ft.Container(
                    ft.Text(date_str, size=12, color=TEXT_PRIMARY),
                    width=90,
                ),
                # Time UTC
                ft.Container(
                    ft.Text(time_str + " UTC", size=12, color=TEXT_SECONDARY),
                    width=75,
                ),
                # Group badge
                ft.Container(
                    ft.Text(
                        f"Grp {group_letter}", size=11, weight=ft.FontWeight.BOLD,
                        color=grp_col,
                    ),
                    width=55,
                ),
                # Home team
                ft.Container(
                    ft.Text(home, size=12, color=TEXT_PRIMARY, text_align=ft.TextAlign.RIGHT),
                    expand=True,
                ),
                # Score / vs
                ft.Container(
                    ft.Text(
                        score, size=13, weight=ft.FontWeight.BOLD,
                        color=ACCENT if score != "vs" else TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=50,
                ),
                # Away team
                ft.Container(
                    ft.Text(away, size=12, color=TEXT_PRIMARY),
                    expand=True,
                ),
                # Status
                ft.Container(
                    ft.Text(status_label, size=11, color=status_colour),
                    width=65,
                ),
                # City
                ft.Container(
                    ft.Text(city, size=12, color=TEXT_SECONDARY),
                    width=140,
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=row_bg,
        padding=ft.Padding.symmetric(vertical=6, horizontal=8),
        border_radius=4,
    )


def header_row() -> ft.Container:
    """Return the column-header row for the schedule table."""
    def _h(label: str, width: int | None = None, expand: bool = False) -> ft.Container:
        return ft.Container(
            ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=ACCENT),
            width=width,
            expand=expand,
        )

    return ft.Container(
        content=ft.Row(
            [
                _h("Day", width=60),
                _h("Date", width=90),
                _h("Time", width=75),
                _h("Group", width=55),
                _h("Home", expand=True),
                _h("Score", width=50),
                _h("Away", expand=True),
                _h("Status", width=65),
                _h("City", width=140),
            ],
            spacing=4,
        ),
        bgcolor=ft.Colors.with_opacity(0.12, ACCENT),
        padding=ft.Padding.symmetric(vertical=6, horizontal=8),
        border_radius=ft.BorderRadius.only(top_left=6, top_right=6),
    )
