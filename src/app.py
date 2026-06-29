"""Entry point for the FIFA World Cup 2026 app – 3-tab layout."""
from __future__ import annotations

import flet as ft

from features.map.services import WorldCupDataService
from core.network import FootballDataClient
from features.map.components import GroupFilter, InfoPanel, MapView
from features.map.models import MapRenderState
from features.venues.views.osm_map_view import build_osm_map_view
from features.schedule.views.schedule_view import build_schedule_view
from features.schedule.services.worldcup_json_service import WorldCupJsonService

_BG = "#1A1A2E"


def _build_app(
    page: ft.Page,
    svc: WorldCupDataService,
    fd_client: "FootballDataClient | None",
    wc_service: "WorldCupJsonService | None",
) -> ft.Control:
    """Root component body — called inside page.render() for a Renderer context."""

    # ── Map tab — responsive ─────────────────────────────────────────────
    _MOBILE_BREAKPOINT = 650

    map_state = MapRenderState(canvas_width=800.0, canvas_height=400.0)
    filter_row   = GroupFilter(groups=svc.get_groups(), state=map_state)
    map_control  = MapView(page=page, svc=svc, state=map_state)
    info_control = InfoPanel(state=map_state)

    map_body_ref = ft.Ref[ft.Column]()

    def _build_map_body(mobile: bool) -> ft.Control:
        if mobile:
            map_height = max(280, int((page.height or 600) * 0.55))
            return ft.Column(
                [
                    ft.Container(map_control, height=map_height, clip_behavior=ft.ClipBehavior.HARD_EDGE),
                    info_control,
                ],
                spacing=12,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            )
        return ft.Row(
            [
                ft.Container(map_control, expand=True),
                ft.Container(info_control, width=300),
            ],
            spacing=12,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    _mobile = (page.width or 1200) < _MOBILE_BREAKPOINT
    map_inner = ft.Column(
        controls=[filter_row, _build_map_body(_mobile)],
        ref=map_body_ref,
        spacing=12,
        expand=True,
    )
    map_tab_content = ft.Container(
        map_inner,
        padding=ft.Padding.only(left=16, right=16, top=12, bottom=0),
        bgcolor=_BG,
        expand=True,
    )

    def _on_resized(_: ft.ControlEvent) -> None:
        is_mobile = (page.width or 1200) < _MOBILE_BREAKPOINT
        nav.label_behavior = (
            ft.NavigationBarLabelBehavior.ALWAYS_HIDE
            if is_mobile
            else ft.NavigationBarLabelBehavior.ALWAYS_SHOW
        )
        if map_body_ref.current:
            map_body_ref.current.controls[-1] = _build_map_body(is_mobile)
            try:
                map_body_ref.current.update()
                nav.update()
            except Exception:
                pass

    page.on_resized = _on_resized

    osm_content = ft.Container(
        build_osm_map_view(page),
        padding=ft.Padding.only(left=16, right=16, top=12, bottom=0),
        bgcolor=_BG,
        expand=True,
    )
    schedule_content = ft.Container(
        build_schedule_view(fd_client, wc_service),
        padding=16, bgcolor=_BG, expand=True,
    )

    # ── Navigation ────────────────────────────────────────────────────────
    tab_bodies = [
        map_tab_content,
        osm_content,
        schedule_content,
    ]

    body = ft.Stack([
        ft.Container(c, expand=True, visible=(i == 0))
        for i, c in enumerate(tab_bodies)
    ], expand=True)

    nav = ft.NavigationBar(
        selected_index=0,
        bgcolor="#16213E",
        indicator_color="#F4A261",
        label_behavior=(
            ft.NavigationBarLabelBehavior.ALWAYS_HIDE
            if _mobile
            else ft.NavigationBarLabelBehavior.ALWAYS_SHOW
        ),
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.MAP_OUTLINED,
                                        selected_icon=ft.Icons.MAP, label="2026 Map"),
            ft.NavigationBarDestination(icon=ft.Icons.PUBLIC_OUTLINED,
                                        selected_icon=ft.Icons.PUBLIC, label="Venues"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                                        selected_icon=ft.Icons.CALENDAR_MONTH, label="Schedule"),
        ],
    )

    def on_nav_change(e: ft.ControlEvent) -> None:
        idx = e.control.selected_index
        for i, child in enumerate(body.controls):
            child.visible = i == idx
        body.update()

    nav.on_change = on_nav_change

    return ft.Column(
        [body, nav],
        spacing=0,
        expand=True,
    )


def main(page: ft.Page) -> None:
    page.title = "FIFA World Cup – History & 2026"
    page.bgcolor = _BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1200
    page.window.height = 780

    # ── Data ──────────────────────────────────────────────────────────────
    try:
        svc = WorldCupDataService()
    except (FileNotFoundError, ValueError) as exc:
        page.add(ft.Text(f"Map data error: {exc}", color=ft.Colors.RED_400, size=16))
        return

    # football-data.org client (None when FOOTBALL_DATA_API_KEY is not set)
    fd_client: FootballDataClient | None
    try:
        fd_client = FootballDataClient()
    except Exception:
        fd_client = None

    # openfootball worldcup.json service (no API key required)
    wc_service: WorldCupJsonService | None
    try:
        wc_service = WorldCupJsonService()
    except Exception:
        wc_service = None

    page.render(_build_app, page, svc, fd_client, wc_service)
