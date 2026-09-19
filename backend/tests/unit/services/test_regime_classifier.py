"""Tests for app.services.regime_classifier."""

import numpy as np
import pandas as pd

from app.services.regime_classifier import (
    RegimeLabel,
    classify_regime,
    classify_regime_series,
    combine_market_regime,
    regime_bucket_key,
)


def _daily_bars(closes, start="2024-01-02"):
    closes = np.asarray(closes, dtype=float)
    idx = pd.date_range(start, periods=len(closes), freq="1D")
    return pd.DataFrame(
        {"open": closes, "high": closes * 1.002, "low": closes * 0.998, "close": closes},
        index=idx,
    )


def _trending_bars(n=200, start_price=100.0, step=1.0):
    return _daily_bars(start_price + np.arange(n) * step)


def _choppy_bars(n=200, price=100.0):
    return _daily_bars(price + np.sin(np.arange(n) / 3) * 0.5)


# --- trend classification -------------------------------------------------


def test_classify_regime_trending_on_a_clean_ramp():
    label = classify_regime(_trending_bars())
    assert label is not None
    assert label.trend == "trending"


def test_classify_regime_ranging_on_chop():
    label = classify_regime(_choppy_bars())
    assert label is not None
    assert label.trend == "ranging"


# --- warm-up / edge cases --------------------------------------------------


def test_classify_regime_none_before_warmup():
    label = classify_regime(_trending_bars(n=5))  # far short of vol_lookback=100 default
    assert label is None


def test_classify_regime_none_on_empty_df():
    assert classify_regime(_daily_bars([])) is None


def test_classify_regime_series_last_row_matches_classify_regime():
    df = _trending_bars()
    series = classify_regime_series(df)
    assert series.iloc[-1] == classify_regime(df)


# --- volatility classification ---------------------------------------------


def test_high_vol_detected_after_a_volatility_expansion():
    # A long quiet stretch, then a trailing stretch with a much wider
    # daily range -- against a reference built mostly from the quiet
    # stretch, the trailing days should read as high_vol.
    n_quiet, n_loud = 150, 20
    rng = np.random.RandomState(0)
    quiet_closes = 100 + np.cumsum(rng.normal(0, 0.05, n_quiet))
    loud_closes = quiet_closes[-1] + np.cumsum(rng.normal(0, 3.0, n_loud))
    closes = np.concatenate([quiet_closes, loud_closes])

    high = closes.copy()
    low = closes.copy()
    high[:n_quiet] = closes[:n_quiet] * 1.002
    low[:n_quiet] = closes[:n_quiet] * 0.998
    high[n_quiet:] = closes[n_quiet:] + 4.0
    low[n_quiet:] = closes[n_quiet:] - 4.0

    idx = pd.date_range("2024-01-02", periods=len(closes), freq="1D")
    df = pd.DataFrame({"open": closes, "high": high, "low": low, "close": closes}, index=idx)

    label = classify_regime(df, vol_lookback=100)
    assert label is not None
    assert label.volatility == "high_vol"


# --- combine_market_regime ---------------------------------------------


def test_combine_market_regime_majority_vote():
    labels = [
        RegimeLabel(trend="trending", volatility="high_vol"),
        RegimeLabel(trend="trending", volatility="low_vol"),
        RegimeLabel(trend="ranging", volatility="low_vol"),
    ]
    combined = combine_market_regime(labels)
    assert combined.trend == "trending"  # 2/3
    assert combined.volatility == "low_vol"  # 2/3


def test_combine_market_regime_tie_resolves_to_less_committal_label():
    labels = [
        RegimeLabel(trend="trending", volatility="high_vol"),
        RegimeLabel(trend="ranging", volatility="low_vol"),
    ]
    combined = combine_market_regime(labels)
    assert combined.trend == "ranging"
    assert combined.volatility == "low_vol"


def test_combine_market_regime_ignores_unclassifiable_proxies():
    only_one = combine_market_regime([None, RegimeLabel(trend="trending", volatility="high_vol")])
    assert only_one == RegimeLabel(trend="trending", volatility="high_vol")


def test_combine_market_regime_none_when_nothing_classifiable():
    assert combine_market_regime([None, None]) is None
    assert combine_market_regime([]) is None


# --- regime_bucket_key ---------------------------------------------


def test_regime_bucket_key_format():
    key = regime_bucket_key(
        RegimeLabel(trend="trending", volatility="high_vol"),
        RegimeLabel(trend="ranging", volatility="low_vol"),
    )
    assert key == "ticker=trending/high_vol|market=ranging/low_vol"


def test_regime_label_key_property():
    assert RegimeLabel(trend="trending", volatility="high_vol").key == "trending/high_vol"
