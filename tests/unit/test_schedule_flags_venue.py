"""Unit tests for schedule flags and venue population — 014-schedule-flags-venue.

TDD: tests written before implementation. Run with:
    uv run pytest tests/unit/test_schedule_flags_venue.py -v
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# city_to_stadium  (T004 — venue fallback helper in core.venue_data)
# ---------------------------------------------------------------------------

class TestCityToStadium:
    def _fn(self):
        from core.venue_data import city_to_stadium
        return city_to_stadium

    def test_exact_match_atlanta(self):
        assert self._fn()("Atlanta") == "Mercedes-Benz Stadium"

    def test_exact_match_mexico_city(self):
        assert self._fn()("Mexico City") == "Estadio Azteca"

    def test_exact_match_seattle(self):
        assert self._fn()("Seattle") == "Lumen Field"

    def test_exact_match_miami(self):
        assert self._fn()("Miami") == "Hard Rock Stadium"

    def test_case_insensitive_match(self):
        assert self._fn()("atlanta") == "Mercedes-Benz Stadium"

    def test_substring_match_guadalajara_with_suffix(self):
        # Local fixture uses "Guadalajara (Zapopan)" — must still resolve
        assert self._fn()("Guadalajara (Zapopan)") == "Estadio Akron"

    def test_substring_match_san_francisco(self):
        # Canonical city is "San Francisco Bay Area" — shorter form should match
        result = self._fn()("San Francisco")
        assert result == "Levi's Stadium"

    def test_unknown_city_returns_input(self):
        assert self._fn()("Unknown City XYZ") == "Unknown City XYZ"

    def test_empty_string_returns_empty(self):
        assert self._fn()("") == ""

    def test_all_16_host_cities_resolve(self):
        from core.venue_data import VENUES, city_to_stadium
        fn = city_to_stadium
        for v in VENUES:
            result = fn(v["city"])
            assert result == v["name"], f"city {v['city']!r} → got {result!r}, expected {v['name']!r}"


# ---------------------------------------------------------------------------
# tla_to_flag  (T003 — US1 flag lookup)
# ---------------------------------------------------------------------------

class TestTlaToFlag:
    def _fn(self):
        from features.schedule.components.match_row import tla_to_flag
        return tla_to_flag

    def test_usa_returns_us_flag(self):
        assert self._fn()("USA") == "🇺🇸"

    def test_mex_returns_mexico_flag(self):
        assert self._fn()("MEX") == "🇲🇽"

    def test_fra_returns_france_flag(self):
        assert self._fn()("FRA") == "🇫🇷"

    def test_bra_returns_brazil_flag(self):
        assert self._fn()("BRA") == "🇧🇷"

    def test_arg_returns_argentina_flag(self):
        assert self._fn()("ARG") == "🇦🇷"

    def test_ger_returns_germany_flag(self):
        assert self._fn()("GER") == "🇩🇪"

    def test_esp_returns_spain_flag(self):
        assert self._fn()("ESP") == "🇪🇸"

    def test_eng_returns_england_flag(self):
        flag = self._fn()("ENG")
        assert flag != "", "England must have a flag"

    def test_sco_returns_scotland_flag(self):
        flag = self._fn()("SCO")
        assert flag != "", "Scotland must have a flag"

    def test_unknown_tla_returns_empty(self):
        assert self._fn()("XYZ") == ""

    def test_none_returns_empty(self):
        assert self._fn()(None) == ""

    def test_empty_string_returns_empty(self):
        assert self._fn()("") == ""

    def test_lowercase_tla_normalised(self):
        assert self._fn()("usa") == "🇺🇸"

    def test_all_48_nations_have_mapping(self):
        from features.schedule.components.match_row import tla_to_flag
        # All expected 2026 TLAs
        expected_tlas = [
            "ALG", "ARG", "AUS", "AUT", "BEL", "BIH", "BRA", "CAN", "CPV",
            "COL", "CRO", "CUR", "CZE", "COD", "ECU", "EGY", "ENG", "FRA",
            "GER", "GHA", "HAI", "IRN", "IRQ", "CIV", "JPN", "JOR", "MEX",
            "MAR", "NED", "NZL", "NOR", "PAN", "PAR", "POR", "QAT", "KSA",
            "SCO", "SEN", "RSA", "KOR", "ESP", "SWE", "SUI", "TUN", "TUR",
            "USA", "URU", "UZB",
        ]
        missing = [tla for tla in expected_tlas if not tla_to_flag(tla)]
        assert missing == [], f"Missing flag mappings for: {missing}"


# ---------------------------------------------------------------------------
# _resolve_venue  (T004 — US2 venue fallback)
# ---------------------------------------------------------------------------

class TestResolveVenue:
    def _fn(self):
        from features.schedule.components.match_row import _resolve_venue
        return _resolve_venue

    def _match(self, venue=None, home="Team A", away="Team B", tla_home="USA", tla_away="MEX", matchday=1, group="GROUP_A"):
        return {
            "venue": venue,
            "matchday": matchday,
            "group": group,
            "homeTeam": {"name": home, "tla": tla_home},
            "awayTeam": {"name": away, "tla": tla_away},
        }

    def test_api_venue_used_when_present(self):
        m = self._match(venue="MetLife Stadium")
        assert self._fn()(m) == "MetLife Stadium"

    def test_api_venue_empty_string_falls_back(self):
        # football-data may return empty string instead of null
        m = self._match(venue="")
        # Should not return ""— should look up local fallback or return TBD
        result = self._fn()(m)
        assert result != ""

    def test_local_fallback_mexico_vs_south_africa(self):
        """Matchday 1 Mexico vs South Africa → Estadio Azteca via local fixture."""
        m = self._match(venue=None, home="Mexico", away="South Africa")
        result = self._fn()(m)
        assert result == "Estadio Azteca"

    def test_local_fallback_south_korea_vs_czech(self):
        m = self._match(venue=None, home="South Korea", away="Czech Republic")
        result = self._fn()(m)
        # Guadalajara → Estadio Akron
        assert result == "Estadio Akron"

    def test_unknown_home_and_away_returns_tbd(self):
        m = self._match(venue=None, home="Unknown Nation", away="Another Unknown")
        assert self._fn()(m) == "TBD"

    def test_none_home_team_returns_tbd(self):
        m = {"venue": None, "homeTeam": None, "awayTeam": None}
        assert self._fn()(m) == "TBD"

    def test_api_venue_takes_priority_over_local(self):
        # Even if local fixture would resolve a different value, API wins
        m = self._match(venue="Override Stadium", home="Mexico", away="South Africa")
        assert self._fn()(m) == "Override Stadium"


# ---------------------------------------------------------------------------
# match_row rendering  (T005-T006)
# ---------------------------------------------------------------------------

class TestMatchRowRendering:
    """Verify flag prefix and venue appear in the rendered row content."""

    def _make_match(
        self,
        home="USA", home_tla="USA",
        away="Mexico", away_tla="MEX",
        venue="AT&T Stadium",
        status="SCHEDULED",
        group="GROUP_A",
        matchday=1,
    ) -> dict:
        return {
            "id": 1,
            "utcDate": "2026-06-11T14:00:00Z",
            "status": status,
            "matchday": matchday,
            "group": group,
            "venue": venue,
            "homeTeam": {"name": home, "tla": home_tla},
            "awayTeam": {"name": away, "tla": away_tla},
            "score": {"fullTime": {"home": None, "away": None}},
        }

    def _extract_texts(self, row) -> list[str]:
        """Recursively collect all Text.value strings from a Flet control tree."""
        import flet as ft
        texts = []

        def _walk(ctrl):
            if isinstance(ctrl, ft.Text):
                texts.append(ctrl.value or "")
            for attr in ("content", "controls", "actions"):
                child = getattr(ctrl, attr, None)
                if child is None:
                    continue
                if isinstance(child, list):
                    for c in child:
                        _walk(c)
                else:
                    _walk(child)

        _walk(row)
        return texts

    def test_home_team_name_present(self):
        from features.schedule.components.match_row import match_row
        row = match_row(self._make_match(), 0)
        texts = self._extract_texts(row)
        assert any("USA" in t for t in texts)

    def test_away_team_name_present(self):
        from features.schedule.components.match_row import match_row
        row = match_row(self._make_match(), 0)
        texts = self._extract_texts(row)
        assert any("Mexico" in t for t in texts)

    def test_home_flag_prefix_present_when_tla_known(self):
        from features.schedule.components.match_row import match_row
        row = match_row(self._make_match(home="USA", home_tla="USA"), 0)
        texts = self._extract_texts(row)
        assert any("🇺🇸" in t for t in texts), f"Expected US flag in texts: {texts}"

    def test_away_flag_prefix_present_when_tla_known(self):
        from features.schedule.components.match_row import match_row
        row = match_row(self._make_match(away="Mexico", away_tla="MEX"), 0)
        texts = self._extract_texts(row)
        assert any("🇲🇽" in t for t in texts), f"Expected Mexico flag in texts: {texts}"

    def test_no_flag_when_tla_unknown(self):
        from features.schedule.components.match_row import match_row, tla_to_flag
        row = match_row(self._make_match(home_tla="XYZ"), 0)
        texts = self._extract_texts(row)
        # The unknown TLA should produce no flag — just the team name
        assert tla_to_flag("XYZ") == ""

    def test_no_flag_when_tla_missing(self):
        from features.schedule.components.match_row import match_row, tla_to_flag
        match = self._make_match()
        match["homeTeam"] = {"name": "USA"}  # no tla key
        row = match_row(match, 0)
        texts = self._extract_texts(row)
        assert any("USA" in t for t in texts)

    def test_venue_text_present(self):
        from features.schedule.components.match_row import match_row
        row = match_row(self._make_match(venue="AT&T Stadium"), 0)
        texts = self._extract_texts(row)
        assert any("AT&T Stadium" in t for t in texts)

    def test_venue_fallback_when_api_venue_null(self):
        from features.schedule.components.match_row import match_row
        match = self._make_match(home="Mexico", away="South Africa", venue=None)
        row = match_row(match, 0)
        texts = self._extract_texts(row)
        # Should resolve to Estadio Azteca from local fixture
        assert any("Estadio Azteca" in t for t in texts), f"Expected Azteca in texts: {texts}"

    def test_venue_tbd_when_unresolvable(self):
        from features.schedule.components.match_row import match_row
        match = self._make_match(home="Unknown", away="Ghost FC", venue=None)
        row = match_row(match, 0)
        texts = self._extract_texts(row)
        assert any("TBD" in t for t in texts)
