"""Schedule view — 2026 FIFA World Cup pool match schedule.

Shows all 48 group-stage kick-off times (UTC), groups, and host cities
sourced from openfootball worldcup.json URL (no API key required) or
football-data.org API (with API key).
"""
from __future__ import annotations

import threading

import flet as ft

from core.network import ApiKeyMissingError, ApiError, FootballDataClient
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR,
)
from features.schedule.components import match_row, header_row
from features.schedule.services.worldcup_json_service import WorldCupJsonService, WorldCupDataError
from core.components import page_header, loading_row

_CHIP_ACTIVE_BG = "#F39C12"
_CHIP_INACTIVE_BG = "#2C3E50"
_CHIP_TEXT_ACTIVE = "#000000"
_CHIP_TEXT_INACTIVE = "#ECF0F1"

_GROUP_LETTERS = list("ABCDEFGHIJKL")


# ── Group chip row (T003) ────────────────────────────────────────────────────────────────────

def _build_group_chips(
    active_group: str,
    on_select,
) -> ft.Row:
    """Return a chip row for All + A–L group selection."""
    def _chip(label: str) -> ft.Container:
        is_active = label == active_group
        return ft.Container(
            content=ft.Text(
                label,
                size=12,
                weight=ft.FontWeight.W_600,
                color=_CHIP_TEXT_ACTIVE if is_active else _CHIP_TEXT_INACTIVE,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=20,
            bgcolor=_CHIP_ACTIVE_BG if is_active else _CHIP_INACTIVE_BG,
            on_click=lambda e, lbl=label: on_select(lbl),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    return ft.Row(
        controls=[_chip("All")] + [_chip(c) for c in _GROUP_LETTERS],
        wrap=True,
        spacing=6,
        run_spacing=6,
    )


# ── Main builder ──────────────────────────────────────────────────────────────

def build_schedule_view(
    fd_client: FootballDataClient | None = None,
    wc_service: WorldCupJsonService | None = None,
) -> ft.Column:
    """Build the 2026 pool schedule tab.
    
    Args:
        fd_client: Optional FootballDataClient for API-based data (requires API key)
        wc_service: Optional WorldCupJsonService for URL-based data (no API key required)
    
    Priority: wc_service takes precedence over fd_client if both are provided.
    """

    lr = loading_row([])
    rows_col = ft.Column([], spacing=2, scroll=ft.ScrollMode.AUTO, expand=True)
    _state: dict = {"all_matches": [], "active_group": "All", "data_source": ""}

    # chips_row is rebuilt on each selection to reflect active state
    chips_row = ft.Row(wrap=True, spacing=6, run_spacing=6)

    def _rebuild_chips() -> None:
        chips_row.controls = _build_group_chips(
            _state["active_group"], _on_chip_select
        ).controls
        try:
            chips_row.update()
        except Exception:
            pass

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

    def _apply_group_filter() -> None:
        sel = _state["active_group"]
        matches = _state["all_matches"]
        if sel != "All":
            matches = [m for m in matches if m.get("group") == f"GROUP_{sel}"]
        _render_matches(matches)

    def _on_chip_select(label: str) -> None:
        _state["active_group"] = label
        _rebuild_chips()
        _apply_group_filter()

    # Seed the chip row with initial state (All active)
    chips_row.controls = _build_group_chips("All", _on_chip_select).controls

    def _load() -> None:
        # Priority: wc_service (URL-based, no API key) > fd_client (API-based)
        if wc_service is not None:
            # Use WorldCupJsonService (URL-based, no API key required)
            lr.ring.visible = True
            lr.notice.value = ""
            lr.notice.visible = False
            try:
                lr.ring.update()
            except Exception:
                pass

            try:
                matches = wc_service.get_group_matches()
                _state["all_matches"] = matches
                _state["data_source"] = wc_service.get_data_source()
                _apply_group_filter()
                
                source_label = "openfootball data (URL)" if _state["data_source"] == "url" else "local file"
                lr.notice.value = f"✅  {len(matches)} group-stage matches loaded from {source_label}"
                lr.notice.visible = True
            except WorldCupDataError as exc:
                lr.notice.value = f"⚠️  Failed to load data: {exc}"
                lr.notice.visible = True
            except (OSError, RuntimeError) as exc:
                lr.notice.value = f"⚠️  Error loading data — {exc}"
                lr.notice.visible = True
            finally:
                lr.ring.visible = False
                try:
                    lr.ring.update()
                    lr.notice.update()
                except Exception:
                    pass
        elif fd_client is not None:
            # Fall back to FootballDataClient (API-based, requires API key)
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
                _state["data_source"] = "api"
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
        else:
            # No data source available
            lr.notice.value = "⚠️  No data source configured. Provide WorldCupJsonService or FootballDataClient."
            lr.notice.visible = True
            try:
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
            chips_row,
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
