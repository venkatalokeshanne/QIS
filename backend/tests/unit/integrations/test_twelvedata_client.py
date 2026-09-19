"""
Tests for app.integrations.twelvedata_client -- the round-robin, rate-
aware key pool spreading requests across multiple Twelve Data API keys,
plus fetch_historical_bars' own request/parse/retry behavior.
"""

import pandas as pd
import pytest

from app.core.exceptions import TwelveDataError
from app.integrations import twelvedata_client
from app.integrations.twelvedata_client import _KeyPool, filter_by_session


@pytest.fixture(autouse=True)
def _clear_pool_cache():
    # fetch_historical_bars caches one _KeyPool per distinct key tuple
    # (see _get_pool) so its rate-limit state survives across calls in
    # production -- but that means two tests using the identical key
    # tuple would otherwise share (and pollute) each other's windows.
    twelvedata_client._pools.clear()
    yield
    twelvedata_client._pools.clear()


# --- _KeyPool -------------------------------------------------------


def test_key_pool_rejects_empty_key_list():
    with pytest.raises(TwelveDataError):
        _KeyPool([], requests_per_minute=8)


def test_key_pool_round_robins_across_keys():
    pool = _KeyPool(["k1", "k2", "k3"], requests_per_minute=8)
    acquired = [pool.acquire() for _ in range(6)]
    assert acquired == ["k1", "k2", "k3", "k1", "k2", "k3"]


def test_key_pool_skips_key_at_its_per_minute_cap():
    pool = _KeyPool(["k1", "k2"], requests_per_minute=1)
    assert pool.acquire() == "k1"
    # k1 is now at its cap (1/min) -- the next acquire should skip it
    # and go straight to k2 rather than blocking.
    assert pool.acquire() == "k2"


def test_key_pool_blocks_until_a_slot_frees_when_every_key_is_at_cap(monkeypatch):
    pool = _KeyPool(["k1"], requests_per_minute=1)
    pool.acquire()  # k1 now at cap

    slept = {}

    def fake_sleep(seconds):
        slept["seconds"] = seconds
        # Simulate the window aging out by clearing it, so the retry
        # inside acquire() succeeds instead of looping forever.
        pool._recent_calls["k1"].clear()

    monkeypatch.setattr(twelvedata_client.time, "sleep", fake_sleep)

    assert pool.acquire() == "k1"
    assert slept["seconds"] > 0


def test_key_pool_penalize_saturates_just_that_key():
    pool = _KeyPool(["k1", "k2"], requests_per_minute=8)
    pool.penalize("k1")

    # k1 should now read as fully saturated (8/8) while k2 is untouched.
    assert len(pool._recent_calls["k1"]) == 8
    assert len(pool._recent_calls["k2"]) == 0

    # acquire() should skip the penalized key and go to k2.
    assert pool.acquire() == "k2"


# --- fetch_historical_bars -------------------------------------------


def _fake_response(status_code=200, json_body=None):
    class _Resp:
        def __init__(self):
            self.status_code = status_code

        def json(self):
            return json_body or {}

    return _Resp()


def _values_body(rows):
    return {"status": "ok", "values": rows}


_SAMPLE_ROWS = [
    {"datetime": "2024-01-02 09:35:00", "open": "101", "high": "102", "low": "100", "close": "101.5", "volume": "500"},
    {"datetime": "2024-01-02 09:30:00", "open": "100", "high": "101", "low": "99", "close": "100.5", "volume": "400"},
]


def test_fetch_historical_bars_raises_when_no_keys_configured(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    with pytest.raises(TwelveDataError):
        twelvedata_client.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_returns_normalized_chronological_frame(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "test-key")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    monkeypatch.setattr(
        twelvedata_client.requests, "get", lambda *a, **kw: _fake_response(200, _values_body(_SAMPLE_ROWS))
    )

    df = twelvedata_client.fetch_historical_bars("AAPL", interval="5min")

    assert list(df["date"]) == [pd.Timestamp("2024-01-02 09:30:00"), pd.Timestamp("2024-01-02 09:35:00")]
    assert df["close"].tolist() == [100.5, 101.5]


def test_fetch_historical_bars_retries_a_different_key_on_429(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "key-one")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "key-two")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    seen_keys = []

    def fake_get(url, params, timeout):
        seen_keys.append(params["apikey"])
        if params["apikey"] == "key-one":
            return _fake_response(429, {"status": "error", "code": 429, "message": "rate limited"})
        return _fake_response(200, _values_body(_SAMPLE_ROWS))

    monkeypatch.setattr(twelvedata_client.requests, "get", fake_get)

    df = twelvedata_client.fetch_historical_bars("AAPL")

    assert seen_keys == ["key-one", "key-two"]
    assert len(df) == 2


def test_fetch_historical_bars_raises_after_every_key_rate_limited(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "key-one")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "key-two")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    monkeypatch.setattr(
        twelvedata_client.requests,
        "get",
        lambda *a, **kw: _fake_response(429, {"status": "error", "code": 429, "message": "rate limited"}),
    )

    with pytest.raises(TwelveDataError):
        twelvedata_client.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_raises_on_api_error_body(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "test-key")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    monkeypatch.setattr(
        twelvedata_client.requests,
        "get",
        lambda *a, **kw: _fake_response(200, {"status": "error", "code": 400, "message": "bad symbol"}),
    )

    with pytest.raises(TwelveDataError):
        twelvedata_client.fetch_historical_bars("NOT_A_SYMBOL")


def test_fetch_historical_bars_clamps_outputsize_to_twelvedata_max(monkeypatch):
    # Regression guard: Twelve Data flat-400s any outputsize above 5000
    # (it does NOT truncate), and several callers' constants were
    # originally sized for the pre-TwelveData streaming feed, which had
    # no such cap. Clamping lives in the client so no caller can
    # reintroduce the 400 by raising its own limit.
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "test-key")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    captured = {}

    def fake_get(url, params, timeout):
        captured.update(params)
        return _fake_response(200, _values_body(_SAMPLE_ROWS))

    monkeypatch.setattr(twelvedata_client.requests, "get", fake_get)

    twelvedata_client.fetch_historical_bars("AAPL", outputsize=100_000)

    assert captured["outputsize"] == twelvedata_client.MAX_OUTPUTSIZE == 5000


def test_fetch_historical_bars_leaves_outputsize_under_the_cap_alone(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "test-key")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    captured = {}

    def fake_get(url, params, timeout):
        captured.update(params)
        return _fake_response(200, _values_body(_SAMPLE_ROWS))

    monkeypatch.setattr(twelvedata_client.requests, "get", fake_get)

    twelvedata_client.fetch_historical_bars("AAPL", outputsize=500)

    assert captured["outputsize"] == 500


def test_fetch_historical_bars_raises_when_no_values_returned(monkeypatch):
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_1", "test-key")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_2", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_3", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_4", "")
    monkeypatch.setattr(twelvedata_client.settings, "twelvedata_api_key_5", "")

    monkeypatch.setattr(
        twelvedata_client.requests, "get", lambda *a, **kw: _fake_response(200, {"status": "ok", "values": []})
    )

    with pytest.raises(TwelveDataError):
        twelvedata_client.fetch_historical_bars("AAPL")


# --- filter_by_session (unchanged, moved from tastytrade_client) -----


def test_filter_by_session_keeps_only_regular_hours_by_default():
    idx = pd.to_datetime(["2024-01-02 08:00", "2024-01-02 09:30", "2024-01-02 12:00", "2024-01-02 16:30"])
    df = pd.DataFrame({"date": idx, "close": [1, 2, 3, 4]})

    result = filter_by_session(df, include_extended_hours=False, include_overnight=False)

    assert list(result["close"]) == [2, 3]


def test_filter_by_session_both_flags_true_is_a_no_op():
    idx = pd.to_datetime(["2024-01-02 02:00", "2024-01-02 09:30"])
    df = pd.DataFrame({"date": idx, "close": [1, 2]})

    result = filter_by_session(df, include_extended_hours=True, include_overnight=True)

    assert len(result) == 2
