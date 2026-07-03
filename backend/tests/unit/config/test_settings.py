"""
Tests for Settings.cors_allowed_origins parsing.

Host dashboards like Render's env var UI are plain text fields, not JSON
editors -- pydantic-settings' default behavior for list[str] fields
requires exact JSON array syntax from the env var or it crashes on
startup. cors_allowed_origins_env is a plain str field instead, with
parsing handled by the cors_allowed_origins property so a bare URL or
comma-separated URLs work too.
"""

from app.config.settings import Settings


def test_default_is_localhost(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    assert Settings().cors_allowed_origins == ["http://localhost:5173"]


def test_bare_url(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.vercel.app")
    assert Settings().cors_allowed_origins == ["https://app.vercel.app"]


def test_comma_separated_urls(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://a.com, https://b.com")
    assert Settings().cors_allowed_origins == ["https://a.com", "https://b.com"]


def test_json_array_still_works(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", '["https://a.com","https://b.com"]')
    assert Settings().cors_allowed_origins == ["https://a.com", "https://b.com"]
