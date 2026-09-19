"""
Custom Anchor VWAP.

A VWAP that resets on a repeating clock-time schedule instead of at
session open (app.indicators.vwap) or a single fixed bar
(app.indicators.anchored_vwap): each period starts at the first bar
on/after `anchor_time`, either every day or, for weekly, only on a
chosen weekday -- and accumulates continuously (including through the
rest of that calendar day and, for daily resets before midnight, past
it) until the next scheduled anchor. Bars before the first anchor in
the dataset have no VWAP yet.

Optional standard-deviation bands (population variance of the source
around the running VWAP, volume-weighted) work the same way as
app.indicators.vwap_stdev_bands, just anchored to this custom
schedule instead of session/week/month.

The reset schedule is inherently stateful/recursive (each bar's
accumulation depends on whether an anchor point was just crossed), so
it's computed with an explicit bar-by-bar loop rather than a
vectorized pandas expression -- the same pattern used by
app.indicators.session_volume_profile for session-keyed accumulation.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("custom_anchor_vwap")
class CustomAnchorVWAP(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="custom_anchor_vwap",
            display_name="Custom Anchor VWAP",
            description="VWAP that resets on a repeating clock-time schedule (daily or weekly) rather than at session open or a single fixed anchor bar, with optional standard-deviation bands.",
            category="overlap",
            default_params={
                "anchor_time": "01:00",
                "reset_frequency": "daily",
                "reset_weekday": 0,
                "show_bands": False,
                "band_multiple": 1.0,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("CustomAnchorVWAP requires a DatetimeIndex.")
        out = df.copy()

        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        pv = (typical_price * out["volume"]).to_numpy()
        p2v = (typical_price * typical_price * out["volume"]).to_numpy()
        vol = out["volume"].to_numpy()

        time_str = out.index.strftime("%H:%M")
        at_or_after = time_str >= p["anchor_time"]
        date_key = out.index.date
        weekday = out.index.weekday
        is_weekly = p["reset_frequency"] == "weekly"
        iso_week_key = out.index.isocalendar().week.to_numpy() + out.index.isocalendar().year.to_numpy() * 100

        n = len(out)
        result = np.full(n, np.nan)
        upper_result = np.full(n, np.nan)
        lower_result = np.full(n, np.nan)
        started = False
        cum_pv = 0.0
        cum_p2v = 0.0
        cum_vol = 0.0
        last_period_key = None

        for i in range(n):
            eligible = at_or_after[i] and (not is_weekly or weekday[i] == p["reset_weekday"])
            period_key = iso_week_key[i] if is_weekly else date_key[i]
            is_new_anchor = eligible and (last_period_key is None or period_key != last_period_key)

            if is_new_anchor:
                cum_pv, cum_p2v, cum_vol = pv[i], p2v[i], vol[i]
                started = True
                last_period_key = period_key
            elif started:
                cum_pv += pv[i]
                cum_p2v += p2v[i]
                cum_vol += vol[i]

            if started and cum_vol > 0:
                vwap = cum_pv / cum_vol
                result[i] = vwap
                if p["show_bands"]:
                    variance = max(cum_p2v / cum_vol - vwap * vwap, 0.0)
                    stdev = np.sqrt(variance)
                    upper_result[i] = vwap + p["band_multiple"] * stdev
                    lower_result[i] = vwap - p["band_multiple"] * stdev

        out["custom_anchor_vwap"] = result
        if p["show_bands"]:
            out["custom_anchor_vwap_upper"] = upper_result
            out["custom_anchor_vwap_lower"] = lower_result
        return out
