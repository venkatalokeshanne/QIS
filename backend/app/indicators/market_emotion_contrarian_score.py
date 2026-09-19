"""
Market Emotion Contrarian Score.

A weighted composite "emotion" reading (0-100) blending a longer-cycle
RSI, a short-cycle RSI, an EMA-smoothed Stochastic-of-RSI (compressed
so only its own extremes count -- middling readings all collapse to
neutral), and price's own %-deviation from a short EMA. High readings
(> fomo_threshold) mean crowd euphoria; low readings (< panic_threshold)
mean crowd despair -- both read as CONTRARIAN setups once the extreme
fades back toward neutral, tracked via a small state machine (armed on
entering an extreme, fires once emotion decays back out of it, resets
once it settles into the neutral band).

The source script's long-cycle RSI is fetched from an explicit weekly
timeframe; computed here on whatever timeframe this is given instead
via a proportionally longer RSI period, since there's no
second-timeframe fetch available from within an Indicator (see
app.indicators.period_high_low for the same reduction pattern).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


@indicator_registry.register("market_emotion_contrarian_score")
class MarketEmotionContrarianScore(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="market_emotion_contrarian_score",
            display_name="Market Emotion Contrarian Score",
            description="Weighted composite 0-100 crowd-emotion reading (long/short RSI, stoch-RSI extremes, EMA deviation); flags a contrarian setup once an extreme reading fades back toward neutral.",
            category="momentum",
            default_params={
                "short_rsi_period": 14,
                "long_rsi_period": 98,
                "stoch_period": 14,
                "stoch_smooth": 3,
                "ema_period": 20,
                "fomo_threshold": 75.0,
                "panic_threshold": 25.0,
                "neutral_low": 35.0,
                "neutral_high": 65.0,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        rsi_short = _rsi(out["close"], p["short_rsi_period"])
        rsi_long = _rsi(out["close"], p["long_rsi_period"])

        low_r = rsi_short.rolling(p["stoch_period"], min_periods=p["stoch_period"]).min()
        high_r = rsi_short.rolling(p["stoch_period"], min_periods=p["stoch_period"]).max()
        stoch_rsi = (rsi_short - low_r) / (high_r - low_r).replace(0, np.nan) * 100
        sk = stoch_rsi.ewm(span=p["stoch_smooth"], adjust=False, min_periods=p["stoch_smooth"]).mean()
        sk_norm = pd.Series(np.where(sk > 90, 100.0, np.where(sk < 10, 0.0, 50.0)), index=out.index)

        ema = out["close"].ewm(span=p["ema_period"], adjust=False, min_periods=p["ema_period"]).mean()
        dev = ((out["close"] - ema) / ema * 500 + 50).clip(lower=0, upper=100)

        emotion = (rsi_long * 0.40) + (rsi_short * 0.25) + (sk_norm * 0.25) + (dev * 0.10)

        fomo_th, panic_th = p["fomo_threshold"], p["panic_threshold"]
        neutral_lo, neutral_hi = p["neutral_low"], p["neutral_high"]
        emotion_arr = emotion.to_numpy()
        n = len(out)
        sell_signal = np.zeros(n, dtype=bool)
        buy_signal = np.zeros(n, dtype=bool)

        state = 0  # 0=idle, 1=armed-fomo, 2=armed-panic, 3=cooldown
        for i in range(n):
            e = emotion_arr[i]
            if np.isnan(e):
                continue
            in_fomo = e > fomo_th
            in_panic = e < panic_th
            in_neutral = neutral_lo <= e <= neutral_hi

            if state == 0 and in_fomo:
                state = 1
            elif state == 0 and in_panic:
                state = 2

            if state == 1 and not in_fomo:
                sell_signal[i] = True
                state = 3
            elif state == 2 and not in_panic:
                buy_signal[i] = True
                state = 3

            if state == 3 and in_neutral:
                state = 0

        out["market_emotion_score"] = emotion
        out["market_emotion_sell_signal"] = sell_signal
        out["market_emotion_buy_signal"] = buy_signal
        return out
