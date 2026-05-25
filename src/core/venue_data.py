"""Shared venue data for FIFA World Cup 2026 host stadiums.

Used by both the OSM venue map and the pool schedule view.
"""
from __future__ import annotations

VENUES: list[dict] = [
    # United States
    {"name": "MetLife Stadium",         "city": "New York / New Jersey", "country": "USA", "lat": 40.8135,  "lon": -74.0745},
    {"name": "SoFi Stadium",            "city": "Los Angeles",           "country": "USA", "lat": 33.9535,  "lon": -118.3392},
    {"name": "AT&T Stadium",            "city": "Dallas",                "country": "USA", "lat": 32.7480,  "lon": -97.0931},
    {"name": "Levi's Stadium",          "city": "San Francisco Bay Area","country": "USA", "lat": 37.4033,  "lon": -121.9694},
    {"name": "Hard Rock Stadium",       "city": "Miami",                 "country": "USA", "lat": 25.9580,  "lon": -80.2389},
    {"name": "Mercedes-Benz Stadium",   "city": "Atlanta",               "country": "USA", "lat": 33.7554,  "lon": -84.4008},
    {"name": "Lumen Field",             "city": "Seattle",               "country": "USA", "lat": 47.5952,  "lon": -122.3316},
    {"name": "Arrowhead Stadium",       "city": "Kansas City",           "country": "USA", "lat": 39.0489,  "lon": -94.4839},
    {"name": "Gillette Stadium",        "city": "Boston",                "country": "USA", "lat": 42.0909,  "lon": -71.2643},
    {"name": "Lincoln Financial Field", "city": "Philadelphia",          "country": "USA", "lat": 39.9008,  "lon": -75.1675},
    # Canada
    {"name": "BC Place",                "city": "Vancouver",             "country": "CAN", "lat": 49.2767,  "lon": -123.1117},
    {"name": "BMO Field",               "city": "Toronto",               "country": "CAN", "lat": 43.6333,  "lon": -79.4186},
    # Mexico
    {"name": "Estadio Azteca",          "city": "Mexico City",           "country": "MEX", "lat": 19.3029,  "lon": -99.1505},
    {"name": "Estadio Akron",           "city": "Guadalajara",           "country": "MEX", "lat": 20.6819,  "lon": -103.4702},
    {"name": "Estadio BBVA",            "city": "Monterrey",             "country": "MEX", "lat": 25.6694,  "lon": -100.2438},
    {"name": "Estadio Cuauhtémoc",      "city": "Puebla",                "country": "MEX", "lat": 18.9934,  "lon": -98.2420},
]

# Exact name → city for O(1) lookups
VENUE_CITY: dict[str, str] = {v["name"]: v["city"] for v in VENUES}

# Lower-cased name → city for fuzzy / API-name lookups
_VENUE_CITY_LOWER: dict[str, str] = {k.lower(): v for k, v in VENUE_CITY.items()}


def venue_to_city(api_venue_name: str) -> str:
    """Return the host city for a stadium name.

    First tries an exact match, then a case-insensitive substring scan so that
    minor differences between the API's venue string and our local names still
    resolve correctly.  Returns the original name if no match is found.
    """
    if not api_venue_name:
        return "—"
    # Exact match
    if api_venue_name in VENUE_CITY:
        return VENUE_CITY[api_venue_name]
    # Case-insensitive exact
    lower = api_venue_name.lower()
    if lower in _VENUE_CITY_LOWER:
        return _VENUE_CITY_LOWER[lower]
    # Substring: API name contains our name keyword or vice-versa
    for key, city in _VENUE_CITY_LOWER.items():
        if key in lower or lower in key:
            return city
    return api_venue_name  # fall back to raw stadium name
