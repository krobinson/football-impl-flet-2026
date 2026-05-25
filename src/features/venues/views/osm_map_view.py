"""OpenStreetMap tile-based venue map for FIFA World Cup 2026.

Uses flet-map (flutter_map) to render an interactive OSM map with
markers for the 16 host stadiums across the USA, Canada, and Mexico.
"""
from __future__ import annotations

import flet as ft
import flet_map as ftm
from core.venue_data import VENUES as _VENUES
from features.venues.components import venue_marker

# ── 2026 Host stadiums ────────────────────────────────────────────────────────
# Venue data is defined in shared/venue_data.py and imported above.


def build_osm_map_view(page: ft.Page) -> ft.Control:
    """Build an OSM tile map tab showing all 16 World Cup 2026 host venues."""

    info_text = ft.Text(
        "Tap a marker to see venue details",
        size=13,
        color=ft.Colors.GREY_400,
        italic=True,
    )

    def _on_marker_tap(venue: dict) -> None:
        flag = _FLAG.get(venue["country"], "🏟️")
        info_text.value = (
            f"{flag}  {venue['name']}  ·  {venue['city']}"
        )
        page.update()

    markers = [venue_marker(v, _on_marker_tap) for v in _VENUES]

    osm_map = ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(35.0, -95.0),
        initial_zoom=3.5,
        interaction_configuration=ftm.InteractionConfiguration(
            flags=ftm.InteractionFlag.ALL,
        ),
        layers=[
            ftm.TileLayer(
                url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                user_agent_package_name="worldcup2026-flet/1.0",
                on_image_error=lambda e: None,
            ),
            ftm.MarkerLayer(markers=markers),
            ftm.SimpleAttribution(
                text="© OpenStreetMap contributors",
                on_click=lambda e: page.launch_url(
                    "https://www.openstreetmap.org/copyright"
                ),
            ),
        ],
    )

    return ft.Column(
        controls=[
            ft.Text(
                "FIFA World Cup 2026 — Host Venues",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            ft.Row(
                controls=[
                    ft.Row([ft.Icon(ft.Icons.STADIUM, color=ft.Colors.BLUE_700, size=16),
                            ft.Text("USA", color=ft.Colors.GREY_300, size=12)], spacing=4),
                    ft.Row([ft.Icon(ft.Icons.STADIUM, color=ft.Colors.RED_700, size=16),
                            ft.Text("Canada", color=ft.Colors.GREY_300, size=12)], spacing=4),
                    ft.Row([ft.Icon(ft.Icons.STADIUM, color=ft.Colors.GREEN_700, size=16),
                            ft.Text("Mexico", color=ft.Colors.GREY_300, size=12)], spacing=4),
                    ft.Container(expand=True),
                    info_text,
                ],
                spacing=16,
            ),
            ft.Container(
                content=osm_map,
                expand=True,
                border_radius=8,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
        ],
        spacing=8,
        expand=True,
    )
