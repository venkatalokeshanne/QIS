"""VSA No Supply / No Demand — a classic Wyckoff volume-spread-analysis pattern: a low-volume bar with wicks on both sides of its body (a "pin") whose direction fails to make a new high (for a bullish "No Demand" bar) or new low (for a bearish "No Supply" bar) relative to the last N closes, while still dipping/pushing past at least one of them on the other side -- read as weak participation in that direction.

The source script's tick-size epsilon (syminfo.mintick, used only to
avoid float-equality edge cases around the body/wick boundary) is
simplified to a plain strict inequality here.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("vsa_no_supply_demand")
class VSANoSupplyDemand(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vsa_no_supply_demand",
            display_name="VSA No Supply / No Demand",
            description="A low-volume, double-wicked bar that fails to make a new close-relative high/low in its own direction -- a classic Wyckoff weak-participation read.",
            category="price_action",
            default_params={"lookback": 10},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["lookback"]

        is_bull = out["close"] > out["open"]
        is_bear = out["open"] > out["close"]

        prev_vol, prev_vol2 = out["volume"].shift(1), out["volume"].shift(2)
        low_volume = (out["volume"] < prev_vol) & (out["volume"] < prev_vol2)

        bull_pins = (out["high"] > out["close"]) & (out["low"] < out["open"])
        bear_pins = (out["high"] > out["open"]) & (out["low"] < out["close"])
        pins = is_bull & bull_pins | is_bear & bear_pins

        close_roll_max = out["close"].rolling(window=n, min_periods=n).max()
        close_roll_min = out["close"].rolling(window=n, min_periods=n).min()
        close_above = close_roll_max > out["high"]
        close_below = close_roll_min < out["low"]

        out["vsa_no_demand"] = is_bull & low_volume & pins & ~close_above & close_below
        out["vsa_no_supply"] = is_bear & low_volume & pins & ~close_below & close_above
        return out
