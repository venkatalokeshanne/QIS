"""ATR Strong Bar — flags bars whose range is unusually large relative to ATR, with a big body and a close near the extreme of the bar (bullish or bearish "strong bar")."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("atr_strong_bar")
class ATRStrongBar(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="atr_strong_bar",
            display_name="ATR Strong Bar",
            description="Flags bars with an unusually large range (vs ATR), a big body, and a close near the bar's extreme -- bullish or bearish 'strong bars'.",
            category="volatility",
            default_params={
                "atr_period": 20,
                "atr_multiple": 1.2,
                "bull_close_pct": 0.60,
                "bear_close_pct": 0.40,
                "min_body_pct": 0.50,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        atr_n, atr_mult, bull_pct, bear_pct, body_pct = (
            p["atr_period"], p["atr_multiple"], p["bull_close_pct"], p["bear_close_pct"], p["min_body_pct"]
        )

        atr = wilders_smooth(true_range(out), atr_n)
        bar_range = out["high"] - out["low"]

        close_pos = ((out["close"] - out["low"]) / bar_range).where(bar_range > 0, 0.5)
        body_size = ((out["close"] - out["open"]).abs() / bar_range).where(bar_range > 0, 0.0)

        is_big = bar_range >= atr * atr_mult
        has_body = body_size >= body_pct

        is_strong_bull = is_big & (out["close"] >= out["open"]) & has_body & (close_pos >= bull_pct)
        is_strong_bear = is_big & (out["close"] < out["open"]) & has_body & (close_pos <= bear_pct)

        out[f"atr_strong_bar_{atr_n}_bull"] = is_strong_bull
        out[f"atr_strong_bar_{atr_n}_bear"] = is_strong_bear
        return out
