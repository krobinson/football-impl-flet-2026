"""Match Explorer view – browse and filter World Cup matches by year/stage/group."""
from __future__ import annotations

import threading
import flet as ft
from features.matches.services import DataStore
from core.network import ApiKeyMissingError, ApiError, FootballDataClient
from core.ui_helpers import (
    ACCENT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR,
    build_data_table, card, section_title, value_text,
)
from features.matches.components import match_detail_controls
from core.components import page_header, styled_dropdown, scrollable_table_card, loading_row

_LIVE_YEAR = 2026  # year served by the live API


def build_matches_view(
    store: DataStore,
    football_data_client: FootballDataClient | None = None,
) -> ft.Column:
    """Build the Match Explorer tab content."""
    years = list(store.all_years)
    if _LIVE_YEAR not in years:
        years = sorted(set(years) | {_LIVE_YEAR})
    default_year = _LIVE_YEAR if _LIVE_YEAR in years else (years[-1] if years else 2022)

    # ── Filters + loading row ─────────────────────────────────────────────────
    year_dd = styled_dropdown(
        "Tournament Year",
        [ft.dropdown.Option(str(y)) for y in years],
        value=str(default_year),
        width=180,
    )
    stage_dd = styled_dropdown(
        "Stage / Round",
        [ft.dropdown.Option("All")],
        value="All",
        width=240,
    )
    group_dd = styled_dropdown(
        "Group",
        [ft.dropdown.Option("All")],
        value="All",
        width=180,
    )
    lr = loading_row([year_dd, stage_dd, group_dd])

    # ── Match table area ──────────────────────────────────────────────────
    table_container = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
    detail_container = ft.Column([], spacing=6)

    # Current filtered matches (stored to support row selection)
    _state: dict = {"matches": [], "year": default_year}

    def _stages_for_year(year: int) -> list[str]:
        df = store.matches
        rows = df[df["year"] == year]
        return sorted(rows["stage"].dropna().unique().tolist())

    def _groups_for_year(year: int) -> list[str]:
        df = store.matches
        rows = df[(df["year"] == year) & df["group"].notna()]
        groups = sorted(rows["group"].unique().tolist())
        return [g for g in groups if g]

    def _filtered_matches(year: int, stage: str, group: str):
        df = store.matches.copy()
        df = df[df["year"] == year]
        if stage and stage != "All":
            df = df[df["stage"] == stage]
        if group and group != "All":
            df = df[df["group"] == group]
        return df

    def _render_api_matches(matches: list[dict]) -> None:
        """Render a list of matches from the football-data.org API response."""
        _state["matches"] = []  # no detail drill-down for live matches (no event data)
        tbl_cols = ["Date (UTC)", "Group", "Home", "Score", "Away", "Status"]
        tbl_rows = []
        for m in matches:
            utc = m.get("utcDate", "")[:16].replace("T", " ")
            group_label = (m.get("group") or "").replace("GROUP_", "Grp ")
            home = (m.get("homeTeam") or {}).get("name", "TBD")
            away = (m.get("awayTeam") or {}).get("name", "TBD")
            ft_score = (m.get("score") or {}).get("fullTime") or {}
            h, a = ft_score.get("home"), ft_score.get("away")
            score = f"{h}–{a}" if h is not None and a is not None else "vs"
            status = m.get("status", "")
            tbl_rows.append([utc, group_label, home, score, away, status])

        table = build_data_table(tbl_cols, tbl_rows, on_select=None)
        table_container.controls = [table]
        detail_container.controls.clear()
        try:
            table_container.update()
            detail_container.update()
        except Exception:
            pass

    def _fetch_live_matches(group: str | None) -> None:
        """Fetch 2026 group-stage matches from the API in a background thread."""
        def _run() -> None:
            lr.ring.visible = True
            lr.notice.value = ""
            lr.notice.visible = False
            try:
                lr.ring.update()
            except Exception:
                pass

            try:
                api_group = None
                if group:
                    api_group = group if group.startswith("GROUP_") else f"GROUP_{group}"
                matches = football_data_client.get_group_matches(group=api_group, season=_LIVE_YEAR)
                _render_api_matches(matches)
                lr.notice.value = f"✅ Loaded {len(matches)} group-stage matches from football-data.org"
                lr.notice.visible = True
            except ApiKeyMissingError as exc:
                lr.notice.value = f"⚠️ API key not configured — showing cached data. ({exc})"
                lr.notice.visible = True
                # Fall back to DataStore historical data for 2026 if any
                _render_table_from_store(_LIVE_YEAR, "All", "All")
            except (ApiError, OSError) as exc:
                lr.notice.value = f"⚠️ API error — {exc}. Showing cached/static data."
                lr.notice.visible = True
                _render_table_from_store(_LIVE_YEAR, "All", "All")
            finally:
                lr.ring.visible = False
                try:
                    lr.ring.update()
                    lr.notice.update()
                except Exception:
                    pass

        threading.Thread(target=_run, daemon=True).start()

    def _render_table_from_store(year: int, stage: str, group: str) -> None:
        """Render matches from the local DataStore (historical / fallback)."""
        df = _filtered_matches(year, stage, group)
        _state["matches"] = df.to_dict("records")

        tbl_cols = ["Date", "Stage", "Home", "Score", "Away", "Venue"]
        tbl_rows = []
        for _, m in df.iterrows():
            score = f"{int(m['home_score'])}–{int(m['away_score'])}"
            if m.get("aet"):
                score += " AET"
            pen_home = m.get("pen_home")
            pen_away = m.get("pen_away")
            if pen_home is not None and pen_away is not None:
                try:
                    score += f" (p: {int(float(pen_home))}–{int(float(pen_away))})"
                except (ValueError, TypeError):
                    pass
            tbl_rows.append([
                str(m["date"]),
                str(m["stage"]),
                str(m["home_team"]),
                score,
                str(m["away_team"]),
                str(m["venue"])[:40],
            ])

        table = build_data_table(tbl_cols, tbl_rows, on_select=_on_match_select)
        table_container.controls = [table]
        detail_container.controls.clear()
        try:
            table_container.update()
            detail_container.update()
        except Exception:
            pass

    def _on_match_select(idx: int) -> None:
        matches = _state["matches"]
        if idx >= len(matches):
            return
        m = matches[idx]
        year = m["year"]
        mid = m["match_id"]

        events = store.match_events[store.match_events["match_id"] == mid]

        detail_container.controls.clear()
        detail_container.controls += match_detail_controls(m, events)
        try:
            detail_container.update()
        except Exception:
            pass

    def _update_stage_group_options(year: int) -> None:
        stages = _stages_for_year(year)
        stage_dd.options = [ft.dropdown.Option("All")] + [ft.dropdown.Option(s) for s in stages]
        stage_dd.value = "All"

        groups = _groups_for_year(year)
        group_dd.options = [ft.dropdown.Option("All")] + [ft.dropdown.Option(g) for g in groups]
        group_dd.value = "All"
        try:
            stage_dd.update()
            group_dd.update()
        except Exception:
            pass

    def _render_table(year: int, stage: str, group: str) -> None:
        """Dispatch to live API fetch or local DataStore based on year."""
        if year == _LIVE_YEAR and football_data_client is not None:
            _fetch_live_matches(group if group != "All" else None)
        else:
            _render_table_from_store(year, stage, group)

    def _on_year_change(_: ft.ControlEvent) -> None:
        year = int(year_dd.value)
        _state["year"] = year
        _update_stage_group_options(year)
        _render_table(year, "All", "All")

    def _on_filter_change(_: ft.ControlEvent) -> None:
        _render_table(
            _state["year"],
            stage_dd.value or "All",
            group_dd.value or "All",
        )

    year_dd.on_change = _on_year_change
    stage_dd.on_change = _on_filter_change
    group_dd.on_change = _on_filter_change

    # Initial population
    _update_stage_group_options(default_year)
    _render_table(default_year, "All", "All")

    return ft.Column(
        [
            page_header("🔍 Match Explorer", "Browse every World Cup match — click a row for goalscorer details"),
            lr.row,
            lr.notice,
            scrollable_table_card(table_container, height=380),
            card(detail_container, padding=14),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
