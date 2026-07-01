"""Match row and header row widgets for the schedule tab."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime

import flet as ft

from core.venue_data import city_to_stadium, venue_to_city
from core.ui_helpers import ACCENT, TEXT_PRIMARY, TEXT_SECONDARY

# ── Country flag map (TLA → Unicode emoji) ───────────────────────────────────

_TLA_FLAG: dict[str, str] = {
    "ALG": "🇩🇿",  # Algeria
    "ARG": "🇦🇷",  # Argentina
    "AUS": "🇦🇺",  # Australia
    "AUT": "🇦🇹",  # Austria
    "BEL": "🇧🇪",  # Belgium
    "BIH": "🇧🇦",  # Bosnia & Herzegovina
    "BRA": "🇧🇷",  # Brazil
    "CAN": "🇨🇦",  # Canada
    "CPV": "🇨🇻",  # Cape Verde
    "CIV": "🇨🇮",  # Ivory Coast
    "COD": "🇨🇩",  # DR Congo
    "COL": "🇨🇴",  # Colombia
    "CRO": "🇭🇷",  # Croatia
    "CUR": "🇨🇼",  # Curaçao
    "CZE": "🇨🇿",  # Czech Republic
    "ECU": "🇪🇨",  # Ecuador
    "EGY": "🇪🇬",  # Egypt
    "ENG": "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f",  # England
    "ESP": "🇪🇸",  # Spain
    "FRA": "🇫🇷",  # France
    "GER": "🇩🇪",  # Germany
    "GHA": "🇬🇭",  # Ghana
    "HAI": "🇭🇹",  # Haiti
    "IRN": "🇮🇷",  # Iran
    "IRQ": "🇮🇶",  # Iraq
    "JOR": "🇯🇴",  # Jordan
    "JPN": "🇯🇵",  # Japan
    "KOR": "🇰🇷",  # South Korea
    "KSA": "🇸🇦",  # Saudi Arabia
    "MAR": "🇲🇦",  # Morocco
    "MEX": "🇲🇽",  # Mexico
    "NED": "🇳🇱",  # Netherlands
    "NOR": "🇳🇴",  # Norway
    "NZL": "🇳🇿",  # New Zealand
    "PAN": "🇵🇦",  # Panama
    "PAR": "🇵🇾",  # Paraguay
    "POR": "🇵🇹",  # Portugal
    "QAT": "🇶🇦",  # Qatar
    "RSA": "🇿🇦",  # South Africa
    "SCO": "🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f",  # Scotland
    "SEN": "🇸🇳",  # Senegal
    "SUI": "🇨🇭",  # Switzerland
    "SWE": "🇸🇪",  # Sweden
    "TUN": "🇹🇳",  # Tunisia
    "TUR": "🇹🇷",  # Turkey
    "URU": "🇺🇾",  # Uruguay
    "USA": "🇺🇸",  # United States
    "UZB": "🇺🇿",  # Uzbekistan
}


def tla_to_flag(tla: str | None) -> str:
    """Return the Unicode flag emoji for a FIFA 3-letter team code.

    Returns an empty string if tla is None, empty, or not in the map.
    """
    if not tla:
        return ""
    return _TLA_FLAG.get(tla.upper(), "")


# ── Local venue fallback index ────────────────────────────────────────────────

def _build_venue_fallback() -> dict[tuple[str, str], str]:
    """Build (team1_lower, team2_lower) → stadium index from local 2026 fixtures."""
    _root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )
    fixture_path = os.path.join(_root, "data", "worldcup", "2026", "worldcup.json")
    try:
        with open(fixture_path, encoding="utf-8") as f:
            matches = json.load(f).get("matches", [])
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return {}

    index: dict[tuple[str, str], str] = {}
    for m in matches:
        team1 = m.get("team1", "")
        team2 = m.get("team2", "")
        ground = m.get("ground", "")
        if not (team1 and team2 and ground):
            continue
        stadium = city_to_stadium(ground)
        key = (team1.lower(), team2.lower())
        if key not in index:
            index[key] = stadium
    return index


_VENUE_FALLBACK: dict[tuple[str, str], str] = _build_venue_fallback()


def _resolve_venue(match: dict) -> str:
    """Return the best available venue name for a match dict.

    Uses API-provided venue first; falls back to the local 2026 fixture index
    keyed by (home_team_name, away_team_name).  Returns "TBD" if neither
    source resolves a venue.
    """
    api_venue = match.get("venue")
    if api_venue:
        return api_venue
    home = (match.get("homeTeam") or {}).get("name", "").lower()
    away = (match.get("awayTeam") or {}).get("name", "").lower()
    if home and away:
        stadium = _VENUE_FALLBACK.get((home, away))
        if stadium:
            return stadium
    return "TBD"


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
    home_team = match.get("homeTeam") or {}
    away_team = match.get("awayTeam") or {}
    home_name = home_team.get("name", "TBD")
    away_name = away_team.get("name", "TBD")
    home_flag = tla_to_flag(home_team.get("tla"))
    away_flag = tla_to_flag(away_team.get("tla"))
    score = _score_text(match)
    status_raw = match.get("status", "")
    status_label, status_colour = _STATUS_LABEL.get(
        status_raw, (status_raw.capitalize(), ft.Colors.GREY_500)
    )
    venue_name = _resolve_venue(match)
    matchday = str(match.get("matchday") or "—")
    grp_col = _group_colour(group_letter) if group_letter else ft.Colors.GREY_400

    home_text = f"{home_flag} {home_name}" if home_flag else home_name
    away_text = f"{away_flag} {away_name}" if away_flag else away_name

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
                    ft.Text(
                        home_text,
                        size=12,
                        color=TEXT_PRIMARY,
                    ),
                    width=150,
                ),
                # Away team
                ft.Container(
                    ft.Text(
                        away_text,
                        size=12,
                        color=TEXT_PRIMARY,
                    ),
                    width=150,
                ),
                # Score
                ft.Container(
                    ft.Text(
                        score,
                        size=12,
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=60,
                ),
                # Status
                ft.Container(
                    ft.Text(status_label, size=11, color=status_colour),
                    width=65,
                ),
                # Venue
                ft.Container(
                    ft.Text(venue_name, size=12, color=TEXT_SECONDARY),
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
                _h("Home", width=150),
                _h("Away", width=150),
                _h("Score", width=60),
                _h("Status", width=65),
                _h("Venue", width=140),
            ],
            spacing=4,
        ),
        bgcolor=ft.Colors.with_opacity(0.12, ACCENT),
        padding=ft.Padding.symmetric(vertical=6, horizontal=8),
        border_radius=ft.BorderRadius.only(top_left=6, top_right=6),
    )
