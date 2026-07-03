"""
Shared math helpers reused across several indicators (Wilder's
smoothing, true range, and the directional-movement building blocks
behind ADX/ADXR/DX/+DI/-DI/+DM/-DM). Not a registered indicator itself
-- same role as app.utils.sessions for strategies.
"""

import numpy as np
import pandas as pd


def wilders_smooth(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def directional_movement(df: pd.DataFrame, period: int) -> dict[str, pd.Series]:
    up_move = df["high"].diff()
    down_move = -df["low"].diff()

    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)

    tr = true_range(df)
    smoothed_tr = wilders_smooth(tr, period)
    smoothed_plus_dm = wilders_smooth(plus_dm, period)
    smoothed_minus_dm = wilders_smooth(minus_dm, period)

    plus_di = 100 * smoothed_plus_dm / smoothed_tr.replace(0, np.nan)
    minus_di = 100 * smoothed_minus_dm / smoothed_tr.replace(0, np.nan)

    return {
        "plus_di": plus_di,
        "minus_di": minus_di,
        "plus_dm": smoothed_plus_dm,
        "minus_dm": smoothed_minus_dm,
        "tr": tr,
    }
