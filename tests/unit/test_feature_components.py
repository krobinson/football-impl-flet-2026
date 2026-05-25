"""Smoke tests: verify all per-feature component packages are importable."""
from __future__ import annotations


def test_schedule_components_importable():
    from features.schedule.components import match_row, header_row  # noqa: F401
    assert callable(match_row)
    assert callable(header_row)


def test_teams_components_importable():
    from features.teams.components import team_stats_row  # noqa: F401
    assert callable(team_stats_row)


def test_venues_components_importable():
    from features.venues.components import venue_marker  # noqa: F401
    assert callable(venue_marker)


def test_matches_components_importable():
    from features.matches.components import match_detail_controls  # noqa: F401
    assert callable(match_detail_controls)


def test_records_components_importable():
    from features.records.components import ModeToggle  # noqa: F401
    assert callable(ModeToggle)


def test_map_components_importable():
    from features.map.components import GroupFilter, InfoPanel, MapView  # noqa: F401
    assert callable(GroupFilter)
    assert callable(InfoPanel)
    assert callable(MapView)
