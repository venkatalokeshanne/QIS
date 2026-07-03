"""Shared fixtures for indicator/filter/strategy tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """
    Two synthetic trading sessions of 1-minute bars (09:30-10:00),
    enough to exercise rolling windows, session resets (VWAP, Opening
    Range), and basic trend behavior.
    """
    rng = np.random.default_rng(seed=42)
    sessions = []
    for day in ["2024-01-02", "2024-01-03"]:
        idx = pd.date_range(f"{day} 09:30", f"{day} 10:00", freq="1min")
        n = len(idx)
        close = 100 + np.cumsum(rng.normal(0, 0.1, n))
        high = close + rng.uniform(0, 0.2, n)
        low = close - rng.uniform(0, 0.2, n)
        open_ = close + rng.normal(0, 0.05, n)
        volume = rng.integers(100, 1000, n)
        sessions.append(
            pd.DataFrame(
                {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
                index=idx,
            )
        )
    return pd.concat(sessions)
