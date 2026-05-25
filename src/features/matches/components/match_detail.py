"""Match detail panel widget for the matches tab."""
from __future__ import annotations

import flet as ft
from core.ui_helpers import ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, section_title


def match_detail_controls(m: dict, events) -> list[ft.Control]:
    """Return a list of controls showing detail for a single match row.

    Args:
        m: Match dict with keys year, match_id, home_team, away_team,
           home_score, away_score, aet, date, stage, venue.
        events: DataFrame of goal events for this match.
    """
    home_score = int(m["home_score"])
    away_score = int(m["away_score"])
    score_str = f"{home_score}–{away_score}"
    if m.get("aet"):
        score_str += " (AET)"

    controls: list[ft.Control] = [
        section_title("📋 Match Detail"),
        ft.Text(
            f"{m['home_team']}  {score_str}  {m['away_team']}",
            size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
        ),
        ft.Text(f"{m['date']}  •  {m['stage']}  •  {m['venue']}", size=12, color=TEXT_SECONDARY),
    ]

    if events.empty:
        controls.append(
            ft.Text("No goalscorer data available.", color=TEXT_SECONDARY, size=12)
        )
    else:
        goal_rows = []
        for _, ev in events.iterrows():
            minute = (
                f"{int(float(ev['minute']))}''"
                if ev.get("minute") and str(ev["minute"]) not in ("nan", "", "None")
                else ""
            )
            etype = {"goal": "⚽", "own_goal": "🔴 OG", "penalty_goal": "⚽ (P)"}.get(
                ev["event_type"], "⚽"
            )
            goal_rows.append(
                ft.Text(f"{etype}  {ev['player']} ({ev['team']}) {minute}",
                        size=12, color=TEXT_PRIMARY)
            )
        controls += [
            ft.Text("Goalscorers:", size=13, color=ACCENT, weight=ft.FontWeight.BOLD)
        ] + goal_rows

    return controls
