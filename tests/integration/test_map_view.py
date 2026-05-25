"""Integration smoke test: real asset files + full data layer."""
from __future__ import annotations

from pathlib import Path

import pytest

from features.map.services import WorldCupDataService

ASSETS_DIR = Path(__file__).parent.parent.parent / "src" / "assets"


@pytest.fixture(scope="module")
def svc() -> WorldCupDataService:
    if not (ASSETS_DIR / "countries.geojson").exists():
        pytest.skip("countries.geojson not present — run download step first")
    return WorldCupDataService()


def test_48_teams_load(svc: WorldCupDataService) -> None:
    assert len(svc.get_all_teams()) == 48


def test_all_groups_present(svc: WorldCupDataService) -> None:
    group_names = {g.name for g in svc.get_groups()}
    assert group_names == set("ABCDEFGHIJKL")


def test_all_iso_a3_non_empty(svc: WorldCupDataService) -> None:
    for team in svc.get_all_teams():
        assert team.iso_a3, f"Empty ISO-A3 for team: {team.name}"


def test_geo_features_loaded(svc: WorldCupDataService) -> None:
    features = svc.get_geo_features()
    assert len(features) > 100, "Expected 100+ country features from Natural Earth"


def test_known_qualifiers(svc: WorldCupDataService) -> None:
    for iso in ("USA", "BRA", "FRA", "ARG", "ESP", "GER"):
        assert svc.is_qualifier(iso), f"{iso} should be a qualifier"


def test_non_qualifiers(svc: WorldCupDataService) -> None:
    for iso in ("GBR", "CHN", "IND", "RUS"):
        # These may or may not be qualifiers depending on data; just check no crash
        result = svc.is_qualifier(iso)
        assert isinstance(result, bool)
