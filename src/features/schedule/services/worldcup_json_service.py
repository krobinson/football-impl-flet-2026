"""WorldCupJsonService — fetches group stage data from openfootball worldcup.json URL.

Provides match data from the public openfootball worldcup.json URL with local
file fallback. No API key required.
"""
from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from core import config

logger = logging.getLogger(__name__)


class WorldCupDataError(RuntimeError):
    """Raised when both URL fetch and local file fallback fail."""

    def __init__(
        self,
        message: str,
        url_error: Exception | None = None,
        file_error: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.url_error = url_error
        self.file_error = file_error


def _parse_utc_offset(time_str: str) -> timedelta:
    """Parse UTC offset from time string like '13:00 UTC-6' or '20:00 UTC+2'."""
    match = re.search(r"UTC([+-])(\d+)", time_str)
    if match:
        sign = 1 if match.group(1) == "+" else -1
        hours = int(match.group(2))
        return timedelta(hours=sign * hours)
    return timedelta(0)


def _extract_matchday(round_str: str) -> int:
    """Extract matchday number from round string like 'Matchday 1' or 'Matchday 14'."""
    match = re.search(r"Matchday\s+(\d+)", round_str)
    if match:
        return int(match.group(1))
    return 99


def is_group_stage(match: dict) -> bool:
    """Return True if the match belongs to a group stage (Group A through Group L)."""
    group = match.get("group", "")
    # "Group A" is 7 chars, "Group L" is 7 chars
    return group.startswith("Group ") and len(group) == 7 and group[-1].isalpha()


def classify_stage(match: dict) -> str:
    """Classify a match into a tournament stage category.

    Returns one of: GROUP_STAGE, ROUND_OF_32, ROUND_OF_16, QUARTER_FINAL,
    SEMI_FINAL, FINAL, or UNKNOWN.
    """
    group = match.get("group", "")
    if group.startswith("Group "):
        return "GROUP_STAGE"
    round_name = match.get("round", "")
    stage_map = {
        "Round of 32": "ROUND_OF_32",
        "Round of 16": "ROUND_OF_16",
        "Quarter-final": "QUARTER_FINAL",
        "Semi-final": "SEMI_FINAL",
        "Final": "FINAL",
        "Match for third place": "FINAL",
    }
    return stage_map.get(round_name, "UNKNOWN")


def round_display_label(match: dict) -> str:
    """Return a short display label for knockout rounds.

    Returns empty string for group stage matches.
    """
    group = match.get("group", "")
    if group.startswith("Group "):
        return ""
    round_name = match.get("round", "")
    label_map = {
        "Round of 32": "R32",
        "Round of 16": "R16",
        "Quarter-final": "QF",
        "Semi-final": "SF",
        "Final": "F",
        "Match for third place": "3rd",
    }
    return label_map.get(round_name, "")


def transform_match(raw: dict) -> dict:
    """Convert a URL-format match dict to the normalized shape expected by match_row().

    Input: Raw dict from worldcup.json with fields: round, date, time, team1, team2, group, ground, score.
    Output: Normalized dict with fields: utcDate, status, matchday, group, venue, homeTeam, awayTeam, score.
    """
    date_str = raw.get("date", "")
    time_str = raw.get("time", "")
    round_str = raw.get("round", "")
    group_str = raw.get("group", "")
    ground = raw.get("ground", "")
    raw_score = raw.get("score")

    # Parse date and time, convert to UTC ISO-8601
    utc_date = ""
    if date_str and time_str:
        try:
            # Parse the time portion (HH:MM)
            time_part = time_str.split()[0]  # "13:00" from "13:00 UTC-6"
            offset = _parse_utc_offset(time_str)
            # Create a datetime with the offset, then convert to UTC
            local_dt = datetime.strptime(f"{date_str} {time_part}", "%Y-%m-%d %H:%M")
            # Subtract the offset to get UTC
            utc_dt = local_dt - offset
            utc_date = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse date/time: {date_str} {time_str}: {e}")
            utc_date = f"{date_str}T00:00:00Z"

    # Convert group format: "Group A" -> "GROUP_A"
    normalized_group = ""
    if group_str.startswith("Group "):
        letter = group_str[-1].upper()
        normalized_group = f"GROUP_{letter}"

    # Transform score: URL format is {'ft': [home, away], 'ht': [...]}
    # API format is {'fullTime': {'home': X, 'away': Y}}
    transformed_score = None
    if raw_score and isinstance(raw_score, dict):
        ft_score = raw_score.get("ft")
        if ft_score and isinstance(ft_score, list) and len(ft_score) == 2:
            transformed_score = {
                "fullTime": {
                    "home": ft_score[0],
                    "away": ft_score[1],
                }
            }

    # Determine status based on whether score exists
    status = "FINISHED" if transformed_score else "SCHEDULED"

    return {
        "utcDate": utc_date,
        "status": status,
        "matchday": _extract_matchday(round_str),
        "group": normalized_group,
        "venue": ground if ground else "TBD",
        "homeTeam": {
            "name": raw.get("team1", "TBD"),
            "tla": None,
        },
        "awayTeam": {
            "name": raw.get("team2", "TBD"),
            "tla": None,
        },
        "score": transformed_score,
        "stage": classify_stage(raw),
        "round_display": round_display_label(raw),
    }


class WorldCupJsonService:
    """Service for fetching World Cup 2026 group stage data from openfootball URL.

    Fetches from URL first, falls back to local file if URL fails.
    """

    def __init__(
        self,
        url: str | None = None,
        local_path: str | Path | None = None,
    ) -> None:
        self._url = url or config.WORLDCUP_JSON_URL
        self._local_path = Path(local_path) if local_path else Path(config.__file__).parents[2] / "data" / "worldcup" / "2026" / "worldcup.json"
        self._data_source = "error"

    def get_group_matches(self) -> list[dict]:
        """Fetch all group stage matches, transform them, and return sorted by date then time.

        Returns:
            list[dict]: 48 match dicts (6 per group × 12 groups).

        Raises:
            WorldCupDataError: If both URL fetch and local file fallback fail.
        """
        raw_matches = None

        # Try URL first
        try:
            raw_matches = self._fetch_from_url()
            self._data_source = "url"
            logger.info(f"Loaded {len(raw_matches)} matches from URL")
        except Exception as e:
            logger.warning(f"URL fetch failed: {e}. Falling back to local file.")
            url_error = e

            # Fall back to local file
            try:
                raw_matches = self._load_from_file()
                self._data_source = "local"
                logger.info(f"Loaded {len(raw_matches)} matches from local file")
            except Exception as file_e:
                logger.error(f"Local file load also failed: {file_e}")
                raise WorldCupDataError(
                    "Failed to load World Cup data from both URL and local file",
                    url_error=url_error,
                    file_error=file_e,
                ) from file_e

        # Filter to group stage only
        group_matches = [m for m in raw_matches if is_group_stage(m)]

        # Transform to normalized format
        transformed = [transform_match(m) for m in group_matches]

        # Sort by date then time
        transformed.sort(key=lambda m: (m.get("utcDate", ""), m.get("matchday", 99)))

        return transformed

    def get_all_matches(self) -> list[dict]:
        """Fetch all tournament matches (group + knockout), transform them, and return sorted.

        Returns:
            list[dict]: 104 match dicts (72 group stage + 32 knockout).

        Raises:
            WorldCupDataError: If both URL fetch and local file fallback fail.
        """
        raw_matches = None

        # Try URL first
        try:
            raw_matches = self._fetch_from_url()
            self._data_source = "url"
            logger.info(f"Loaded {len(raw_matches)} matches from URL")
        except Exception as e:
            logger.warning(f"URL fetch failed: {e}. Falling back to local file.")
            url_error = e

            # Fall back to local file
            try:
                raw_matches = self._load_from_file()
                self._data_source = "local"
                logger.info(f"Loaded {len(raw_matches)} matches from local file")
            except Exception as file_e:
                logger.error(f"Local file load also failed: {file_e}")
                raise WorldCupDataError(
                    "Failed to load World Cup data from both URL and local file",
                    url_error=url_error,
                    file_error=file_e,
                ) from file_e

        # Transform all matches (no group filter)
        transformed = [transform_match(m) for m in raw_matches]

        # Sort by date then time
        transformed.sort(key=lambda m: (m.get("utcDate", ""), m.get("matchday", 99)))

        return transformed

    def get_data_source(self) -> str:
        """Return the origin of the most recently loaded data.

        Returns:
            str: "url", "local", or "error"
        """
        return self._data_source

    def _fetch_from_url(self) -> list[dict]:
        """Fetch match data from the remote URL."""
        req = urllib.request.Request(
            self._url,
            headers={"Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("matches", [])
        except urllib.error.URLError as e:
            raise RuntimeError(f"URL fetch failed: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from URL: {e}") from e

    def _load_from_file(self) -> list[dict]:
        """Load match data from the local fallback file."""
        if not self._local_path.exists():
            raise FileNotFoundError(f"Local file not found: {self._local_path}")

        try:
            with open(self._local_path, encoding="utf-8") as f:
                data = json.load(f)
                return data.get("matches", [])
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in local file: {e}") from e
