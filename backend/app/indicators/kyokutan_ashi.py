"""
Kyokutan-Ashi ("extreme-leg") candles.

An amplified Heikin-Ashi variant: computes the standard HA open/close
recursion, takes the RAW deviation of each real OHLC value from its HA
counterpart, scales that deviation by a multiplier, then re-anchors the
scaled deviations onto a chosen reference price (the real open, close,
or hl2) -- producing synthetic candles that exaggerate whatever HA was
already smoothing away, rather than smoothing it further.

haMode "Simplified" skips HA-open's usual self-referential recursion
and uses the prior bar's raw (open+close)/2 directly instead.

calc_mode is NOT exposed as a parameter: the source script's two modes
("Max/Min" vs "Strict") take different arithmetic paths but are
algebraically identical -- anchor + max(a,b,c,d) equals
max(anchor+a, anchor+b, anchor+c, anchor+d) -- so both produce the same
output for every bar; only one formula is implemented here.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("kyokutan_ashi")
class KyokutanAshi(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="kyokutan_ashi",
            display_name="Kyokutan-Ashi",
            description="An amplified Heikin-Ashi variant that scales each bar's deviation from its HA counterpart and re-anchors it onto the real open/close/hl2.",
            category="overlap",
            default_params={"anchor": "open", "ha_mode": "traditional", "deviation_multiplier": 1.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = len(out)
        o, h, l, c = out["open"].to_numpy(), out["high"].to_numpy(), out["low"].to_numpy(), out["close"].to_numpy()

        ha_close = (o + h + l + c) / 4
        ha_open = np.full(n, np.nan)
        if n > 0:
            if p["ha_mode"] == "traditional":
                ha_open[0] = (o[0] + c[0]) / 2
                for i in range(1, n):
                    ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2
            else:
                ha_open[0] = np.nan
                for i in range(1, n):
                    ha_open[i] = (o[i - 1] + c[i - 1]) / 2

        ha_high = np.maximum(h, np.maximum(ha_open, ha_close))
        ha_low = np.minimum(l, np.minimum(ha_open, ha_close))

        mult = p["deviation_multiplier"]
        raw_open = (o - ha_open) * mult
        raw_close = (c - ha_close) * mult
        raw_high = (h - ha_high) * mult
        raw_low = (l - ha_low) * mult

        if p["anchor"] == "open":
            anchor = o
        elif p["anchor"] == "close":
            anchor = c
        else:
            anchor = (h + l) / 2

        anti_open = anchor + raw_open
        anti_close = anchor + raw_close
        anti_high = np.maximum.reduce([anchor + raw_open, anchor + raw_close, anchor + raw_high, anchor + raw_low])
        anti_low = np.minimum.reduce([anchor + raw_open, anchor + raw_close, anchor + raw_high, anchor + raw_low])

        out["kyokutan_ashi_open"] = anti_open
        out["kyokutan_ashi_high"] = anti_high
        out["kyokutan_ashi_low"] = anti_low
        out["kyokutan_ashi_close"] = anti_close
        return out
