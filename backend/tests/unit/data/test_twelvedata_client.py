"""
Tests for app.integrations.twelvedata_client, mocking requests.get so
these run without a real network call or API key.
"""

import pandas as pd
import pytest
import requests

from app.config.settings import settings
from app.core.exceptions import TwelveDataError
from app.integrations import twelvedata_client


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
def api_key(monkeypatch):
    monkeypatch.setattr(settings, "twelvedata_api_key", "test-key")


def test_fetch_historical_bars_parses_and_sorts_chronologically(monkeypatch):
    payload = {
        "status": "ok",
        "values": [
            {"datetime": "2024-01-02 09:31:00", "open": "100.5", "high": "102", "low": "100", "close": "101.5", "volume": "600"},
            {"datetime": "2024-01-02 09:30:00", "open": "100", "high": "101", "low": "99", "close": "100.5", "volume": "500"},
        ],
    }
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _FakeResponse(payload))

    df = twelvedata_client.fetch_historical_bars("AAPL")

    assert list(df["date"]) == list(pd.to_datetime(["2024-01-02 09:30:00", "2024-01-02 09:31:00"]))
    assert df.iloc[0]["open"] == 100.0
    assert df["volume"].dtype.kind in "iu" or df["volume"].dtype.kind == "f"


def test_fetch_historical_bars_raises_on_api_error_status(monkeypatch):
    payload = {"status": "error", "code": 400, "message": "bad symbol"}
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _FakeResponse(payload))

    with pytest.raises(TwelveDataError, match="bad symbol"):
        twelvedata_client.fetch_historical_bars("NOTREAL")


def test_fetch_historical_bars_raises_on_empty_values(monkeypatch):
    payload = {"status": "ok", "values": []}
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _FakeResponse(payload))

    with pytest.raises(TwelveDataError, match="no historical bars"):
        twelvedata_client.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_raises_on_network_error(monkeypatch):
    def fake_get(*a, **kw):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(TwelveDataError, match="Could not reach Twelve Data"):
        twelvedata_client.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_raises_when_api_key_missing(monkeypatch):
    monkeypatch.setattr(settings, "twelvedata_api_key", "")
    with pytest.raises(TwelveDataError, match="TWELVEDATA_API_KEY"):
        twelvedata_client.fetch_historical_bars("AAPL")


def test_fetch_historical_bars_passes_params_through(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        return _FakeResponse(
            {
                "status": "ok",
                "values": [
                    {"datetime": "2024-01-02 09:30:00", "open": "1", "high": "1", "low": "1", "close": "1", "volume": "1"}
                ],
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)

    twelvedata_client.fetch_historical_bars(
        "TSLA", interval="5min", outputsize=100, start_date="2024-01-01", end_date="2024-01-31"
    )

    assert captured["url"].endswith("/time_series")
    assert captured["params"]["symbol"] == "TSLA"
    assert captured["params"]["interval"] == "5min"
    assert captured["params"]["outputsize"] == 100
    assert captured["params"]["start_date"] == "2024-01-01"
    assert captured["params"]["end_date"] == "2024-01-31"
    assert captured["params"]["apikey"] == "test-key"
