"""Unit tests for WorldCupDataService."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from features.map.services import WorldCupDataService

# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_geojson(tmp: Path) -> Path:
    gj = {"type": "FeatureCollection", "features": []}
    p = tmp / "countries.geojson"
    p.write_text(json.dumps(gj), encoding="utf-8")
    return p


def _make_worldcup_json(tmp: Path, teams: list[dict]) -> Path:
    data = {"tournament": "FIFA World Cup 2026", "teams": teams}
    p = tmp / "worldcup2026.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _minimal_team(iso: str, group: str) -> dict:
    return {
        "iso_a3": iso,
        "name": f"Country {iso}",
        "group": group,
        "appearances": 1,
        "flag_emoji": "🏳",
    }


def _make_48_teams() -> list[dict]:
    groups = "ABCDEFGHIJKL"
    teams = []
    for i, g in enumerate(groups):
        for j in range(4):
            iso = f"{g}{j:02d}"  # e.g. "A00", "A01"
            teams.append(_minimal_team(iso, g))
    return teams


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_loads_48_teams() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        wc = _make_worldcup_json(tmp, _make_48_teams())
        geo = _make_geojson(tmp)
        svc = WorldCupDataService(worldcup_path=wc, geojson_path=geo)
        assert len(svc.get_all_teams()) == 48


def test_raises_on_wrong_team_count() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        teams = _make_48_teams()[:-1]  # only 47
        wc = _make_worldcup_json(tmp, teams)
        geo = _make_geojson(tmp)
        with pytest.raises(ValueError, match="48"):
            WorldCupDataService(worldcup_path=wc, geojson_path=geo)


def test_raises_on_duplicate_iso() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        teams = _make_48_teams()
        teams[-1]["iso_a3"] = teams[0]["iso_a3"]  # introduce duplicate
        wc = _make_worldcup_json(tmp, teams)
        geo = _make_geojson(tmp)
        with pytest.raises(ValueError, match="Duplicate"):
            WorldCupDataService(worldcup_path=wc, geojson_path=geo)


def test_raises_on_missing_geojson() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        wc = _make_worldcup_json(tmp, _make_48_teams())
        with pytest.raises(FileNotFoundError):
            WorldCupDataService(worldcup_path=wc, geojson_path=tmp / "nope.geojson")


def test_get_team_returns_country() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        wc = _make_worldcup_json(tmp, _make_48_teams())
        geo = _make_geojson(tmp)
        svc = WorldCupDataService(worldcup_path=wc, geojson_path=geo)
        team = svc.get_team("A00")
        assert team is not None
        assert team.iso_a3 == "A00"
        assert team.group == "A"


def test_get_team_returns_none_for_unknown() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        wc = _make_worldcup_json(tmp, _make_48_teams())
        geo = _make_geojson(tmp)
        svc = WorldCupDataService(worldcup_path=wc, geojson_path=geo)
        assert svc.get_team("ZZZ") is None


def test_get_groups_returns_12() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        wc = _make_worldcup_json(tmp, _make_48_teams())
        geo = _make_geojson(tmp)
        svc = WorldCupDataService(worldcup_path=wc, geojson_path=geo)
        assert len(svc.get_groups()) == 12


def test_is_qualifier() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        wc = _make_worldcup_json(tmp, _make_48_teams())
        geo = _make_geojson(tmp)
        svc = WorldCupDataService(worldcup_path=wc, geojson_path=geo)
        assert svc.is_qualifier("A00") is True
        assert svc.is_qualifier("XXX") is False
