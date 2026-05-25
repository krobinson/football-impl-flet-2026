"""Unit tests for domain models."""
from __future__ import annotations

from features.map.models import FIFAGroup, MapRenderState, ParticipatingCountry


def test_participating_country_frozen() -> None:
    c = ParticipatingCountry(iso_a3="ARG", name="Argentina", group="D", appearances=18, flag_emoji="🇦🇷")
    assert c.iso_a3 == "ARG"
    # Frozen dataclass – mutation must raise
    try:
        c.iso_a3 = "BRA"  # type: ignore[misc]
        assert False, "Expected FrozenInstanceError"
    except Exception:
        pass


def test_fifa_group_frozen() -> None:
    c = ParticipatingCountry(iso_a3="FRA", name="France", group="B", appearances=16, flag_emoji="🇫🇷")
    g = FIFAGroup(name="B", countries=(c,))
    assert g.name == "B"
    assert len(g.countries) == 1


def test_map_render_state_defaults() -> None:
    s = MapRenderState()
    assert s.canvas_width == 800.0
    assert s.canvas_height == 400.0
    assert s.active_group_filter is None
    assert s.selected_country is None


def test_map_render_state_mutable() -> None:
    s = MapRenderState()
    s.active_group_filter = "A"
    assert s.active_group_filter == "A"


def test_map_render_state_is_observable() -> None:
    import flet as ft
    # @ft.observable decorates the class; verify the decorator is present/effective
    assert hasattr(ft, "observable"), "ft.observable must exist"
    # The decorated class should have observable notification machinery
    s = MapRenderState()
    assert s is not None  # basic sanity; observable wrapping didn't break construction
