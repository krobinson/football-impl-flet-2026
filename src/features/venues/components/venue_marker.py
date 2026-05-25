"""Venue marker widget for the OSM map view."""
from __future__ import annotations

from typing import Callable

import flet as ft
import flet_map as ftm

_FLAG = {"USA": "🇺🇸", "CAN": "🇨🇦", "MEX": "🇲🇽"}
_COLOR = {"USA": ft.Colors.BLUE_700, "CAN": ft.Colors.RED_700, "MEX": ft.Colors.GREEN_700}


def venue_marker(venue: dict, on_tap: Callable[[dict], None]) -> ftm.Marker:
    """Return a styled map marker for a single venue dict."""
    return ftm.Marker(
        coordinates=ftm.MapLatitudeLongitude(venue["lat"], venue["lon"]),
        content=ft.GestureDetector(
            content=ft.Icon(
                ft.Icons.STADIUM,
                color=_COLOR.get(venue["country"], ft.Colors.YELLOW_700),
                size=28,
                tooltip=f"{venue['name']}\n{venue['city']}",
            ),
            on_tap=lambda e, v=venue: on_tap(v),
        ),
    )
