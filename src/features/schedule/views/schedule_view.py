"""Schedule view — 2026 FIFA World Cup tournament schedule.

Shows all 104 matches (72 group stage + 32 knockout) with scores,
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
from features.schedule.components.stage_chips import build_stage_chips
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
    _state: dict = {
        "all_matches": [],
        "active_stage": "ALL",
        "active_group": "All",
        "data_source": "",
    }

    # Stage chips row
    stage_chips_row = ft.Row(wrap=True, spacing=6, run_spacing=6)

    # Group chips row (visible only when stage is GROUP_STAGE)
    group_chips_row = ft.Row(wrap=True, spacing=6, run_spacing=6)
    group_chips_container = ft.Container(
        content=group_chips_row,
        visible=False,
    )

    def _rebuild_stage_chips() -> None:
        stage_chips_row.controls = build_stage_chips(
            _state["active_stage"], _on_stage_select
        ).controls
        try:
            stage_chips_row.update()
        except Exception:
            pass

    def _rebuild_group_chips() -> None:
        group_chips_row.controls = _build_group_chips(
            _state["active_group"], _on_chip_select
        ).controls
        try:
            group_chips_row.update()
        except Exception:
            pass

    def _update_group_chips_visibility() -> None:
        group_chips_container.visible = _state["active_stage"] == "GROUP_STAGE"
        try:
            group_chips_container.update()
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

    def _apply_filters() -> None:
        matches = _state["all_matches"]
        stage = _state["active_stage"]
        group = _state["active_group"]

        # Apply stage filter
        if stage != "ALL":
            matches = [m for m in matches if m.get("stage") == stage]

        # Apply group filter (only when stage is GROUP_STAGE)
        if stage == "GROUP_STAGE" and group != "All":
            matches = [m for m in matches if m.get("group") == f"GROUP_{group}"]

        _render_matches(matches)

    def _on_stage_select(stage: str) -> None:
        _state["active_stage"] = stage
        # Reset group filter when changing stage
        _state["active_group"] = "All"
        _rebuild_stage_chips()
        _rebuild_group_chips()
        _update_group_chips_visibility()
        _apply_filters()

    def _on_chip_select(label: str) -> None:
        _state["active_group"] = label
        _rebuild_group_chips()
        _apply_filters()

    # Seed the chip rows with initial state
    stage_chips_row.controls = build_stage_chips("ALL", _on_stage_select).controls
    group_chips_row.controls = _build_group_chips("All", _on_chip_select).controls

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
                matches = wc_service.get_all_matches()
                _state["all_matches"] = matches
                _state["data_source"] = wc_service.get_data_source()
                _apply_filters()
                
                source_label = "openfootball data (URL)" if _state["data_source"] == "url" else "local file"
                lr.notice.value = f"✅  {len(matches)} matches loaded from {source_label}"
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
                _apply_filters()
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
            ft.Text("📅  2026 World Cup Schedule", size=22,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text("All matches with kick-off times in UTC",
                    size=13, color=TEXT_SECONDARY),
            ft.Divider(color=BORDER_COLOR, height=1),
            stage_chips_row,
            group_chips_container,
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
