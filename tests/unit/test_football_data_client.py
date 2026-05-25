"""Unit tests for FootballDataClient — throttling, caching, error handling."""
from __future__ import annotations

import json
import time
import unittest
from unittest.mock import MagicMock, patch

from core.network import (
    ApiError,
    ApiKeyMissingError,
    FootballDataClient,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_client(api_key: str = "test_token", throttle: float = 0.0, ttl: int = 300):
    return FootballDataClient(
        api_key=api_key,
        throttle_interval_s=throttle,
        cache_ttl_s=ttl,
        competition_code="WC",
    )


def _fake_response(data: dict):
    """Return a mock urlopen context manager yielding JSON bytes."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestApiKeyMissing(unittest.TestCase):
    def test_raises_when_no_key(self):
        client = FootballDataClient(api_key=None, throttle_interval_s=0.0)
        with self.assertRaises(ApiKeyMissingError):
            client.get_group_matches()


class TestGetGroupMatches(unittest.TestCase):
    def setUp(self):
        self.client = _make_client()

    def _stub_urlopen(self, matches: list[dict]):
        return patch(
            "urllib.request.urlopen",
            return_value=_fake_response({"matches": matches}),
        )

    def test_returns_matches_list(self):
        sample = [{"id": 1, "group": "GROUP_A", "status": "SCHEDULED"}]
        with self._stub_urlopen(sample):
            result = self.client.get_group_matches()
        self.assertEqual(result, sample)

    def test_group_filter_applied_client_side(self):
        matches = [
            {"id": 1, "group": "GROUP_A"},
            {"id": 2, "group": "GROUP_B"},
            {"id": 3, "group": "GROUP_A"},
        ]
        with self._stub_urlopen(matches):
            result = self.client.get_group_matches(group="GROUP_A")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(m["group"] == "GROUP_A" for m in result))

    def test_cache_hit_skips_network(self):
        sample = [{"id": 99}]
        with self._stub_urlopen(sample) as mock_urlopen:
            self.client.get_group_matches()
            self.client.get_group_matches()  # should use cache
        # urlopen should only be called once
        self.assertEqual(mock_urlopen.call_count, 1)

    def test_cache_miss_after_ttl(self):
        sample = [{"id": 7}]
        # Use a very short TTL
        client = _make_client(ttl=1)
        with patch("urllib.request.urlopen", return_value=_fake_response({"matches": sample})) as mock_urlopen:
            client.get_group_matches()
            time.sleep(1.1)
            client.get_group_matches()
        self.assertEqual(mock_urlopen.call_count, 2)

    def test_url_contains_stage_group_stage(self):
        with patch("urllib.request.urlopen", return_value=_fake_response({"matches": []})) as m:
            self.client.get_group_matches()
        call_args = m.call_args
        req = call_args[0][0]
        self.assertIn("GROUP_STAGE", req.full_url)

    def test_request_includes_auth_header(self):
        with patch("urllib.request.urlopen", return_value=_fake_response({"matches": []})) as m:
            self.client.get_group_matches()
        req = m.call_args[0][0]
        self.assertEqual(req.get_header("X-auth-token"), "test_token")


class TestThrottling(unittest.TestCase):
    def test_throttle_enforces_minimum_gap(self):
        # Use a real throttle interval and measure elapsed time
        client = _make_client(throttle=0.1, ttl=0)  # 0 TTL → always re-fetch
        sample = {"matches": []}
        with patch("urllib.request.urlopen", return_value=_fake_response(sample)):
            t0 = time.monotonic()
            client.get_group_matches()
            client.get_group_matches()
            elapsed = time.monotonic() - t0
        # Two requests with 0.1 s gap → at least 0.1 s total
        self.assertGreaterEqual(elapsed, 0.05)  # generous lower bound


class TestErrorHandling(unittest.TestCase):
    def test_http_error_raises_api_error(self):
        import urllib.error
        http_err = urllib.error.HTTPError(
            url="http://x", code=401, msg="Unauthorized", hdrs=None, fp=None
        )
        client = _make_client()
        with patch("urllib.request.urlopen", side_effect=http_err):
            with self.assertRaises(ApiError) as cm:
                client.get_group_matches()
        self.assertEqual(cm.exception.status, 401)

    def test_429_retries_then_raises(self):
        import urllib.error
        http_429 = urllib.error.HTTPError(
            url="http://x", code=429, msg="Too Many Requests", hdrs=None, fp=None
        )
        client = _make_client()
        with patch("time.sleep"):  # don't actually wait 60 s
            with patch("urllib.request.urlopen", side_effect=http_429):
                with self.assertRaises(ApiError) as cm:
                    client.get_group_matches()
        self.assertEqual(cm.exception.status, 429)

    def test_url_error_raises_api_error_status_zero(self):
        import urllib.error
        url_err = urllib.error.URLError(reason="Connection refused")
        client = _make_client()
        with patch("urllib.request.urlopen", side_effect=url_err):
            with self.assertRaises(ApiError) as cm:
                client.get_group_matches()
        self.assertEqual(cm.exception.status, 0)


if __name__ == "__main__":
    unittest.main()
