"""
request.history() for the *_TS indicators inside QIS.

TrendSpider serves request.history(ticker, resolution) from its own data
servers, reaching back at least 320 bars of the requested resolution. The
QIS equivalent fetches the same ticker/interval from Twelve Data (QIS's
market-data source). When the chart's own ticker is requested at a higher
resolution and no fetch is possible, the chart bars are resampled into
TrendSpider-style bars instead (same session rules as bar_at()).
"""

from __future__ import annotations

import functools
import logging

import pandas as pd

from app.indicators.trendspider_store._runtime import sessions
from app.indicators.trendspider_store._runtime.api import REGULAR_SESSION

log = logging.getLogger(__name__)

TD_INTERVAL = {
    "1": "1min", "5": "5min", "15": "15min", "30": "30min", "45": "45min", "60": "1h", "120": "2h", "240": "4h",
    "D": "1day", "1440": "1day", "W": "1week", "M": "1month",
}
MINUTES = {"D": 1440, "1440": 1440, "W": 10080, "M": 43200, "Q": 129600, "Y": 525600}


def tf_minutes(res):
    res = str(res).upper()
    if res in MINUTES:
        return MINUTES[res]
    try:
        return float(res)
    except ValueError:
        return None


def resample_bars(bars, res):
    groups, order = {}, []
    for i, t in enumerate(bars["time"]):
        key = sessions.bar_at(res, REGULAR_SESSION, t * 1000, greedy_daily=True)
        if key is None:
            continue
        if key not in groups:
            groups[key] = [key // 1000, bars["open"][i], bars["high"][i], bars["low"][i], bars["close"][i], bars["volume"][i]]
            order.append(key)
        else:
            g = groups[key]
            g[2] = max(g[2], bars["high"][i])
            g[3] = min(g[3], bars["low"][i])
            g[4] = bars["close"][i]
            g[5] += bars["volume"][i]
    cols = ["time", "open", "high", "low", "close", "volume"]
    return {k: [groups[o][j] for o in order] for j, k in enumerate(cols)}


@functools.lru_cache(maxsize=64)
def _fetch(ticker: str, interval: str, outputsize: int):
    from app.services.backtest_data import fetch_backtest_bars

    return fetch_backtest_bars(ticker, interval, outputsize=outputsize)


class QISHistoryProvider:
    def __init__(self, df, bars, ticker, resolution):
        self.df, self.bars, self.ticker, self.resolution = df, bars, ticker, str(resolution)

    def history(self, ticker, resolution, ext_session=False, chart_type="candles", base=None):
        from app.indicators.trendspider_store._runtime.indicator import frame_to_bars

        from app.indicators.trendspider_store._runtime.indicator import UNKNOWN_TICKER

        res = str(resolution).upper()
        same = ticker.upper() == str(self.ticker).upper()
        if same and tf_minutes(res) == tf_minutes(self.resolution):
            return self.bars
        if same and self.ticker == UNKNOWN_TICKER:
            # Symbol unknown: only the chart's own bars are available.
            if (tf_minutes(res) or 0) > (tf_minutes(self.resolution) or 0):
                return resample_bars(self.bars, res)
            return {"error": f"no {res} data: the chart's symbol is unknown"}
        interval = TD_INTERVAL.get(res)
        if interval is not None:
            try:
                df = _fetch(ticker.upper(), interval, 5000)
                return frame_to_bars(df, res if not res.isdigit() else res)
            except Exception as exc:  # network/auth/symbol problems
                log.warning("request.history(%s, %s) fetch failed: %s", ticker, res, exc)
        if same and (tf_minutes(res) or 0) > (tf_minutes(self.resolution) or 0):
            return resample_bars(self.bars, res)
        return {"error": f"no data for {ticker} at resolution {res}"}

    def alt_data(self, kind, *args):
        if kind == "http":
            return http_get(*args)
        raise_unavailable(kind)


def raise_unavailable(kind):
    from app.indicators.trendspider_store._runtime import js as J

    raise J.Unsupported(
        f"request.{kind}() is TrendSpider alternative data; QIS has no {kind} feed, so this indicator cannot run here"
    )


_HTTP_CACHE: dict[str, tuple[float, object]] = {}


def http_get(url=None, ttl=600, headers=None, *_):
    """request.http(): HTTPS GET, JSON-decoded when the response is JSON,
    cached for `ttl` seconds (clamped to 5s..24h like TrendSpider)."""
    import json
    import time

    import requests

    if not isinstance(url, str) or not url.startswith("https://"):
        return {"error": 'url must start from "https://"'}
    ttl = min(max(5, float(ttl or 600)), 86400)
    hit = _HTTP_CACHE.get(url)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    allowed = {"authorization", "accept", "user-agent", "x-api-key"}
    hdrs = {k: v for k, v in (headers or {}).items() if str(k).lower() in allowed}
    try:
        r = requests.get(url, headers=hdrs, timeout=10)
    except requests.RequestException as exc:
        return {"error": str(exc)}
    if r.status_code // 100 != 2:
        return {"error": f"HTTP {r.status_code}"}
    body = r.content[: 10 * 1024 * 1024]
    if "json" in r.headers.get("content-type", ""):
        try:
            data = json.loads(body)
        except ValueError:
            data = body.decode("utf-8", "replace")
    else:
        data = body.decode("utf-8", "replace")
    _HTTP_CACHE[url] = (time.time(), data)
    return data
