"""
Glue between a translated store script and QIS's Indicator contract.

register_store_indicator(script, ...) creates and registers an Indicator
named `<name>_TS`. calculate(df, params):
  * converts the OHLCV frame to TrendSpider's bar arrays (bar start times
    as Unix seconds; daily-and-up bars stamped at the 09:30 ET session
    open, which is how TrendSpider timestamps them),
  * runs the script with `params` as its input values (keyed by the input
    ids TrendSpider derives from the input titles),
  * returns every painted series and registered signal as a column named
    `<name>_TS__<series id>`.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry
from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.api import ScriptContext, run_script
from app.indicators.trendspider_store._runtime.provider import QISHistoryProvider

NY = "America/New_York"

# Ticker used when the frame doesn't say which symbol it is. request.history()
# for the chart's own ticker is then served by resampling the chart's bars.
UNKNOWN_TICKER = "CHART"


class StoreScriptError(ValueError):
    """The TrendSpider script itself rejected this input (its own assert, e.g.
    "intraday charts only") -- TrendSpider shows the same error."""


class StoreDataUnavailable(ValueError):
    """The script needs data QIS doesn't have (TrendSpider alternative data)."""


def infer_resolution(index: pd.DatetimeIndex) -> str:
    if len(index) < 2:
        return "D"
    minutes = index.to_series().diff().dropna().dt.total_seconds().div(60).mode().iloc[0]
    if minutes < 1440 - 1:
        return str(int(round(minutes)))
    days = minutes / 1440
    if days < 5:
        return "D"
    if days < 20:
        return "W"
    if days < 80:
        return "M"
    return "Q" if days < 300 else "Y"


def frame_to_bars(df: pd.DataFrame, resolution: str) -> dict:
    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex):
        raise ValueError("TrendSpider store indicators need a DatetimeIndex of bar start times")
    if idx.tz is None:
        idx = idx.tz_localize(NY, ambiguous="infer", nonexistent="shift_forward")
    if not resolution.isdigit():
        # TrendSpider stamps daily-and-up bars at the session open.
        local = idx.tz_convert(NY)
        idx = pd.DatetimeIndex([t.normalize() + pd.Timedelta(hours=9, minutes=30) for t in local])
    # Unit-safe: pandas 3 indexes may be stored in s/ms/us/ns resolution,
    # so the raw int64 (asi8) is NOT necessarily nanoseconds.
    secs = idx.tz_convert("UTC").as_unit("s").asi8.tolist()

    def col(name):
        return [None if (v is None or (isinstance(v, float) and math.isnan(v))) else (float(v)) for v in df[name].tolist()]

    vol = df["volume"].fillna(0).astype(float).tolist() if "volume" in df else [0.0] * len(df)
    return {"time": secs, "open": col("open"), "high": col("high"), "low": col("low"), "close": col("close"), "volume": vol}


def _to_column(values, index):
    vals = []
    kind = "num"
    for v in values:
        if isinstance(v, J.JSObject):
            v = v.get("y", None)
        if v is J.undefined or v is J.HOLE:
            v = None
        if isinstance(v, bool):
            kind = "bool" if kind in ("num", "bool") else kind
        elif isinstance(v, str):
            kind = "str"
            v = J.from_utf16(v)
        elif isinstance(v, (dict, list)):
            v = None
        vals.append(v)
    if kind == "bool" and all(v is None or isinstance(v, bool) for v in vals):
        return pd.Series([bool(v) for v in vals], index=index, dtype=bool)
    if kind == "str":
        return pd.Series(vals, index=index, dtype=object)
    return pd.Series([float(v) if isinstance(v, (int, float)) else float("nan") for v in vals], index=index, dtype=float)


def register_store_indicator(script, *, name, title, developer, url, position, inputs, outputs, signals,
                             requires=(), parity="unverified", description=""):
    default_params = {i["id"]: i["default"] for i in inputs}

    class _StoreIndicator(Indicator):
        TS_SCRIPT = staticmethod(script)
        TS_INPUTS = inputs
        TS_OUTPUTS = outputs
        TS_SIGNALS = signals
        TS_REQUIRES = tuple(requires)
        TS_PARITY = parity
        TS_URL = url

        @property
        def metadata(self) -> IndicatorMetadata:
            return IndicatorMetadata(
                name=name,
                display_name=f"{title} (TrendSpider)",
                description=description or f"TrendSpider store indicator by {developer}. {url}",
                category="trendspider_store",
                default_params=dict(default_params),
            )

        def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
            p = self.validate_params(params)
            resolution = str(p.pop("__resolution__", None) or infer_resolution(df.index))
            ticker = p.pop("__ticker__", None) or df.attrs.get("symbol") or UNKNOWN_TICKER
            bars = frame_to_bars(df, resolution)
            ctx = ScriptContext(bars, inputs=p, ticker=ticker, resolution=resolution,
                                provider=QISHistoryProvider(df, bars, ticker, resolution))
            try:
                res = run_script(script, ctx)
            except J.JSError as exc:
                # The script itself failed (e.g. its own "intraday charts only"
                # assert) -- TrendSpider shows the same error and no series.
                raise StoreScriptError(f"{name}: {exc}") from exc
            except J.Unsupported as exc:
                raise StoreDataUnavailable(f"{name}: {exc}") from exc
            out = df.copy()
            for sid, values in res.out.items():
                if sid.endswith("_color") or res.meta["appearance"].get(sid, {}).get("rendererType") == "visualGrid":
                    continue
                if J.truthy(res.meta["appearance"].get(sid, {}).get("isProjection", J.undefined)):
                    continue
                out[f"{name}__{sid}"] = _to_column(values, df.index)
            return out

    _StoreIndicator.__name__ = _StoreIndicator.__qualname__ = "".join(w.capitalize() for w in name.split("_")) + "Indicator"
    indicator_registry.register(name)(_StoreIndicator)
    return _StoreIndicator
