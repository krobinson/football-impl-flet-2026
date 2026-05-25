"""Domain models for the FIFA World Cup 2026 map application."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import flet as ft


@dataclass(frozen=True)
class ParticipatingCountry:
    """A country participating in FIFA World Cup 2026."""

    iso_a3: str
    name: str
    group: str
    appearances: int
    flag_emoji: str


@dataclass(frozen=True)
class FIFAGroup:
    """A FIFA World Cup group containing four countries."""

    name: str  # "A" … "L"
    countries: tuple[ParticipatingCountry, ...]


# Type alias for a raw GeoJSON feature dict (opaque at this layer).
GeoFeature = dict[str, Any]


@ft.observable
@dataclass
class MapRenderState:
    """Mutable runtime rendering state for the world-map canvas."""

    canvas_width: float = 800.0
    canvas_height: float = 400.0
    active_group_filter: str | None = None  # "A"–"L" or None
    selected_country: ParticipatingCountry | None = None
    pan_x: float = 0.0
    pan_y: float = 0.0
    zoom: float = 1.0

    def reset_view(self) -> None:
        """Reset pan and zoom to default."""
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.zoom = 1.0
