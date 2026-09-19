"""AlphaTrend (Kivanc Ozbilgic) — an ATR-based trailing level that only ratchets toward price while RSI/MFI momentum (>=50 bullish, <50 bearish) agrees with its direction, giving a smoother, whipsaw-resistant trend line than a plain Chandelier/SuperTrend band."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("alphatrend")
class AlphaTrend(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="alphatrend",
            display_name="AlphaTrend",
            description="ATR-based trailing level that only ratchets toward price while RSI/MFI momentum agrees with its direction (bullish >= 50, bearish < 50).",
            category="trend",
            default_params={"period": 14, "multiplier": 1.0, "source": "close", "no_volume_data": False},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, mult, source, no_volume_data = p["period"], p["multiplier"], p["source"], p["no_volume_data"]

        # Simple (not Wilder-smoothed) moving average of true range -- matches
        # Pine's `ta.sma(ta.tr, AP)`, deliberately not the wilders_smooth ATR
        # every other ATR-based indicator here uses.
        atr = true_range(out).rolling(window=n, min_periods=n).mean()
        up_band = (out["low"] - atr * mult).to_numpy()
        down_band = (out["high"] + atr * mult).to_numpy()

        momentum = _rsi(out[source], n) if no_volume_data else _mfi(out, n)
        bullish = (momentum >= 50).to_numpy()
        valid = atr.notna().to_numpy() & momentum.notna().to_numpy()

        length = len(out)
        alpha_trend = np.full(length, np.nan)
        prev = 0.0  # matches Pine's nz(AlphaTrend[1]) -- "no prior value yet" reads as 0
        for i in range(length):
            if not valid[i]:
                continue
            level = up_band[i] if bullish[i] else down_band[i]
            # Ratchet: while bullish the level only ever rises (never gives back
            # ground below its last value); while bearish it only ever falls.
            held_back = (bullish[i] and level < prev) or (not bullish[i] and level > prev)
            val = prev if held_back else level
            alpha_trend[i] = val
            prev = val

        out[f"alphatrend_{n}_{mult}"] = alpha_trend
        return out


def _rsi(source: pd.Series, period: int) -> pd.Series:
    delta = source.diff()
    avg_gain = wilders_smooth(delta.clip(lower=0), period)
    avg_loss = wilders_smooth(-delta.clip(upper=0), period)
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _mfi(df: pd.DataFrame, period: int) -> pd.Series:
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    money_flow = typical_price * df["volume"]
    price_up = typical_price.diff() > 0
    positive_sum = money_flow.where(price_up, 0.0).rolling(window=period, min_periods=period).sum()
    negative_sum = money_flow.where(~price_up, 0.0).rolling(window=period, min_periods=period).sum()
    money_ratio = positive_sum / negative_sum.replace(0, np.nan)
    return 100 - (100 / (1 + money_ratio))
