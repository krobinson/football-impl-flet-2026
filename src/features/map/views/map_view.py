"""World Cup 2026 interactive map view — OSM tile + polygon edition.

Uses flet-map (flutter_map / OpenStreetMap) with PolygonLayer so each
qualifying country is drawn as a filled, bordered shape on the OSM tiles.
Clicking anywhere on a polygon selects that country via a geographic
point-in-polygon hit test (no pixel projection required).
"""
from __future__ import annotations

import flet as ft
import flet_map as ftm

from features.map.services import WorldCupDataService
from core.geo_utils import geo_hit_test
from features.map.models import GeoFeature, MapRenderState

# ── Colour palette (fill uses 40 % opacity so OSM tiles show through) ─────────
_FILL_QUALIFYING   = ft.Colors.with_opacity(0.40, ft.Colors.GREEN_500)
_FILL_ACTIVE_GROUP = ft.Colors.with_opacity(0.55, ft.Colors.ORANGE_500)
_FILL_DIMMED       = ft.Colors.with_opacity(0.25, ft.Colors.GREY_600)
_FILL_SELECTED     = ft.Colors.with_opacity(0.60, ft.Colors.RED_500)

_BORDER_QUALIFYING   = ft.Colors.GREEN_600
_BORDER_ACTIVE_GROUP = ft.Colors.ORANGE_700
_BORDER_DIMMED       = ft.Colors.GREY_500
_BORDER_SELECTED     = ft.Colors.RED_700


# ── Colour selector ───────────────────────────────────────────────────────────

def _poly_colours(
    iso_a3: str,
    state: MapRenderState,
    svc: WorldCupDataService,
) -> tuple[str, str]:
    """Return (fill_colour, border_colour) for a qualifying ISO code."""
    country = svc.get_team(iso_a3)

    if state.selected_country and state.selected_country.iso_a3 == iso_a3:
        return _FILL_SELECTED, _BORDER_SELECTED

    if state.active_group_filter:
        if country and country.group == state.active_group_filter:
            return _FILL_ACTIVE_GROUP, _BORDER_ACTIVE_GROUP
        return _FILL_DIMMED, _BORDER_DIMMED

    return _FILL_QUALIFYING, _BORDER_QUALIFYING


# ── GeoJSON → PolygonMarker list ──────────────────────────────────────────────

def _build_polygons(
    state: MapRenderState,
    svc: WorldCupDataService,
    features: list[GeoFeature],
) -> list[ftm.PolygonMarker]:
    """Convert qualifying-country GeoJSON rings to PolygonMarker objects."""
    polys: list[ftm.PolygonMarker] = []

    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        props = feature.get("properties", {})
        iso: str = props.get("ISO_A3", "")
        if iso == "-99":
            iso = props.get("ADM0_A3", "-99")
        if not svc.is_qualifier(iso):
            continue

        fill, border = _poly_colours(iso, state, svc)
        geo_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        rings: list[list[list[float]]] = (
            [coordinates[0]] if geo_type == "Polygon"
            else [p[0] for p in coordinates]   # MultiPolygon outer rings
        )

        for ring in rings:
            if len(ring) < 3:
                continue
            # GeoJSON coords are [lon, lat]; MapLatitudeLongitude wants (lat, lon)
            coords = [ftm.MapLatitudeLongitude(c[1], c[0]) for c in ring]
            polys.append(
                ftm.PolygonMarker(
                    coordinates=coords,
                    color=fill,
                    border_color=border,
                    border_stroke_width=1.5,
                )
            )

    return polys


# ── Declarative component ─────────────────────────────────────────────────────

@ft.component
def MapView(
    page: ft.Page,
    svc: WorldCupDataService,
    state: MapRenderState,
) -> ft.Control:
    """Interactive OSM + polygon map component.

    Derives polygon colours from *state* on each render.  Tap events write
    back to *state.selected_country*; the observable decorator triggers
    re-renders automatically.

    Args:
        page:  Flet page (used for launch_url on attribution click).
        svc:   World Cup data service.
        state: Shared MapRenderState — read for colours, written on tap.
    """
    features = svc.get_geo_features()

    def _on_map_tap(e: ftm.MapTapEvent) -> None:
        iso = geo_hit_test(e.coordinates.longitude, e.coordinates.latitude, features)
        state.selected_country = svc.get_team(iso) if iso else None

    osm_map = ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(20.0, 10.0),
        min_zoom=1.2,
        initial_zoom=2.5,
        interaction_configuration=ftm.InteractionConfiguration(
            flags=ftm.InteractionFlag.ALL,
        ),
        on_tap=_on_map_tap,
        layers=[
            ftm.TileLayer(
                url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                user_agent_package_name="worldcup2026-flet/1.0",
                on_image_error=lambda e: None,
            ),
            ftm.PolygonLayer(
                polygons=_build_polygons(state, svc, features),
                polygon_culling=True,
                simplification_tolerance=0.5,
            ),
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
                "FIFA World Cup 2026",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            ft.Text(
                "48 qualifying nations — click a country",
                size=13,
                color=ft.Colors.GREY_400,
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