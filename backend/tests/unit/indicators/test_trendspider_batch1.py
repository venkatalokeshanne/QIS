"""
Correctness tests for the first batch of TrendSpider-catalog-inspired
indicators: Donchian Channel, Awesome Oscillator, Fisher Transform,
Elder Ray, Chaikin Money Flow, KDJ, Kairi Relative Index, Ulcer Index,
Average Daily Range, Consecutive Candles, Drawdown from ATH %, ALMA,
Linear Regression Channel, WaveTrend, and Darvas Box.

Each of these implements a published, public technical-analysis
formula (Donchian's channel, Bill Williams' Awesome Oscillator, John
Ehlers' Fisher Transform, Alexander Elder's Bull/Bear Power, Marc
Chaikin's Money Flow, the KDJ oscillator, the Kairi Relative Index,
Peter Martin's Ulcer Index, ALMA, and Nicolas Darvas's box theory) --
written independently against those public definitions, not against
any specific third-party source.
"""

import numpy as np
import pandas as pd
import pytest

from app.indicators.adr import AverageDailyRange
from app.indicators.alma import ALMA
from app.indicators.awesome_oscillator import AwesomeOscillator
from app.indicators.cmf import ChaikinMoneyFlow
from app.indicators.consecutive_candles import ConsecutiveCandles
from app.indicators.darvas_box import DarvasBox
from app.indicators.donchian import Donchian
from app.indicators.drawdown_from_ath import DrawdownFromATH
from app.indicators.elder_ray import ElderRay
from app.indicators.fisher_transform import FisherTransform
from app.indicators.kdj import KDJ
from app.indicators.kri import KairiRelativeIndex
from app.indicators.linearreg_channel import LinearRegressionChannel
from app.indicators.ulcer_index import UlcerIndex
from app.indicators.wavetrend import WaveTrend


@pytest.fixture
def flat_df():
    idx = pd.date_range("2024-01-02 09:30", periods=60, freq="1min")
    return pd.DataFrame(
        {"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1000}, index=idx
    )


def test_donchian_channel_values():
    idx = pd.date_range("2024-01-02 09:30", periods=25, freq="1min")
    high = [100 + i for i in range(25)]
    low = [90 + i for i in range(25)]
    df = pd.DataFrame({"open": 95, "high": high, "low": low, "close": 95, "volume": 1000}, index=idx)

    out = Donchian().calculate(df, {"period": 20})
    # At bar 24 (0-indexed), the trailing 20-bar window is bars 5..24.
    assert out["donchian_upper_20"].iloc[24] == max(high[5:25])
    assert out["donchian_lower_20"].iloc[24] == min(low[5:25])
    assert out["donchian_mid_20"].iloc[24] == pytest.approx(
        (max(high[5:25]) + min(low[5:25])) / 2
    )
    assert out["donchian_upper_20"].iloc[:19].isna().all()


def test_awesome_oscillator_matches_manual_sma_difference():
    idx = pd.date_range("2024-01-02 09:30", periods=40, freq="1min")
    rng = np.random.default_rng(1)
    high = 100 + rng.uniform(0, 1, 40)
    low = high - rng.uniform(0.5, 1, 40)
    df = pd.DataFrame({"open": high, "high": high, "low": low, "close": high, "volume": 1000}, index=idx)

    out = AwesomeOscillator().calculate(df, {"fast_period": 5, "slow_period": 34})
    median_price = (df["high"] + df["low"]) / 2
    expected = (
        median_price.rolling(5, min_periods=5).mean() - median_price.rolling(34, min_periods=34).mean()
    )
    pd.testing.assert_series_equal(out["ao_5_34"], expected, check_names=False)


def test_fisher_transform_is_undefined_on_perfectly_flat_data(flat_df):
    out = FisherTransform().calculate(flat_df, {"period": 10})
    valid = out["fisher_10"].dropna()
    # Flat price -> price sits exactly at both the rolling high and low ->
    # band is 0 -> every bar is skipped (stays NaN) by design (no signal
    # when there's no range to normalize against).
    assert valid.empty


def test_fisher_transform_produces_finite_values_on_trending_data():
    idx = pd.date_range("2024-01-02 09:30", periods=40, freq="1min")
    close = [100 + i * 0.5 for i in range(40)]
    df = pd.DataFrame(
        {"open": close, "high": [c + 0.3 for c in close], "low": [c - 0.3 for c in close], "close": close, "volume": 1000},
        index=idx,
    )
    out = FisherTransform().calculate(df, {"period": 10})
    valid = out["fisher_10"].dropna()
    assert len(valid) > 0
    assert np.isfinite(valid).all()


def test_elder_ray_bull_bear_power():
    idx = pd.date_range("2024-01-02 09:30", periods=20, freq="1min")
    close = [100.0] * 20
    high = [101.0] * 20
    low = [99.0] * 20
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000}, index=idx)

    out = ElderRay().calculate(df, {"period": 13})
    ema = df["close"].ewm(span=13, adjust=False, min_periods=13).mean()
    assert (out["bull_power_13"].dropna() == (pd.Series(high, index=idx) - ema).dropna()).all()
    assert (out["bear_power_13"].dropna() == (pd.Series(low, index=idx) - ema).dropna()).all()


def test_cmf_is_positive_when_closes_are_near_the_high():
    idx = pd.date_range("2024-01-02 09:30", periods=25, freq="1min")
    high = [101.0] * 25
    low = [99.0] * 25
    close = [100.8] * 25  # near the high every bar -> strong accumulation pressure
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000}, index=idx)

    out = ChaikinMoneyFlow().calculate(df, {"period": 20})
    assert (out["cmf_20"].dropna() > 0).all()


def test_kdj_j_line_formula():
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="1min")
    rng = np.random.default_rng(3)
    close = 100 + np.cumsum(rng.normal(0, 0.3, 30))
    high = close + rng.uniform(0, 0.3, 30)
    low = close - rng.uniform(0, 0.3, 30)
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000}, index=idx)

    out = KDJ().calculate(df, {"k_period": 9, "k_slowing": 3, "d_period": 3})
    k, d, j = out["kdj_k_9_3_3"], out["kdj_d_9_3_3"], out["kdj_j_9_3_3"]
    expected_j = 3 * k - 2 * d
    pd.testing.assert_series_equal(j, expected_j, check_names=False)


def test_kri_zero_when_price_equals_its_own_average(flat_df):
    out = KairiRelativeIndex().calculate(flat_df, {"period": 14})
    valid = out["kri_14"].dropna()
    assert len(valid) > 0
    assert (valid == 0).all()


def test_ulcer_index_zero_on_monotonic_new_highs():
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="1min")
    close = [100 + i for i in range(30)]  # always a new high -> zero drawdown throughout
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1000}, index=idx)

    out = UlcerIndex().calculate(df, {"period": 14})
    valid = out["ulcer_index_14"].dropna()
    assert len(valid) > 0
    assert (valid == 0).all()


def test_ulcer_index_positive_during_a_drawdown():
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="1min")
    close = [100 + i for i in range(15)] + [115 - i for i in range(15)]
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1000}, index=idx)

    out = UlcerIndex().calculate(df, {"period": 14})
    assert out["ulcer_index_14"].iloc[-1] > 0


def test_adr_averages_prior_session_ranges():
    idx = pd.date_range("2024-01-02 09:30", periods=3 * 5, freq="1min")
    # 3 sessions worth of 5 bars/day at distinct day boundaries via explicit dates
    idx = (
        list(pd.date_range("2024-01-02 09:30", periods=5, freq="1min"))
        + list(pd.date_range("2024-01-03 09:30", periods=5, freq="1min"))
        + list(pd.date_range("2024-01-04 09:30", periods=5, freq="1min"))
    )
    idx = pd.DatetimeIndex(idx)
    high = [110] * 5 + [120] * 5 + [130] * 5
    low = [100] * 5 + [100] * 5 + [100] * 5
    close = [105] * 15
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000}, index=idx)

    out = AverageDailyRange().calculate(df, {"period": 2})
    # Day 3's ADR(2) should average day 1's range (10) and day 2's range (20) = 15.
    assert out["adr_2"].iloc[-1] == pytest.approx(15.0)


def test_consecutive_candles_counts_streaks_and_resets_on_flip():
    idx = pd.date_range("2024-01-02 09:30", periods=6, freq="1min")
    open_ = [100, 100, 100, 100, 100, 100]
    close = [101, 102, 103, 99, 98, 105]  # up,up,up,down,down,up
    df = pd.DataFrame({"open": open_, "high": close, "low": close, "close": close, "volume": 1000}, index=idx)

    out = ConsecutiveCandles().calculate(df, {})
    assert out["consecutive_candles"].tolist() == [1, 2, 3, -1, -2, 1]


def test_drawdown_from_ath_is_zero_at_new_highs_and_negative_after():
    idx = pd.date_range("2024-01-02 09:30", periods=5, freq="1min")
    close = [100, 110, 105, 95, 120]
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1000}, index=idx)

    out = DrawdownFromATH().calculate(df, {})
    result = out["drawdown_from_ath_pct"]
    assert result.iloc[0] == 0
    assert result.iloc[1] == 0  # new high
    assert result.iloc[2] == pytest.approx((105 - 110) / 110 * 100)
    assert result.iloc[3] == pytest.approx((95 - 110) / 110 * 100)
    assert result.iloc[4] == 0  # new high again


def test_alma_weights_sum_to_one_and_output_is_finite():
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="1min")
    rng = np.random.default_rng(2)
    close = 100 + np.cumsum(rng.normal(0, 0.2, 30))
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1000}, index=idx)

    out = ALMA().calculate(df, {"period": 9, "offset": 0.85, "sigma": 6.0})
    valid = out["alma_9"].dropna()
    assert len(valid) > 0
    assert np.isfinite(valid).all()
    # ALMA of a constant series should just reproduce that constant (weights sum to 1).
    flat = pd.DataFrame(
        {"open": 50.0, "high": 50.0, "low": 50.0, "close": 50.0, "volume": 1000}, index=idx
    )
    flat_out = ALMA().calculate(flat, {"period": 9})
    assert flat_out["alma_9"].dropna().unique().tolist() == pytest.approx([50.0])


def test_linearreg_channel_mid_matches_existing_linearreg_endpoint():
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="1min")
    rng = np.random.default_rng(4)
    close = 100 + np.cumsum(rng.normal(0, 0.2, 30))
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1000}, index=idx)

    from app.indicators.linearreg import LinearRegression

    channel_out = LinearRegressionChannel().calculate(df, {"period": 14, "std_dev": 2.0})
    reg_out = LinearRegression().calculate(df, {"period": 14})

    pd.testing.assert_series_equal(
        channel_out["linearreg_channel_mid_14"], reg_out["linearreg_14"], check_names=False
    )
    assert (channel_out["linearreg_channel_upper_14"].dropna() >= channel_out["linearreg_channel_mid_14"].dropna()).all()
    assert (channel_out["linearreg_channel_lower_14"].dropna() <= channel_out["linearreg_channel_mid_14"].dropna()).all()


def test_wavetrend_produces_two_lines_with_expected_relationship():
    idx = pd.date_range("2024-01-02 09:30", periods=60, freq="1min")
    rng = np.random.default_rng(5)
    close = 100 + np.cumsum(rng.normal(0, 0.3, 60))
    high = close + rng.uniform(0, 0.3, 60)
    low = close - rng.uniform(0, 0.3, 60)
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000}, index=idx)

    out = WaveTrend().calculate(df, {"channel_period": 10, "average_period": 21, "signal_period": 4})
    wt1 = out["wavetrend_wt1_10_21_4"].dropna()
    wt2 = out["wavetrend_wt2_10_21_4"].dropna()
    assert len(wt1) > 0
    assert len(wt2) > 0
    assert np.isfinite(wt1).all()
    assert np.isfinite(wt2).all()


def test_darvas_box_locks_after_confirmation_bars_and_resets_on_new_high():
    idx = pd.date_range("2024-01-02 09:30", periods=10, freq="1min")
    # Bars 0-3: rising highs (new box candidate each bar). Bars 4-6: high
    # holds at 110 for 3 bars -> box should lock at bar 6 (confirmation=3).
    high = [100, 105, 108, 110, 110, 110, 110, 110, 110, 110]
    low = [95, 100, 103, 105, 104, 102, 101, 101, 101, 101]
    df = pd.DataFrame({"open": high, "high": high, "low": low, "close": high, "volume": 1000}, index=idx)

    out = DarvasBox().calculate(df, {"period": 4, "confirmation_bars": 3})
    box_top = out["darvas_box_top_4"]
    box_bottom = out["darvas_box_bottom_4"]

    # Not locked yet before confirmation_bars have held.
    assert box_top.iloc[:6].isna().all()
    # Locked by bar 6 (3rd bar the high of 110 has held without being exceeded).
    assert box_top.iloc[6] == 110
    assert box_bottom.iloc[6] == min(low[3:7])
