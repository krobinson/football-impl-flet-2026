"""Application configuration — all values read from environment variables."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels above this file: src/core/config.py)
load_dotenv(Path(__file__).parents[2] / ".env")

# ── football-data.org API ─────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY: str | None = os.environ.get("FOOTBALL_DATA_API_KEY")

# Plan tier controls the minimum gap between requests.
# FREE: 10 req/min → 6 s gap
# STANDARD: 30 req/min → 2 s gap
# FULL: 60 req/min → 1 s gap
_PLAN = os.environ.get("FOOTBALL_DATA_PLAN", "FREE").upper()
_THROTTLE_MAP = {"FREE": 6.0, "STANDARD": 2.0, "FULL": 1.0}
FOOTBALL_DATA_THROTTLE_INTERVAL_S: float = float(
    os.environ.get(
        "FOOTBALL_DATA_THROTTLE_INTERVAL_S",
        str(_THROTTLE_MAP.get(_PLAN, 6.0)),
    )
)

# How long (seconds) to serve a cached response before re-fetching.
FOOTBALL_DATA_CACHE_TTL_S: int = int(
    os.environ.get("FOOTBALL_DATA_CACHE_TTL_S", "300")
)

# Competition code for FIFA World Cup on football-data.org.
FOOTBALL_DATA_WC_CODE: str = os.environ.get("FOOTBALL_DATA_WC_CODE", "WC")
