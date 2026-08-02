"""
Tastytrade OAuth + quote-token client (https://developer.tastytrade.com).

Used only to obtain short-lived access tokens (via the long-lived
refresh_token from an OAuth2 app registered in Tastytrade's developer
portal) and DXLink streamer quote tokens for live market data -- not
for account data or order placement. The actual streaming connection
lives in app.services.tastytrade_stream; this module is the synchronous
REST/token half.

Requires TASTYTRADE_CLIENT_ID, TASTYTRADE_CLIENT_SECRET, and
TASTYTRADE_REFRESH_TOKEN set (backend/.env) -- see backend/.env.example.
"""

import time

import requests

from app.config.settings import settings
from app.core.exceptions import TastytradeError

_TIMEOUT_SECONDS = 10
# Refresh a little before the token's real expiry so a request never
# races a token that's about to go stale mid-flight.
_EXPIRY_SAFETY_MARGIN_SECONDS = 60


class TastytradeSession:
    """Caches the short-lived OAuth access token, refreshing it via the
    long-lived refresh_token only when it's missing or close to expiry.
    """

    def __init__(self):
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def get_access_token(self) -> str:
        if self._access_token is None or time.monotonic() >= self._expires_at:
            self._refresh()
        return self._access_token

    def _refresh(self) -> None:
        if not (
            settings.tastytrade_client_id
            and settings.tastytrade_client_secret
            and settings.tastytrade_refresh_token
        ):
            raise TastytradeError(
                "TASTYTRADE_CLIENT_ID, TASTYTRADE_CLIENT_SECRET, and TASTYTRADE_REFRESH_TOKEN must all be "
                "set. Add them to backend/.env (see backend/.env.example)."
            )

        try:
            resp = requests.post(
                f"{settings.tastytrade_base_url}/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.tastytrade_client_id,
                    "client_secret": settings.tastytrade_client_secret,
                    "refresh_token": settings.tastytrade_refresh_token,
                },
                timeout=_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            body = resp.json()
        except requests.RequestException as exc:
            # Not f"...{exc}" -- avoid echoing request details (which
            # could embed the form-encoded client_secret/refresh_token)
            # into the error text, the same care taken in
            # twelvedata_client for its apikey query param.
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise TastytradeError(f"Could not refresh a Tastytrade access token (HTTP {status}).") from exc

        access_token = body.get("access_token")
        expires_in = body.get("expires_in")
        if not access_token or not expires_in:
            raise TastytradeError("Tastytrade token refresh response was missing access_token/expires_in.")

        self._access_token = access_token
        self._expires_at = time.monotonic() + expires_in - _EXPIRY_SAFETY_MARGIN_SECONDS


# Module-level singleton, same pattern as `settings = Settings()` --
# every caller shares one cached token instead of re-authenticating.
session = TastytradeSession()


def get_quote_token() -> dict:
    """
    Fetch a DXLink streamer token + WebSocket URL for live quote
    subscriptions. Returns Tastytrade's raw {"token": ..., "dxlink-url":
    ...} data -- app.services.tastytrade_stream is responsible for
    driving the actual DXLink connection.
    """
    access_token = session.get_access_token()
    try:
        resp = requests.get(
            f"{settings.tastytrade_base_url}/api-quote-tokens",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise TastytradeError(f"Could not fetch a Tastytrade quote token (HTTP {status}).") from exc

    data = body.get("data") or {}
    if not data.get("token") or not data.get("dxlink-url"):
        raise TastytradeError("Tastytrade quote-token response was missing token/dxlink-url.")
    return data
