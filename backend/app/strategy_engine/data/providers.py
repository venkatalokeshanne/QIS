"""
Market-data providers for the Strategy Selection Engine.

  TwelveData   long regular-hours history (intraday + daily), fetched in
               date-ranged chunks (5000 bars per request). The Basic plan
               has no extended hours and no VIX.
  Tastytrade   extended-hours candles (premarket/after-hours), the VIX
               index, and expected earnings dates. Market data only --
               this module never touches orders or account endpoints.
               Intraday candle history is limited (~3 months).

Every fetch returns a NORMALIZED frame (see normalize.py) plus the
provider name, ready for BarStore.upsert.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import time

import pandas as pd
import requests

from app.config.settings import settings
from app.strategy_engine.data.normalize import normalize_bars
from app.strategy_engine.models import Timeframe


class ProviderError(RuntimeError):
    pass


# ----------------------------------------------------------------------------
# Twelve Data
# ----------------------------------------------------------------------------

TWELVEDATA_INTERVALS = {
    Timeframe.M1: "1min", Timeframe.M5: "5min", Timeframe.M15: "15min", Timeframe.M30: "30min",
    Timeframe.H1: "1h", Timeframe.H2: "2h", Timeframe.H4: "4h",
    Timeframe.D1: "1day", Timeframe.W1: "1week", Timeframe.MN1: "1month",
}


class TwelveDataProvider:
    name = "twelvedata"

    def __init__(self, fetch=None, max_requests: int = 50):
        from app.integrations import twelvedata_client

        self._fetch = fetch or twelvedata_client.fetch_historical_bars
        self.max_requests = max_requests  # guard the daily credit budget

    def fetch(self, symbol: str, timeframe: Timeframe, start: dt.date, end: dt.date) -> pd.DataFrame:
        interval = TWELVEDATA_INTERVALS.get(timeframe)
        if interval is None:
            raise ProviderError(f"Twelve Data has no {timeframe} interval (build it by resampling a finer timeframe)")
        chunks, chunk_end, requests_made = [], end, 0
        while requests_made < self.max_requests:
            raw = self._fetch(symbol, interval=interval, outputsize=5000,
                              start_date=start.isoformat(), end_date=(chunk_end + dt.timedelta(days=1)).isoformat())
            requests_made += 1
            if raw is None or raw.empty:
                break
            chunks.append(raw)
            earliest = pd.Timestamp(raw["date"].min())
            if len(raw) < 5000 or earliest.date() <= start:
                break
            chunk_end = earliest.date()  # overlap one day; duplicates are dropped on normalize
        if not chunks:
            return normalize_bars(pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"]), timeframe)[0]
        df, _ = normalize_bars(pd.concat(chunks, ignore_index=True), timeframe, time_column="date")
        return df


# ----------------------------------------------------------------------------
# Tastytrade (DXLink / dxFeed)
# ----------------------------------------------------------------------------

DXFEED_PERIODS = {
    Timeframe.M1: "1m", Timeframe.M5: "5m", Timeframe.M15: "15m", Timeframe.M30: "30m",
    Timeframe.M65: "65m", Timeframe.H1: "1h", Timeframe.H2: "2h", Timeframe.H4: "4h",
    Timeframe.D1: "1d", Timeframe.W1: "1w", Timeframe.MN1: "1mo",
}
_CANDLE_FIELDS = ["eventType", "eventSymbol", "time", "open", "high", "low", "close", "volume"]


class TastytradeProvider:
    name = "tastytrade"

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self._token: str | None = None
        self._token_expiry = 0.0

    # -- auth ------------------------------------------------------------------
    def _access_token(self) -> str:
        if self._token and time.monotonic() < self._token_expiry:
            return self._token
        if not (settings.tastytrade_client_id and settings.tastytrade_client_secret and settings.tastytrade_refresh_token):
            raise ProviderError("TASTYTRADE_CLIENT_ID / _CLIENT_SECRET / _REFRESH_TOKEN are not set in backend/.env")
        try:
            r = requests.post(f"{settings.tastytrade_base_url}/oauth/token", timeout=self.timeout, data={
                "grant_type": "refresh_token", "client_id": settings.tastytrade_client_id,
                "client_secret": settings.tastytrade_client_secret, "refresh_token": settings.tastytrade_refresh_token})
            r.raise_for_status()
        except requests.RequestException as exc:  # never echo the request (it carries the secret)
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise ProviderError(f"Tastytrade token refresh failed (HTTP {status})") from None
        body = r.json()
        self._token = body["access_token"]
        self._token_expiry = time.monotonic() + float(body.get("expires_in", 900)) - 60
        return self._token

    def _get(self, path: str, params: dict | None = None) -> dict:
        try:
            r = requests.get(f"{settings.tastytrade_base_url}{path}", params=params, timeout=self.timeout,
                             headers={"Authorization": f"Bearer {self._access_token()}"})
            r.raise_for_status()
        except requests.RequestException as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise ProviderError(f"Tastytrade GET {path} failed (HTTP {status})") from None
        return r.json()

    # -- candles ---------------------------------------------------------------
    def fetch(self, symbol: str, timeframe: Timeframe, start: dt.date, end: dt.date | None = None,
              extended_hours: bool = True) -> pd.DataFrame:
        """Candles from `start` (dxFeed serves roughly the last 3 months of
        intraday history). extended_hours=False requests regular hours only."""
        period = DXFEED_PERIODS.get(timeframe)
        if period is None:
            raise ProviderError(f"no dxFeed period for {timeframe}")
        sym = f"{symbol.upper()}{{={period},tho={'false' if extended_hours else 'true'}}}"
        from_ms = int(dt.datetime.combine(start, dt.time(0), dt.timezone.utc).timestamp() * 1000)
        # dxFeed backfills in batches with variable pauses; a long pause can
        # end a collection early. Resume from the last candle received until
        # the history reaches `end` (or a resume brings nothing new).
        target = dt.datetime.combine(end or dt.date.today(), dt.time(0), dt.timezone.utc).timestamp() * 1000
        events: dict[int, dict] = {}
        for _ in range(6):
            got = asyncio.run(self._candles(sym, from_ms))
            new = [e for e in got if e["time"] not in events]
            for e in got:
                events[e["time"]] = e
            if not new or max(events) >= target:
                break
            from_ms = max(events)
        events = [events[k] for k in sorted(events)]
        def stamp(ms):
            t = pd.Timestamp(ms, unit="ms", tz="UTC")
            # dxFeed stamps daily-and-coarser candles at 00:00 UTC OF THE
            # TRADING DATE (verified against Twelve Data). Converting that
            # instant to New York would land on the previous day, so take the
            # UTC calendar date as the (naive, exchange-local) trading date.
            return t if timeframe.is_intraday else pd.Timestamp(t.date())

        raw = pd.DataFrame([{"timestamp": stamp(e["time"]), "open": e["open"], "high": e["high"],
                             "low": e["low"], "close": e["close"], "volume": e.get("volume") or 0} for e in events])
        if raw.empty:
            raw = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
        # Indexes (e.g. VIX) have no volume; dxFeed sends it as the string "NaN".
        raw["volume"] = pd.to_numeric(raw["volume"], errors="coerce").fillna(0.0)
        df, _ = normalize_bars(raw, timeframe, time_column="timestamp")
        if end is not None:
            df = df[df.index.tz_convert("America/New_York").date <= end]
        return df

    async def _candles(self, symbol: str, from_ms: int, cap_s: float = 240.0, quiet_s: float = 10.0) -> list[dict]:
        import websockets

        token = self._get("/api-quote-tokens")["data"]
        async with websockets.connect(token["dxlink-url"], max_size=None) as ws:
            await ws.send(json.dumps({"type": "SETUP", "channel": 0, "version": "0.1-strategy-engine",
                                      "keepaliveTimeout": 60, "acceptKeepaliveTimeout": 60}))
            await ws.send(json.dumps({"type": "AUTH", "channel": 0, "token": token["token"]}))
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), 20))
                if m.get("type") == "AUTH_STATE" and m.get("state") == "AUTHORIZED":
                    break
            await ws.send(json.dumps({"type": "CHANNEL_REQUEST", "channel": 1, "service": "FEED", "parameters": {"contract": "AUTO"}}))
            await ws.recv()
            await ws.send(json.dumps({"type": "FEED_SETUP", "channel": 1, "acceptDataFormat": "FULL",
                                      "acceptEventFields": {"Candle": _CANDLE_FIELDS}}))
            await ws.recv()
            await ws.send(json.dumps({"type": "FEED_SUBSCRIPTION", "channel": 1,
                                      "add": [{"type": "Candle", "symbol": symbol, "fromTime": from_ms}]}))
            out: dict[int, dict] = {}
            deadline = time.monotonic() + cap_s
            while time.monotonic() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=quiet_s)
                except asyncio.TimeoutError:
                    break
                m = json.loads(raw)
                if m.get("type") != "FEED_DATA":
                    continue
                for e in m.get("data", []):
                    # Not-yet-computed candles arrive with "NaN" OHLC.
                    if e.get("eventType") == "Candle" and e.get("time") and e.get("open") not in ("NaN", None):
                        out[e["time"]] = e
        return [out[k] for k in sorted(out)]

    # -- events ----------------------------------------------------------------
    def earnings(self, symbols: list[str]) -> dict[str, dict]:
        """{symbol: {"expected_report_date": date|None, "time_of_day": str|None}}.
        A past date means no upcoming report is known (Tastytrade keeps the
        last one until the next is announced) -- callers must not read it as
        'earnings today'."""
        body = self._get("/market-metrics", {"symbols": ",".join(s.upper() for s in symbols)})
        out = {}
        for item in body.get("data", {}).get("items", []):
            e = item.get("earnings") or {}
            d = e.get("expected-report-date")
            out[item.get("symbol")] = {"expected_report_date": dt.date.fromisoformat(d) if d else None,
                                       "time_of_day": e.get("time-of-day")}
        return out
