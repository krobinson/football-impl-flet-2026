"""OpenStreetMap tile-based venue map for FIFA World Cup 2026.

Displays three regional panels:
  West  — Vancouver, Seattle, San Francisco Bay Area, Los Angeles
  East  — Toronto, Boston, New York/NJ, Philadelphia, Atlanta, Miami,
           Kansas City, Dallas
  Mexico — Guadalajara, Mexico City, Monterrey, Puebla
"""
from __future__ import annotations

import flet as ft
import flet_map as ftm
from core.venue_data import VENUES as _VENUES
from features.venues.components import venue_marker

_FLAG: dict[str, str] = {
    "USA": "🇺🇸",
    "CAN": "🇨🇦",
    "MEX": "🇲🇽",
}

# ── Region definitions ────────────────────────────────────────────────────────
# Each tuple: (label, filter_fn, center_lat, center_lon, initial_zoom)
_REGIONS = [
    (
        "🌊 West Coast",
        lambda v: v["country"] in ("USA", "CAN") and v["lon"] <= -110.0,
        43.0, -121.5, 5.0,
    ),
    (
        "🗽 East & Central",
        lambda v: v["country"] in ("USA", "CAN") and v["lon"] > -110.0,
        36.5, -84.0, 4.5,
    ),
    (
        "🌮 Mexico",
        lambda v: v["country"] == "MEX",
        20.3, -100.8, 6.0,
    ),
]


def _make_map(
    venues: list[dict],
    center_lat: float,
    center_lon: float,
    zoom: float,
    on_tap,
) -> ftm.Map:
    markers = [venue_marker(v, on_tap) for v in venues]
    return ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(center_lat, center_lon),
        initial_zoom=zoom,
        min_zoom=2.5,
        max_zoom=12.0,
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
                on_click=lambda e: None,
            ),
        ],
    )


def build_osm_map_view(page: ft.Page) -> ft.Control:
    """Build a three-panel regional venue map for FIFA World Cup 2026."""

    info_text = ft.Text(
        "Tap a marker to see venue details",
        size=13,
        color=ft.Colors.GREY_400,
        italic=True,
    )

    def _on_marker_tap(venue: dict) -> None:
        flag = _FLAG.get(venue["country"], "🏟️")
        info_text.value = f"{flag}  {venue['name']}  ·  {venue['city']}"
        info_text.update()

    # Build one panel per region
    region_panels: list[ft.Control] = []
    for label, filter_fn, clat, clon, zoom in _REGIONS:
        region_venues = [v for v in _VENUES if filter_fn(v)]
        region_map = _make_map(region_venues, clat, clon, zoom, _on_marker_tap)
        panel = ft.Column(
            [
                ft.Text(label, size=14, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Container(
                    content=region_map,
                    expand=True,
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
            ],
            spacing=4,
            expand=True,
        )
        region_panels.append(panel)

    legend = ft.Row(
        [
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
    )

    return ft.Column(
        [
            ft.Text(
                "FIFA World Cup 2026 — Host Venues",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            legend,
            ft.Row(
                region_panels,
                spacing=8,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ],
        spacing=8,
        expand=True,
    )

