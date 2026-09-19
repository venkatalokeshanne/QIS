"""
Pocket Pivot (Morales/Kacher).

A volume signature used to spot institutional accumulation before a
breakout confirms: an up-day whose volume exceeds the HIGHEST volume
of any DOWN day in the trailing lookback window -- i.e. buying
pressure on this up day outweighs the worst recent selling pressure,
without needing a new price high yet. compare_all_days (off by
default) relaxes the comparison to the highest volume of any prior
day (up or down), not just down days. use_price_sma_filter (off by
default) adds the classic stricter variant requiring close above a
10-period SMA.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("pocket_pivot")
class PocketPivot(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="pocket_pivot",
            display_name="Pocket Pivot",
            description="An up-day whose volume exceeds the highest down-day volume of the trailing lookback -- a buying-pressure signature that can precede a breakout.",
            category="volume",
            default_params={
                "volume_sma_period": 20,
                "lookback": 10,
                "compare_all_days": False,
                "use_price_sma_filter": False,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        lb = p["lookback"]

        volume_sma = out["volume"].rolling(window=p["volume_sma_period"], min_periods=p["volume_sma_period"]).mean()
        up_day = out["close"] > out["close"].shift(1)
        down_day_volume = out["volume"].where(out["close"] < out["close"].shift(1), 0.0)

        max_down_vol = down_day_volume.shift(1).rolling(window=lb, min_periods=lb).max()
        max_all_vol = out["volume"].shift(1).rolling(window=lb, min_periods=lb).max()
        vol_threshold = max_all_vol if p["compare_all_days"] else max_down_vol

        price_sma_10 = out["close"].rolling(window=10, min_periods=10).mean()
        price_ok = (out["close"] > price_sma_10) if p["use_price_sma_filter"] else True

        out["pocket_pivot_volume_sma"] = volume_sma
        out["pocket_pivot"] = up_day & (out["volume"] > vol_threshold) & price_ok
        return out
