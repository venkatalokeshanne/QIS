"""
Tests for app.integrations.tastytrade_client, mocking requests so these
run without a real network call or OAuth credentials.
"""

import time

import pytest
import requests

from app.config.settings import settings
from app.core.exceptions import TastytradeError
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
