"""Geo-projection and hit-testing utilities (stdlib only, no Shapely)."""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from features.map.models import GeoFeature

# Full latitude bounds — shows entire world including Antarctica.
_LAT_MAX = 90.0   # degrees north
_LAT_MIN = -90.0  # degrees south
_LAT_RANGE = _LAT_MAX - _LAT_MIN  # 180°
# Canvas aspect ratio implied by these bounds: 360 / 180 = 2.0
MAP_ASPECT_RATIO: float = 360.0 / _LAT_RANGE


def project(
    lon: float,
    lat: float,
    width: float,
    height: float,
) -> tuple[float, float]:
    """Map (longitude, latitude) to canvas pixel coordinates.

    Uses a cropped equirectangular projection (lat clamped to
    ``_LAT_MIN`` … ``_LAT_MAX``) so Australia remains clearly visible
    and Antarctica is largely omitted.

    Args:
        lon: Longitude in decimal degrees (-180 … 180).
        lat: Latitude in decimal degrees (clamped to _LAT_MIN … _LAT_MAX).
        width: Canvas width in pixels.
        height: Canvas height in pixels.

    Returns:
        (x, y) pixel coordinates.
    """
    x = (lon + 180.0) / 360.0 * width
    y = (_LAT_MAX - lat) / _LAT_RANGE * height
    return x, y


def _point_in_polygon(px: float, py: float, ring: list[list[float]]) -> bool:
    """Ray-casting algorithm: returns True if (px, py) is inside *ring*.

    Ring coordinates are geographic (lon, lat), so we work directly in
    geographic space to avoid round-trip projection errors.
    """
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-10) + xi):
            inside = not inside
        j = i
    return inside


def _canvas_to_geo(
    px: float,
    py: float,
    width: float,
    height: float,
) -> tuple[float, float]:
    """Inverse cropped equirectangular: pixel → (lon, lat)."""
    lon = px / width * 360.0 - 180.0
    lat = _LAT_MAX - py / height * _LAT_RANGE
    return lon, lat


def hit_test(
    px: float,
    py: float,
    features: list["GeoFeature"],
    width: float,
    height: float,
) -> str | None:
    """Return the ISO-A3 code of the country whose polygon contains (px, py).

    Args:
        px: Canvas x coordinate of the tap/click.
        py: Canvas y coordinate of the tap/click.
        features: List of GeoJSON Feature dicts from countries.geojson.
        width: Canvas width in pixels.
        height: Canvas height in pixels.

    Returns:
        ISO-A3 string (from feature properties "ISO_A3") or None if no match.
    """
    lon, lat = _canvas_to_geo(px, py, width, height)

    for feature in features:
        geometry = feature.get("geometry")
        if geometry is None:
            continue
        geo_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])
        props = feature.get("properties", {})
        iso_a3: str = props.get("ISO_A3", "")
        # Some Natural Earth features have ISO_A3 = "-99"; fall back to ADM0_A3.
        if iso_a3 == "-99":
            iso_a3 = props.get("ADM0_A3", "-99")

        if geo_type == "Polygon":
            outer_ring = coordinates[0]
            if _point_in_polygon(lon, lat, outer_ring):
                return iso_a3

        elif geo_type == "MultiPolygon":
            for polygon in coordinates:
                outer_ring = polygon[0]
                if _point_in_polygon(lon, lat, outer_ring):
                    return iso_a3

    return None


def geo_hit_test(
    lon: float,
    lat: float,
    features: "list[GeoFeature]",
) -> str | None:
    """Return the ISO-A3 of the country containing geographic point (lon, lat).

    Unlike ``hit_test``, this operates directly in geographic space — no pixel
    projection needed.  Use with ``ftm.Map.on_tap`` which provides lat/lon.

    Args:
        lon: Tap longitude in decimal degrees.
        lat: Tap latitude in decimal degrees.
        features: List of GeoJSON Feature dicts from countries.geojson.

    Returns:
        ISO-A3 string or None if no polygon contains the point.
    """
    for feature in features:
        geometry = feature.get("geometry")
        if geometry is None:
            continue
        geo_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])
        props = feature.get("properties", {})
        iso_a3: str = props.get("ISO_A3", "")
        if iso_a3 == "-99":
            iso_a3 = props.get("ADM0_A3", "-99")

        if geo_type == "Polygon":
            if _point_in_polygon(lon, lat, coordinates[0]):
                return iso_a3
        elif geo_type == "MultiPolygon":
            for polygon in coordinates:
                if _point_in_polygon(lon, lat, polygon[0]):
                    return iso_a3

    return None
