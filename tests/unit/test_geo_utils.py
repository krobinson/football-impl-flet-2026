"""Unit tests for geo_utils: project() and hit_test()."""
from __future__ import annotations

import pytest

from core.geo_utils import _LAT_MAX, _LAT_MIN, _canvas_to_geo, hit_test, project


def test_project_origin() -> None:
    """(lon=-180, lat=_LAT_MAX) → (0, 0) top-left corner."""
    x, y = project(-180.0, _LAT_MAX, 800, 400)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)


def test_project_antipodal() -> None:
    """(lon=180, lat=_LAT_MIN) → (width, height) bottom-right corner."""
    x, y = project(180.0, _LAT_MIN, 800, 400)
    assert x == pytest.approx(800.0)
    assert y == pytest.approx(400.0)


def test_project_centre() -> None:
    """Null-island (0, 0) → (width/2, height/2) with full -90/+90 range."""
    x, y = project(0.0, 0.0, 800, 400)
    assert x == pytest.approx(400.0)
    assert y == pytest.approx(200.0)


def test_canvas_to_geo_roundtrip() -> None:
    lon, lat = 10.5, -33.2  # within cropped bounds
    x, y = project(lon, lat, 1000, 500)
    lon2, lat2 = _canvas_to_geo(x, y, 1000, 500)
    assert lon2 == pytest.approx(lon, abs=1e-6)
    assert lat2 == pytest.approx(lat, abs=1e-6)


def _square_feature(lon_min, lat_min, lon_max, lat_max, iso: str) -> dict:
    """Helper: create a simple GeoJSON Polygon feature."""
    ring = [
        [lon_min, lat_max],
        [lon_max, lat_max],
        [lon_max, lat_min],
        [lon_min, lat_min],
        [lon_min, lat_max],
    ]
    return {
        "type": "Feature",
        "properties": {"ISO_A3": iso},
        "geometry": {"type": "Polygon", "coordinates": [ring]},
    }


def test_hit_test_inside() -> None:
    feature = _square_feature(0, 0, 10, 10, "TST")
    x, y = project(5.0, 5.0, 800, 400)
    result = hit_test(x, y, [feature], 800, 400)
    assert result == "TST"


def test_hit_test_outside() -> None:
    feature = _square_feature(0, 0, 10, 10, "TST")
    x, y = project(50.0, 50.0, 800, 400)
    result = hit_test(x, y, [feature], 800, 400)
    assert result is None


def test_hit_test_empty_features() -> None:
    assert hit_test(400.0, 200.0, [], 800, 400) is None
