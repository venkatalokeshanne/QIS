"""
Indicator math used by the regime detectors.

Deliberately small and explicit: each value at bar t uses only bars <= t
(no centered windows), so a regime computed "as of" a bar never sees the
future. Swing points are the one place where confirmation needs later
bars -- `confirmed_swings` returns them at the bar they become KNOWN.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev = df["close"].shift(1)
    return pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1).max(axis=1)


def wilder(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    return wilder(true_range(df), n)


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    tr = wilder(true_range(df), n)
    plus_di = 100 * wilder(plus_dm, n) / tr
    minus_di = 100 * wilder(minus_dm, n) / tr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return wilder(dx, n)


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    gain = wilder(d.clip(lower=0), n)
    loss = wilder((-d).clip(lower=0), n)
    return 100 - 100 / (1 + gain / loss.replace(0, np.nan))


def roc(s: pd.Series, n: int) -> pd.Series:
    return s / s.shift(n) - 1


def macd(s: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(s, fast) - ema(s, slow)
    sig = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def realized_vol(close: pd.Series, n: int = 20, periods_per_year: int = 252) -> pd.Series:
    r = np.log(close / close.shift(1))
    return r.rolling(n, min_periods=n).std() * np.sqrt(periods_per_year)


def trailing_percentile(s: pd.Series, window: int) -> pd.Series:
    """Percentile rank (0..1) of each value within its own trailing window
    (current value included) -- the value's position in its OWN history."""
    def rank(w: np.ndarray) -> float:
        cur = w[-1]
        w = w[~np.isnan(w)]
        if len(w) < 2 or np.isnan(cur):
            return np.nan
        return float((w < cur).sum() + 0.5 * ((w == cur).sum() - 1)) / (len(w) - 1)

    return s.rolling(window, min_periods=max(20, window // 4)).apply(rank, raw=True)


def classify_percentile(p: float, cuts: list[float], labels: list[str]) -> str | None:
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return None
    for cut, label in zip(cuts, labels):
        if p < cut:
            return label
    return labels[-1]


def confirmed_swings(df: pd.DataFrame, k: int) -> tuple[list[tuple[int, int, float]], list[tuple[int, int, float]]]:
    """Swing highs/lows as (known_at_position, swing_position, price).

    A swing high at i is a bar whose high is the max of i-k..i+k; it is only
    KNOWN at i+k. Consumers must only use swings with known_at <= t.
    """
    h, l = df["high"].to_numpy(), df["low"].to_numpy()
    highs, lows = [], []
    for i in range(k, len(df) - k):
        win_h, win_l = h[i - k:i + k + 1], l[i - k:i + k + 1]
        if h[i] == win_h.max() and (win_h == h[i]).sum() == 1:
            highs.append((i + k, i, float(h[i])))
        if l[i] == win_l.min() and (win_l == l[i]).sum() == 1:
            lows.append((i + k, i, float(l[i])))
    return highs, lows


def structure_series(df: pd.DataFrame, k: int, swings: int = 2) -> pd.Series:
    """Per bar: BULLISH (higher highs AND higher lows), BEARISH (lower highs
    AND lower lows) or MIXED, from the last `swings` swing points confirmed
    by that bar. None until enough swings are known."""
    highs, lows = confirmed_swings(df, k)
    out = [None] * len(df)
    hi_ptr = lo_ptr = 0
    known_h: list[float] = []
    known_l: list[float] = []
    for t in range(len(df)):
        while hi_ptr < len(highs) and highs[hi_ptr][0] <= t:
            known_h.append(highs[hi_ptr][2])
            hi_ptr += 1
        while lo_ptr < len(lows) and lows[lo_ptr][0] <= t:
            known_l.append(lows[lo_ptr][2])
            lo_ptr += 1
        if len(known_h) < swings or len(known_l) < swings:
            continue
        hs, ls = known_h[-swings:], known_l[-swings:]
        higher_h = all(b > a for a, b in zip(hs, hs[1:]))
        higher_l = all(b > a for a, b in zip(ls, ls[1:]))
        lower_h = all(b < a for a, b in zip(hs, hs[1:]))
        lower_l = all(b < a for a, b in zip(ls, ls[1:]))
        out[t] = "BULLISH" if (higher_h and higher_l) else "BEARISH" if (lower_h and lower_l) else "MIXED"
    return pd.Series(out, index=df.index, dtype=object)


def persist(raw: pd.Series, n: int) -> pd.Series:
    """Regime persistence: the label only changes after `n` consecutive
    observations of a new raw label. Missing raw values keep the state."""
    out, state, cand, run = [], None, None, 0
    for v in raw:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            out.append(state)
            continue
        if state is None:
            state = v
        elif v == state:
            cand, run = None, 0
        else:
            if v == cand:
                run += 1
            else:
                cand, run = v, 1
            if run >= n:
                state, cand, run = v, None, 0
        out.append(state)
    return pd.Series(out, index=raw.index, dtype=object)
