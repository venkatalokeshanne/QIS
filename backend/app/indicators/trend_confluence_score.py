"""Trend Confluence Score — a 5-factor bull/bear vote (fast EMA > slow EMA, close > fast EMA, RSI > 50, MACD line > its signal, MACD histogram > 0), each contributing one point to a 0-5 bull score and its complementary bear score."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("trend_confluence_score")
class TrendConfluenceScore(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="trend_confluence_score",
            display_name="Trend Confluence Score",
            description="5-factor bull/bear vote (EMA cross, price vs EMA, RSI vs 50, MACD line vs signal, histogram sign) -- each contributes one point to a 0-5 score.",
            category="trend",
            default_params={
                "ema_fast_period": 50,
                "ema_slow_period": 200,
                "rsi_period": 14,
                "macd_fast_period": 12,
                "macd_slow_period": 26,
                "macd_signal_period": 9,
                "bullish_threshold": 4,
                "bearish_threshold": 4,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        ema_fast = out["close"].ewm(span=p["ema_fast_period"], adjust=False, min_periods=p["ema_fast_period"]).mean()
        ema_slow = out["close"].ewm(span=p["ema_slow_period"], adjust=False, min_periods=p["ema_slow_period"]).mean()

        delta = out["close"].diff()
        avg_gain = wilders_smooth(delta.clip(lower=0), p["rsi_period"])
        avg_loss = wilders_smooth(-delta.clip(upper=0), p["rsi_period"])
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        macd_fast_ema = out["close"].ewm(span=p["macd_fast_period"], adjust=False).mean()
        macd_slow_ema = out["close"].ewm(span=p["macd_slow_period"], adjust=False).mean()
        macd_line = macd_fast_ema - macd_slow_ema
        macd_signal = macd_line.ewm(span=p["macd_signal_period"], adjust=False).mean()
        macd_hist = macd_line - macd_signal

        bull_score = (
            (ema_fast > ema_slow).astype(int)
            + (out["close"] > ema_fast).astype(int)
            + (rsi > 50).astype(int)
            + (macd_line > macd_signal).astype(int)
            + (macd_hist > 0).astype(int)
        )
        bear_score = 5 - bull_score

        out["trend_confluence_bull_score"] = bull_score
        out["trend_confluence_bear_score"] = bear_score
        out["trend_confluence_bullish"] = bull_score >= p["bullish_threshold"]
        out["trend_confluence_bearish"] = bear_score >= p["bearish_threshold"]
        return out
