import numpy as np
import pandas as pd
import pytest

from app.services import market_light_service as ml


def _bars(closes) -> pd.DataFrame:
    c = pd.Series(closes, dtype=float)
    idx = pd.date_range("2025-01-01", periods=len(c), freq="D", tz="UTC")
    return pd.DataFrame({"open": c.values, "high": c.values * 1.005, "low": c.values * 0.995,
                         "close": c.values, "volume": 1e6}, index=idx)


def test_steady_uptrend_is_green():
    assert ml.classify(_bars(np.linspace(100, 160, 120)))["light"].iloc[-1] == ml.GREEN


def test_steady_downtrend_is_red():
    assert ml.classify(_bars(np.linspace(160, 100, 120)))["light"].iloc[-1] == ml.RED


def test_flat_market_is_yellow():
    closes = 100 + np.sin(np.arange(120) / 2) * 0.3
    assert ml.classify(_bars(closes))["light"].iloc[-1] == ml.YELLOW


def test_price_below_a_still_rising_average_is_yellow():
    # Long uptrend, then one close just under the 21 EMA: the average is
    # still rising, so the rules call it conflicting, not red.
    closes = list(np.linspace(100, 160, 120)) + [154]
    row = ml.classify(_bars(closes)).iloc[-1]
    assert row["close"] < row["ema21"] and row["slope_atr"] > ml.FLAT_ATR
    assert row["light"] == ml.YELLOW


def test_light_is_point_in_time():
    closes = list(np.linspace(100, 160, 100)) + list(np.linspace(160, 110, 40))
    full = ml.classify(_bars(closes))["light"]
    for cut in (60, 100, 120):
        truncated = ml.classify(_bars(closes[:cut]))["light"]
        pd.testing.assert_series_equal(truncated, full.iloc[:cut], check_names=False)


@pytest.mark.parametrize("lights,expected", [
    (["green", "green", "green"], "green"),
    (["green", "green", "yellow"], "green"),
    (["red", "red", "yellow"], "red"),
    (["green", "red", "yellow"], "yellow"),
    (["green", "green", "red"], "yellow"),
    (["yellow", "yellow", "green"], "yellow"),
])
def test_composite(lights, expected):
    assert ml.composite(lights)[0] == expected


def test_get_market_light_end_to_end_with_injected_bars():
    series = {"SPY": np.linspace(400, 480, 200), "QQQ": np.linspace(300, 380, 200), "IWM": np.linspace(220, 180, 200)}

    def fake_fetch(symbol, interval, outputsize):
        b = _bars(series[symbol])
        return b.reset_index().rename(columns={"index": "date"})

    out = ml.get_market_light("1D", fetch_bars=fake_fetch)
    assert [i["light"] for i in out["indices"]] == ["green", "green", "red"]
    assert out["light"] == "yellow"                      # green and red disagree
    assert len(out["history"]) == ml.HISTORY_BARS
    assert out["indices"][0]["stats"]["green"]["bars"] > 0


def test_unknown_timeframe_rejected():
    with pytest.raises(Exception):
        ml.get_market_light("4h", fetch_bars=lambda *a, **k: None)
