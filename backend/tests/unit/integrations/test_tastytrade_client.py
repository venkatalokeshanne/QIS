"""
Tests for app.integrations.tastytrade_client, mocking requests/DXLink
collection so these run without a real network call or OAuth credentials.
"""

import time

import pandas as pd
import pytest
import requests

from app.config.settings import settings
from app.core.exceptions import TastytradeError
from app.integrations import tastytrade_client as tt
from app.integrations.tastytrade_client import TastytradeSession, get_quote_token, session as module_session


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setattr(settings, "tastytrade_client_id", "test-client-id")
    monkeypatch.setattr(settings, "tastytrade_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "tastytrade_refresh_token", "test-refresh-token")


def test_get_access_token_refreshes_when_no_cached_token(monkeypatch):
    calls = []

    def fake_post(url, data=None, timeout=None):
        calls.append((url, data))
        return _FakeResponse({"access_token": "tok-1", "expires_in": 900})

    monkeypatch.setattr(requests, "post", fake_post)

    sess = TastytradeSession()
    token = sess.get_access_token()

    assert token == "tok-1"
    assert len(calls) == 1
    assert calls[0][0].endswith("/oauth/token")
    assert calls[0][1]["grant_type"] == "refresh_token"
    assert calls[0][1]["refresh_token"] == "test-refresh-token"


def test_get_access_token_reuses_cached_token_until_near_expiry(monkeypatch):
    calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **kw: calls.append(1) or _FakeResponse(
        {"access_token": "tok-1", "expires_in": 900}
    ))

    sess = TastytradeSession()
    sess.get_access_token()
    sess.get_access_token()
    sess.get_access_token()

    assert len(calls) == 1, "a still-fresh cached token must not trigger another refresh"


def test_get_access_token_refreshes_again_once_expired(monkeypatch):
    responses = iter([
        _FakeResponse({"access_token": "tok-1", "expires_in": 900}),
        _FakeResponse({"access_token": "tok-2", "expires_in": 900}),
    ])
    monkeypatch.setattr(requests, "post", lambda *a, **kw: next(responses))

    sess = TastytradeSession()
    assert sess.get_access_token() == "tok-1"

    # Force the cached token to look expired without sleeping in the test.
    sess._expires_at = time.monotonic() - 1
    assert sess.get_access_token() == "tok-2"


def test_get_access_token_raises_when_credentials_missing(monkeypatch):
    monkeypatch.setattr(settings, "tastytrade_client_secret", "")
    sess = TastytradeSession()

    with pytest.raises(TastytradeError, match="TASTYTRADE_CLIENT_ID"):
        sess.get_access_token()


def test_refresh_raises_on_network_error_without_leaking_secret(monkeypatch):
    def fake_post(*a, **kw):
        raise requests.ConnectionError("boom, secret=test-client-secret leaked in a bad impl")

    monkeypatch.setattr(requests, "post", fake_post)
    sess = TastytradeSession()

    with pytest.raises(TastytradeError) as exc_info:
        sess.get_access_token()

    assert "test-client-secret" not in str(exc_info.value)
    assert "Could not refresh" in str(exc_info.value)


def test_refresh_raises_on_malformed_response(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _FakeResponse({"token_type": "bearer"}))
    sess = TastytradeSession()

    with pytest.raises(TastytradeError, match="missing access_token"):
        sess.get_access_token()


def test_get_quote_token_uses_bearer_auth_and_returns_data(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _FakeResponse({"access_token": "tok-1", "expires_in": 900}))
    monkeypatch.setattr(module_session, "_access_token", None)
    monkeypatch.setattr(module_session, "_expires_at", 0.0)

    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        return _FakeResponse({"data": {"token": "quote-tok", "dxlink-url": "wss://example/dxlink"}})

    monkeypatch.setattr(requests, "get", fake_get)

    data = get_quote_token()

    assert data == {"token": "quote-tok", "dxlink-url": "wss://example/dxlink"}
    assert captured["url"].endswith("/api-quote-tokens")
    assert captured["headers"]["Authorization"] == "Bearer tok-1"


def test_get_quote_token_raises_on_missing_fields(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _FakeResponse({"access_token": "tok-1", "expires_in": 900}))
    monkeypatch.setattr(module_session, "_access_token", None)
    monkeypatch.setattr(module_session, "_expires_at", 0.0)
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _FakeResponse({"data": {"token": "quote-tok"}}))

    with pytest.raises(TastytradeError, match="missing token/dxlink-url"):
        get_quote_token()


# --- fetch_historical_bars / _collect_candles helpers ------------------


def test_periodicity_for_interval_valid_and_invalid():
    assert tt.periodicity_for_interval("5min") == "5m"
    assert tt.periodicity_for_interval("1day") == "1d"
    with pytest.raises(TastytradeError, match="Unsupported interval"):
        tt.periodicity_for_interval("3min")


def test_is_real_candle_filters_nan_placeholder():
    # Confirmed live: a just-subscribed, not-yet-computed candle arrives
    # with every OHLC field as the literal STRING "NaN".
    assert not tt.is_real_candle({"open": "NaN", "time": 123})
    assert not tt.is_real_candle({"open": 1.0, "time": None})
    assert tt.is_real_candle({"open": 1.0, "time": 123})


def test_build_candle_symbol_includes_periodicity_and_trading_hours_flag():
    assert tt.build_candle_symbol("AAPL", "5m") == "AAPL{=5m,tho=true}"
    assert tt.build_candle_symbol("AAPL", "5m", tho=False) == "AAPL{=5m,tho=false}"


def test_from_time_ms_for_outputsize_looks_generously_far_back():
    now_ms = time.time() * 1000
    from_ms = tt._from_time_ms_for_outputsize("5min", 100)
    assert from_ms < now_ms
    # ~100 5-min bars is ~1.3 regular sessions -- the heuristic's buffer
    # should comfortably span at least a weekend.
    assert (now_ms - from_ms) / 86_400_000 >= 2


def test_fetch_historical_bars_rejects_unsupported_interval_before_any_network_call(monkeypatch):
    async def _should_not_be_called(*a, **kw):
        raise AssertionError("_collect_candles must not be called for an invalid interval")

    monkeypatch.setattr(tt, "_collect_candles", _should_not_be_called)

    with pytest.raises(TastytradeError, match="Unsupported interval"):
        tt.fetch_historical_bars("AAPL", interval="3min")


def _fake_candle(time_ms, close):
    return {
        "eventType": "Candle",
        "eventSymbol": "AAPL{=5m,tho=true}",
        "time": time_ms,
        "open": str(close),
        "high": str(close),
        "low": str(close),
        "close": str(close),
        "volume": "1000",
    }


def test_fetch_historical_bars_builds_expected_shape_and_sort_order(monkeypatch):
    # Candles arrive newest-first from the feed.
    candles = [_fake_candle(1785527700000, 309.03), _fake_candle(1785527400000, 308.87)]

    async def fake_collect(symbol, periodicity, outputsize, from_time_ms, tho=True):
        return candles

    monkeypatch.setattr(tt, "_collect_candles", fake_collect)

    df = tt.fetch_historical_bars("AAPL", interval="5min", outputsize=10)

    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert df["date"].is_monotonic_increasing
    assert df.iloc[-1]["close"] == 309.03  # newest ends up last after chronological sort
    assert df.iloc[0]["close"] == 308.87


def test_fetch_historical_bars_trims_to_outputsize(monkeypatch):
    candles = [_fake_candle(1785527700000 - i * 300_000, float(i)) for i in range(20)]

    async def fake_collect(symbol, periodicity, outputsize, from_time_ms, tho=True):
        return candles

    monkeypatch.setattr(tt, "_collect_candles", fake_collect)

    df = tt.fetch_historical_bars("AAPL", interval="5min", outputsize=5)
    assert len(df) == 5
    # The freshest 5 -- i.e. i=0..4 -- kept, sorted ascending by date.
    assert list(df["close"]) == [4.0, 3.0, 2.0, 1.0, 0.0]


def test_fetch_historical_bars_raises_when_no_candles_come_back(monkeypatch):
    async def fake_collect(symbol, periodicity, outputsize, from_time_ms, tho=True):
        return []

    monkeypatch.setattr(tt, "_collect_candles", fake_collect)

    with pytest.raises(TastytradeError, match="no historical bars"):
        tt.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_keeps_same_day_bars_for_date_only_end_date(monkeypatch):
    candles = [
        _fake_candle(int(pd.Timestamp("2026-08-03 04:05:00", tz="UTC").timestamp() * 1000), 1.0),
        _fake_candle(int(pd.Timestamp("2026-08-03 23:55:00", tz="UTC").timestamp() * 1000), 2.0),
    ]

    async def fake_collect(symbol, periodicity, outputsize, from_time_ms, tho=True):
        return candles

    monkeypatch.setattr(tt, "_collect_candles", fake_collect)

    df = tt.fetch_historical_bars("AAPL", interval="5min", outputsize=10, start_date="2026-08-03", end_date="2026-08-03")

    assert len(df) == 2
    assert df["date"].dt.date.iloc[0] == pd.Timestamp("2026-08-03").date()
    assert df["date"].dt.date.iloc[-1] == pd.Timestamp("2026-08-03").date()


def test_fetch_historical_bars_wraps_unexpected_errors(monkeypatch):
    async def fake_collect(symbol, periodicity, outputsize, from_time_ms, tho=True):
        raise RuntimeError("socket exploded")

    monkeypatch.setattr(tt, "_collect_candles", fake_collect)

    with pytest.raises(TastytradeError, match="Could not fetch historical bars"):
        tt.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_converts_epoch_ms_to_naive_america_new_york(monkeypatch):
    # Verified against a live connection: 1785418200000 ms -> exactly
    # 2026-07-30 09:30:00 in America/New_York (the regular session open).
    candles = [_fake_candle(1785418200000, 100.0)]

    async def fake_collect(symbol, periodicity, outputsize, from_time_ms, tho=True):
        return candles

    monkeypatch.setattr(tt, "_collect_candles", fake_collect)

    df = tt.fetch_historical_bars("AAPL", interval="5min", outputsize=10)

    assert df.iloc[0]["date"] == pd.Timestamp("2026-07-30 09:30:00")
    assert df["date"].dt.tz is None  # naive, matching twelvedata_client's convention
