"""Tests for app.services.notification_service.send_telegram_message."""

import pytest
import requests

from app.config.settings import settings
from app.services import notification_service


@pytest.fixture(autouse=True)
def _telegram_configured(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")


def test_send_telegram_message_posts_expected_url_and_payload(monkeypatch):
    calls = []

    def _fake_post(url, json=None, timeout=None):
        calls.append((url, json))

        class _Resp:
            def raise_for_status(self):
                pass

        return _Resp()

    monkeypatch.setattr(requests, "post", _fake_post)

    notification_service.send_telegram_message("hello")

    assert len(calls) == 1
    url, payload = calls[0]
    assert url == "https://api.telegram.org/bottest-token/sendMessage"
    assert payload == {"chat_id": "12345", "text": "hello", "parse_mode": "Markdown"}


def test_send_telegram_message_noops_when_bot_token_unset(monkeypatch):
    monkeypatch.setattr(settings, "telegram_bot_token", "")
    calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **k: calls.append(1))

    notification_service.send_telegram_message("hello")

    assert calls == []


def test_send_telegram_message_noops_when_chat_id_unset(monkeypatch):
    monkeypatch.setattr(settings, "telegram_chat_id", "")
    calls = []
    monkeypatch.setattr(requests, "post", lambda *a, **k: calls.append(1))

    notification_service.send_telegram_message("hello")

    assert calls == []


def test_send_telegram_message_swallows_request_exceptions(monkeypatch):
    def _raise(*a, **k):
        raise requests.RequestException("network blew up")

    monkeypatch.setattr(requests, "post", _raise)

    notification_service.send_telegram_message("hello")  # must not raise
