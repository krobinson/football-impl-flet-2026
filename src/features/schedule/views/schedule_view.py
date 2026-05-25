"""Schedule view — 2026 FIFA World Cup pool match schedule.

Shows all 48 group-stage kick-off times (UTC), groups, and host cities
sourced live from football-data.org via FootballDataClient.
"""
from __future__ import annotations

import threading

import flet as ft

from core.network import ApiKeyMissingError, ApiError, FootballDataClient
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR,
)
from features.schedule.components import match_row, header_row
from core.components import page_header, styled_dropdown, loading_row


# ── Main builder ──────────────────────────────────────────────────────────────

def build_schedule_view(
    fd_client: FootballDataClient | None = None,
) -> ft.Column:
    """Build the 2026 pool schedule tab."""

    group_dd = styled_dropdown(
        "Group",
        [ft.dropdown.Option("All")]
        + [ft.dropdown.Option(f"GROUP_{c}", f"Group {c}") for c in "ABCDEFGHIJKL"],
        value="All",
        width=160,
    )
    lr = loading_row([group_dd])

    rows_col = ft.Column([], spacing=2, scroll=ft.ScrollMode.AUTO, expand=True)

    _state: dict = {"all_matches": []}

    def _render_matches(matches: list[dict]) -> None:
        sorted_matches = sorted(
            matches,
            key=lambda m: (m.get("matchday") or 99, m.get("utcDate") or ""),
        )
        rows_col.controls = [header_row()] + [
            match_row(m, i) for i, m in enumerate(sorted_matches)
        ]
        try:
            rows_col.update()
        except Exception:
            pass

    def _apply_group_filter(_: ft.ControlEvent | None = None) -> None:
        sel = group_dd.value or "All"
        matches = _state["all_matches"]
        if sel != "All":
            matches = [m for m in matches if m.get("group") == sel]
        _render_matches(matches)

    group_dd.on_change = _apply_group_filter

    def _load() -> None:
        if fd_client is None:
            lr.notice.value = "⚠️  Set FOOTBALL_DATA_API_KEY to load the live 2026 schedule."
            lr.notice.visible = True
            try:
                lr.notice.update()
            except Exception:
                pass
            return

        lr.ring.visible = True
        lr.notice.value = ""
        lr.notice.visible = False
        try:
            lr.ring.update()
        except Exception:
            pass

        try:
            matches = fd_client.get_group_matches(season=2026)
            _state["all_matches"] = matches
            _apply_group_filter()
            lr.notice.value = f"✅  {len(matches)} group-stage matches loaded from football-data.org (UTC times)"
            lr.notice.visible = True
        except ApiKeyMissingError as exc:
            lr.notice.value = f"⚠️  {exc}"
            lr.notice.visible = True
        except (ApiError, OSError) as exc:
            lr.notice.value = f"⚠️  API error — {exc}"
            lr.notice.visible = True
        finally:
            lr.ring.visible = False
            try:
                lr.ring.update()
                lr.notice.update()
            except Exception:
                pass

    # Kick off fetch in background so the tab renders immediately
    threading.Thread(target=_load, daemon=True).start()

    return ft.Column(
        [
            ft.Text("📅  2026 World Cup Pool Schedule", size=22,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text("Group-stage kick-off times are shown in UTC",
                    size=13, color=TEXT_SECONDARY),
            ft.Divider(color=BORDER_COLOR, height=1),
            lr.row,
            lr.notice,
            ft.Container(
                rows_col,
                bgcolor=BG_CARD,
                border_radius=8,
                padding=ft.Padding.symmetric(vertical=4, horizontal=0),
                border=ft.Border.all(1, BORDER_COLOR),
                expand=True,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
