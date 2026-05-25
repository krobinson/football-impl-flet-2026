"""Smoke tests for src/core/components/."""
from __future__ import annotations

import flet as ft
from core.ui_helpers import BG_CARD
from core.components import (
    page_header, styled_dropdown, scrollable_table_card, loading_row, LoadingRow,
)


def test_page_header_returns_column():
    result = page_header("Title", "Subtitle")
    assert isinstance(result, ft.Column)
    assert isinstance(result.controls[0], ft.Text)
    assert result.controls[0].value == "Title"


def test_page_header_no_divider():
    result = page_header("Title", "Sub", divider=False)
    assert not any(isinstance(c, ft.Divider) for c in result.controls)


def test_page_header_with_divider():
    result = page_header("Title", "Sub", divider=True)
    assert any(isinstance(c, ft.Divider) for c in result.controls)


def test_styled_dropdown_returns_dropdown():
    opts = [ft.dropdown.Option("All"), ft.dropdown.Option("A")]
    dd = styled_dropdown("Group", opts, value="All", width=160)
    assert isinstance(dd, ft.Dropdown)
    assert dd.bgcolor == BG_CARD
    assert dd.width == 160
    assert dd.value == "All"


def test_scrollable_table_card_returns_container():
    inner = ft.Text("hello")
    result = scrollable_table_card(inner, height=300)
    assert isinstance(result, ft.Container)
    assert result.height == 300
    assert isinstance(result.content, ft.Column)


def test_loading_row_fields():
    lr = loading_row()
    assert isinstance(lr, LoadingRow)
    assert lr.ring.visible is False
    assert lr.notice.visible is False
    assert isinstance(lr.row, ft.Row)


def test_loading_row_prefix_controls():
    dd = ft.Dropdown(label="X", options=[])
    lr = loading_row(prefix_controls=[dd])
    assert dd in lr.row.controls
    assert lr.ring in lr.row.controls
