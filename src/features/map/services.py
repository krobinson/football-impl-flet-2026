"""Service for loading World Cup and GeoJSON data from static asset files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from features.map.models import FIFAGroup, GeoFeature, ParticipatingCountry

# Default asset paths (relative to project root when run with uv run flet run).
_ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
_WORLDCUP_JSON = _ASSETS_DIR / "worldcup2026.json"
_COUNTRIES_GEOJSON = _ASSETS_DIR / "countries.geojson"


class WorldCupDataService:
    """Loads and exposes World Cup and geographic boundary data.

    Args:
        worldcup_path: Path to worldcup2026.json (defaults to src/assets/).
        geojson_path: Path to countries.geojson (defaults to src/assets/).

    Raises:
        FileNotFoundError: If either file is missing.
        ValueError: If team count ≠ 48 or duplicate ISO-A3 codes are found.
    """

    def __init__(
        self,
        worldcup_path: Path | None = None,
        geojson_path: Path | None = None,
    ) -> None:
        wc_path = Path(worldcup_path) if worldcup_path else _WORLDCUP_JSON
        geo_path = Path(geojson_path) if geojson_path else _COUNTRIES_GEOJSON

        if not wc_path.exists():
            raise FileNotFoundError(f"World Cup data not found: {wc_path}")
        if not geo_path.exists():
            raise FileNotFoundError(
                f"GeoJSON boundary data not found: {geo_path}. "
                "Run: curl -sL <URL> -o src/assets/countries.geojson"
            )

        raw = json.loads(wc_path.read_text(encoding="utf-8"))
        teams_raw: list[dict] = raw["teams"]

        if len(teams_raw) != 48:
            raise ValueError(f"Expected 48 teams, got {len(teams_raw)}")

        iso_set: set[str] = set()
        self._teams: dict[str, ParticipatingCountry] = {}
        for t in teams_raw:
            iso = t["iso_a3"]
            if iso in iso_set:
                raise ValueError(f"Duplicate ISO-A3 code: {iso}")
            iso_set.add(iso)
            self._teams[iso] = ParticipatingCountry(
                iso_a3=iso,
                name=t["name"],
                group=t["group"],
                appearances=t["appearances"],
                flag_emoji=t["flag_emoji"],
            )

        # GeoJSON ISO_A3 aliases: some Natural Earth codes differ from FIFA codes.
        # Stored separately so get_all_teams() always returns exactly 48 entries.
        _GEO_ALIAS_MAP: dict[str, str] = {
            "DEU": "GER",   # Germany: Natural Earth uses DEU, FIFA uses GER
            "DZA": "ALG",   # Algeria: Natural Earth uses DZA, FIFA uses ALG
            # France: ISO_A3 = -99 in NE → ADM0_A3 = FRA, handled in hit_test
        }
        self._geo_aliases: dict[str, ParticipatingCountry] = {
            geo_iso: self._teams[team_iso]
            for geo_iso, team_iso in _GEO_ALIAS_MAP.items()
            if team_iso in self._teams
        }

        # Build group index
        self._groups: dict[str, FIFAGroup] = {}
        for country in self._teams.values():
            grp = country.group
            existing = self._groups.get(grp)
            if existing is None:
                self._groups[grp] = FIFAGroup(name=grp, countries=(country,))
            else:
                self._groups[grp] = FIFAGroup(
                    name=grp, countries=existing.countries + (country,)
                )

        # Load GeoJSON features
        geojson = json.loads(geo_path.read_text(encoding="utf-8"))
        self._features: list[GeoFeature] = geojson.get("features", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_teams(self) -> list[ParticipatingCountry]:
        """Return all 48 participating countries sorted by ISO-A3."""
        return sorted(self._teams.values(), key=lambda c: c.iso_a3)

    def get_team(self, iso_a3: str) -> ParticipatingCountry | None:
        """Return the country with *iso_a3*, or None if not a qualifier.

        Accepts both FIFA ISO codes (e.g. "GER") and GeoJSON ISO codes (e.g. "DEU").
        """
        return self._teams.get(iso_a3) or self._geo_aliases.get(iso_a3)

    def get_groups(self) -> list[FIFAGroup]:
        """Return all 12 FIFA groups sorted by name (A–L)."""
        return sorted(self._groups.values(), key=lambda g: g.name)

    def get_group(self, name: str) -> FIFAGroup | None:
        """Return the group named *name* (e.g. "A"), or None if unknown."""
        return self._groups.get(name)

    def get_geo_features(self) -> list[GeoFeature]:
        """Return the raw GeoJSON feature list for all world countries."""
        return self._features

    def is_qualifier(self, iso_a3: str) -> bool:
        """Return True if *iso_a3* is one of the 48 World Cup qualifiers."""
        return iso_a3 in self._teams or iso_a3 in self._geo_aliases
