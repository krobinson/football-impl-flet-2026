"""Unit tests for shared.venue_data — venue-to-city lookup."""
from __future__ import annotations

import pytest
from core.venue_data import VENUES, VENUE_CITY, venue_to_city


def test_venues_has_16_entries():
    assert len(VENUES) == 16


def test_venue_city_dict_populated():
    assert len(VENUE_CITY) == 16


def test_exact_match():
    assert venue_to_city("AT&T Stadium") == "Dallas"
    assert venue_to_city("BC Place") == "Vancouver"
    assert venue_to_city("Estadio Azteca") == "Mexico City"


def test_case_insensitive_match():
    assert venue_to_city("at&t stadium") == "Dallas"
    assert venue_to_city("LUMEN FIELD") == "Seattle"


def test_substring_match():
    # API might return shortened name
    assert venue_to_city("MetLife") == "New York / New Jersey"


def test_empty_returns_dash():
    assert venue_to_city("") == "—"


def test_unknown_name_returns_itself():
    result = venue_to_city("Unknown Arena XYZ")
    assert result == "Unknown Arena XYZ"


def test_all_venues_have_city_country_lat_lon():
    for v in VENUES:
        assert "name" in v and v["name"]
        assert "city" in v and v["city"]
        assert "country" in v and v["country"] in ("USA", "CAN", "MEX")
        assert isinstance(v["lat"], float)
        assert isinstance(v["lon"], float)
