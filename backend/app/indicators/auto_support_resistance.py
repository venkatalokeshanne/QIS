"""Auto Support & Resistance — clusters recent confirmed swing highs/lows (within `cluster_pct` of each other) into levels, ranked by how many swings touched each cluster -- more touches implies a more significant level."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("auto_support_resistance")
class AutoSupportResistance(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="auto_support_resistance",
            display_name="Auto Support & Resistance",
            description="Clusters recent swing highs/lows into levels, ranked by how many swings touched each cluster.",
            category="price_action",
            default_params={"swing_range": 5, "lookback": 100, "cluster_pct": 0.5},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        left = right = p["swing_range"]
        window = left + right + 1

        def is_swing_high(w: pd.Series) -> bool:
            return w.iloc[left] == w.max() and (w == w.iloc[left]).sum() == 1

        def is_swing_low(w: pd.Series) -> bool:
            return w.iloc[left] == w.min() and (w == w.iloc[left]).sum() == 1

        swing_high_mask = (
            out["high"].rolling(window=window, min_periods=window).apply(is_swing_high, raw=False).astype(bool)
        ).shift(-right).fillna(False).astype(bool)
        swing_low_mask = (
            out["low"].rolling(window=window, min_periods=window).apply(is_swing_low, raw=False).astype(bool)
        ).shift(-right).fillna(False).astype(bool)

        swing_prices = pd.concat([out["high"].where(swing_high_mask), out["low"].where(swing_low_mask)]).dropna()

        lookback = p["lookback"]
        recent = swing_prices.iloc[-lookback:] if len(swing_prices) > 0 else swing_prices
        levels: list[tuple[float, int]] = []  # (level_price, touch_count)
        cluster_frac = p["cluster_pct"] / 100

        for price in sorted(recent.tolist()):
            matched = False
            for i, (level_price, count) in enumerate(levels):
                if abs(price - level_price) / max(level_price, 1e-9) <= cluster_frac:
                    # Recompute the cluster's average price as new touches arrive.
                    new_count = count + 1
                    new_price = (level_price * count + price) / new_count
                    levels[i] = (new_price, new_count)
                    matched = True
                    break
            if not matched:
                levels.append((price, 1))

        levels.sort(key=lambda lv: lv[1], reverse=True)
        top_levels = [lv[0] for lv in levels[:5]]
        while len(top_levels) < 5:
            top_levels.append(np.nan)

        for i, level in enumerate(top_levels):
            out[f"auto_sr_level_{i + 1}"] = level
        return out
