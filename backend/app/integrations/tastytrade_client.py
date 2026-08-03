"""
Tastytrade OAuth + market-data client (https://developer.tastytrade.com).

Two things live here:
    - OAuth token management (short-lived access tokens refreshed from
      the long-lived refresh_token) and DXLink streamer quote tokens.
    - fetch_historical_bars(): a one-shot historical-bars fetch via a
      short-lived DXLink connection (Candle events) -- the one bar
      source for the whole app, injectable as `fetch_bars` into
      app.services.levels_service / app.services.signal_service /
      app.services.backtest_data.

Requires TASTYTRADE_CLIENT_ID, TASTYTRADE_CLIENT_SECRET, and
TASTYTRADE_REFRESH_TOKEN set (backend/.env) -- see backend/.env.example.
"""

import asyncio
import json
import time

import pandas as pd
import requests
import websockets

from app.config.settings import settings
from app.core.exceptions import TastytradeError
from app.integrations import dxlink

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
            # into the error text.
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


# --- Historical bars via DXLink Candle events ------------------------

# dxFeed candle-symbol periodicity suffix, e.g. "AAPL{=5m}".
_DXFEED_PERIODICITY = {
    "1min": "1m",
    "5min": "5m",
    "15min": "15m",
    "30min": "30m",
    "1h": "1h",
    "1day": "1d",
}

# Used only to size a generous fromTime lookback from `outputsize` --
# over-requesting is harmless since _collect_candles stops as soon as
# it has enough, so this doesn't need to be precise.
_REGULAR_SESSION_MINUTES = 390  # 9:30-16:00 America/New_York
_INTERVAL_MINUTES = {"1min": 1, "5min": 5, "15min": 15, "30min": 30, "1h": 60, "1day": 390}

# Collection stops on whichever of these hits first: enough candles,
# a quiet period (no new message), or the overall cap.
_QUIET_PERIOD_SECONDS = 2.0
_MAX_COLLECT_SECONDS = 20.0

_CANDLE_FIELDS = ["eventType", "eventSymbol", "time", "open", "high", "low", "close", "volume"]


def _periodicity_for_interval(interval: str) -> str:
    try:
        return _DXFEED_PERIODICITY[interval]
    except KeyError:
        raise TastytradeError(
            f"Unsupported interval '{interval}' for Tastytrade historical bars. "
            f"Supported: {sorted(_DXFEED_PERIODICITY)}."
        ) from None


def _from_time_ms_for_outputsize(interval: str, outputsize: int) -> int:
    minutes_per_bar = _INTERVAL_MINUTES.get(interval, 5)
    bars_per_session = max(1, _REGULAR_SESSION_MINUTES // minutes_per_bar)
    trading_days_needed = -(-outputsize // bars_per_session)  # ceil division
    # Weekends/holidays roughly inflate trading-day count by ~1.6x in
    # calendar days, plus a flat few extra days of slack.
    calendar_days_back = int(trading_days_needed * 1.6) + 5
    return int((time.time() - 86400 * calendar_days_back) * 1000)


def _is_real_candle(event: dict) -> bool:
    # A just-subscribed, not-yet-computed candle arrives with every OHLC
    # field as the literal string "NaN" -- confirmed against a live
    # connection -- rather than being omitted or JSON null.
    return event.get("open") != "NaN" and event.get("time") is not None


async def _collect_candles(symbol: str, periodicity: str, outputsize: int, from_time_ms: int) -> list[dict]:
    quote_token = get_quote_token()
    # tho=true (trading hours only) -- confirmed against a live
    # connection: without it, candles include pre-/after-market data,
    # which would silently pull extended-hours ticks into
    # levels_service's session-boundary aggregates (prior close, daily
    # high/low) where Twelve Data's regular-session-only bars didn't.
    dxfeed_symbol = f"{symbol}{{={periodicity},tho=true}}"

    async with websockets.connect(quote_token["dxlink-url"]) as ws:
        await dxlink.handshake(ws, quote_token["token"], {"Candle": _CANDLE_FIELDS})
        await ws.send(json.dumps({
            "type": "FEED_SUBSCRIPTION",
            "channel": 1,
            "add": [{"type": "Candle", "symbol": dxfeed_symbol, "fromTime": from_time_ms}],
        }))

        candles: list[dict] = []
        deadline = time.monotonic() + _MAX_COLLECT_SECONDS
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=min(_QUIET_PERIOD_SECONDS, remaining))
            except asyncio.TimeoutError:
                break  # quiet period elapsed -- backfill is done (or symbol has no more history)

            message = json.loads(raw)
            if message.get("type") != "FEED_DATA":
                continue
            for event in message.get("data", []):
                if event.get("eventType") == "Candle" and _is_real_candle(event):
                    candles.append(event)

            # Candles arrive newest-first, so once we have enough we
            # already have exactly the freshest window -- no need to
            # keep waiting out the quiet period.
            if len(candles) >= outputsize:
                break

    return candles


def fetch_historical_bars(
    symbol: str,
    interval: str = "1min",
    outputsize: int = 5000,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Fetch historical bars for `symbol` via Tastytrade's DXLink feed and
    return a raw (not-yet-normalized) DataFrame with a "date" column
    plus lowercase open/high/low/close/volume, chronologically sorted --
    ready for the same detect -> normalize -> validate pipeline every
    bar consumer in this app (levels_service, signal_service,
    backtest_data) runs it through.

    Unlike a simple REST call, this opens a short-lived DXLink WebSocket
    connection, subscribes to a Candle feed with a `fromTime` backfill
    request, and collects events until enough bars have arrived (see
    _collect_candles). Safe to call from a sync context that's already
    off the main event loop (every current caller runs inside a thread-
    pool worker: FastAPI's sync route handlers, or poller.py's
    asyncio.to_thread(self.tick)) -- asyncio.run() here starts its own
    fresh loop in that thread rather than colliding with one already
    running.
    """
    periodicity = _periodicity_for_interval(interval)  # validate before opening a connection

    if start_date:
        from_time_ms = int(pd.Timestamp(start_date).timestamp() * 1000)
    else:
        from_time_ms = _from_time_ms_for_outputsize(interval, outputsize)

    try:
        candles = asyncio.run(_collect_candles(symbol, periodicity, outputsize, from_time_ms))
    except TastytradeError:
        raise
    except Exception as exc:
        raise TastytradeError(f"Could not fetch historical bars for '{symbol}' from Tastytrade.") from exc

    if not candles:
        raise TastytradeError(
            f"Tastytrade returned no historical bars for '{symbol}'. Check the symbol and interval, and "
            "whether the market has been open recently enough to cover this lookback."
        )

    df = pd.DataFrame(candles)
    df["date"] = (
        pd.to_datetime(df["time"], unit="ms", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    )
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col])
    df = df[["date", "open", "high", "low", "close", "volume"]].sort_values("date").reset_index(drop=True)

    if end_date:
        df = df[df["date"] <= pd.Timestamp(end_date)].reset_index(drop=True)

    # A quiet-period/timeout exit (rather than the outputsize early-exit)
    # can overshoot since a single batched message can carry more than
    # one candle -- keep only the freshest `outputsize` rows, matching
    # Twelve Data's outputsize contract.
    if len(df) > outputsize:
        df = df.iloc[-outputsize:].reset_index(drop=True)

    return df
