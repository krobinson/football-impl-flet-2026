"""football_data_client.py — Throttled HTTP client for football-data.org v4 API.

Throttling policy (free plan): 10 requests per minute.
This client enforces a minimum inter-request gap (default 6 s for the free
tier) and backs off 60 s on HTTP 429.  Successful responses are cached in
memory for CACHE_TTL_S seconds so the UI can call `get_group_matches()`
freely without triggering extra network calls.

Usage::

    from services.football_data_client import FootballDataClient, ApiKeyMissingError

    client = FootballDataClient()          # reads FOOTBALL_DATA_API_KEY env var
    try:
        matches = client.get_group_matches()
    except ApiKeyMissingError:
        # handle missing key — show fallback data
        ...
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from core import config

logger = logging.getLogger(__name__)

# ── Exceptions ────────────────────────────────────────────────────────────────

class ApiKeyMissingError(RuntimeError):
    """Raised when no API key is available."""


class ApiError(RuntimeError):
    """Raised on non-retryable HTTP errors (4xx except 429, 5xx)."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


# ── Client ────────────────────────────────────────────────────────────────────

class FootballDataClient:
    """Throttled, caching client for the football-data.org v4 API.

    Parameters
    ----------
    api_key:
        Personal API token.  Defaults to ``config.FOOTBALL_DATA_API_KEY``
        (i.e. the ``FOOTBALL_DATA_API_KEY`` environment variable).
    throttle_interval_s:
        Minimum seconds between consecutive HTTP requests.
        Defaults to ``config.FOOTBALL_DATA_THROTTLE_INTERVAL_S``.
    cache_ttl_s:
        Seconds to keep a cached response before re-fetching.
        Defaults to ``config.FOOTBALL_DATA_CACHE_TTL_S``.
    competition_code:
        API code for the World Cup competition.
        Defaults to ``config.FOOTBALL_DATA_WC_CODE`` (``"WC"``).
    """

    BASE_URL = "https://api.football-data.org/v4"

    # Sentinel so __init__ can distinguish "caller passed None explicitly"
    # (meaning: no key) from "caller omitted the argument" (meaning: use env).
    _UNSET: object = object()

    def __init__(
        self,
        api_key: str | None = _UNSET,  # type: ignore[assignment]
        throttle_interval_s: float | None = None,
        cache_ttl_s: int | None = None,
        competition_code: str | None = None,
    ) -> None:
        # If the caller omitted api_key, fall back to the env-var config.
        # If the caller explicitly passed None (e.g. in tests), honour that.
        if api_key is FootballDataClient._UNSET:
            self._api_key = config.FOOTBALL_DATA_API_KEY
        else:
            self._api_key = api_key
        self._throttle_interval = (
            throttle_interval_s
            if throttle_interval_s is not None
            else config.FOOTBALL_DATA_THROTTLE_INTERVAL_S
        )
        self._cache_ttl = (
            cache_ttl_s
            if cache_ttl_s is not None
            else config.FOOTBALL_DATA_CACHE_TTL_S
        )
        self._competition_code = competition_code or config.FOOTBALL_DATA_WC_CODE

        # Throttle state
        self._last_request_time: float = 0.0

        # In-memory cache: cache_key → (fetched_at, data)
        self._cache: dict[str, tuple[float, Any]] = {}

    # ── Public API ────────────────────────────────────────────────────────

    def get_group_matches(
        self,
        group: str | None = None,
        season: int = 2026,
    ) -> list[dict]:
        """Return group-stage matches for the World Cup.

        Parameters
        ----------
        group:
            Optional group filter, e.g. ``"GROUP_A"``.  When supplied the
            result is filtered client-side from the cached full fetch, so
            no extra network request is issued.
        season:
            Four-digit year (default ``2026``).

        Returns
        -------
        list[dict]
            Each dict is a match item from the football-data.org response.

        Raises
        ------
        ApiKeyMissingError
            If no API key is configured.
        ApiError
            On a non-retryable HTTP error.
        """
        if not self._api_key:
            raise ApiKeyMissingError(
                "FOOTBALL_DATA_API_KEY environment variable is not set. "
                "Register at https://www.football-data.org/ to get a free key."
            )

        # Always fetch the full GROUP_STAGE list and filter client-side so we
        # only consume one request per cache-miss (not one per group).
        cache_key = f"group_matches:{self._competition_code}:{season}"
        all_matches = self._cached_fetch(
            cache_key,
            path=f"/competitions/{self._competition_code}/matches",
            params={"stage": "GROUP_STAGE", "season": str(season)},
        ).get("matches", [])

        if group:
            all_matches = [m for m in all_matches if m.get("group") == group]

        return all_matches

    # ── Internal helpers ──────────────────────────────────────────────────

    def _cached_fetch(self, cache_key: str, path: str, params: dict) -> dict:
        """Return cached data if fresh; otherwise issue a throttled HTTP request."""
        now = time.monotonic()
        if cache_key in self._cache:
            fetched_at, data = self._cache[cache_key]
            age = now - fetched_at
            if age < self._cache_ttl:
                logger.debug(
                    "Cache hit for %s (age=%.1f s / ttl=%s s)",
                    cache_key, age, self._cache_ttl,
                )
                return data

        data = self._fetch_with_retry(path, params)
        self._cache[cache_key] = (time.monotonic(), data)
        return data

    def _fetch_with_retry(self, path: str, params: dict, *, _retries: int = 1) -> dict:
        """Issue a single HTTP request, retrying once on HTTP 429."""
        self._throttle()
        try:
            return self._fetch(path, params)
        except ApiError as exc:
            if exc.status == 429 and _retries > 0:
                logger.warning(
                    "Rate-limited (HTTP 429). Backing off 60 s before retry."
                )
                time.sleep(60)
                return self._fetch_with_retry(path, params, _retries=_retries - 1)
            raise

    def _throttle(self) -> None:
        """Block until the minimum inter-request gap has elapsed."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        wait = self._throttle_interval - elapsed
        if wait > 0:
            logger.debug("Throttling: sleeping %.2f s", wait)
            time.sleep(wait)
        self._last_request_time = time.monotonic()

    def _fetch(self, path: str, params: dict) -> dict:
        """Make a single HTTP GET request and return the parsed JSON body."""
        query = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}{path}?{query}"
        logger.info("GET %s", url)

        req = urllib.request.Request(
            url,
            headers={
                "X-Auth-Token": self._api_key,
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
            return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise ApiError(exc.code, body[:200]) from exc
        except urllib.error.URLError as exc:
            raise ApiError(0, str(exc.reason)) from exc
