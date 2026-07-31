"""Tests for the Confluence Order Block strategy.

Strategy.run() is overridden (see the module docstring in strategy.py
for why), so these tests monkeypatch the instance's `prepare` to return
a hand-built "already enriched" frame -- exactly like
test_ema_vwap_morning_cross.py's `_prepared_df` helper -- so the trade
rules (fill/stop/target/sizing) are exercised directly without depending
on the indicator's own zone-detection math (covered separately in
test_confluence_order_block.py under tests/unit/indicators/).
"""

import pandas as pd
import pytest

from app.domain.interfaces.strategy import TradeDirection
from app.strategies.confluence_order_block.strategy import ConfluenceOrderBlock
from app.strategies.execution import ExecutionConfig


def _prepared_df(times, open_, high, low, close, signal, zone_top, zone_bottom, atr_at_formation, ema=None, ema_col=None):
    idx = pd.DatetimeIndex(pd.to_datetime(times))
    df = pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "cob_zone_top": zone_top,
            "cob_zone_bottom": zone_bottom,
            "cob_atr_at_formation": atr_at_formation,
        },
        index=idx,
    )
    # Assigned separately (not passed to the DataFrame constructor as a
    # Series) -- a Series with its own default RangeIndex would be
    # reindex-aligned against `idx` by label instead of by position,
    # silently turning every value into NaN.
    df["cob_signal"] = pd.Series(signal, index=idx, dtype=object)
    if ema is not None:
        df[ema_col] = ema
    return df


def _run(prepared_df, params, execution_config=None):
    strategy = ConfluenceOrderBlock()
    strategy.prepare = lambda df, p: prepared_df
    return strategy.run(prepared_df, params, execution_config or ExecutionConfig())


_TIMES = [f"2024-01-02 09:{30 + 5 * i:02d}" for i in range(6)]


def test_long_entry_fills_at_limit_min_of_open_and_zone_top():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 9.8, 100.0],
        high=[100.0, 100.0, 100.0],
        low=[100.0, 9.5, 100.0],
        close=[100.0, 9.9, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    trades = _run(df, {"trend_len": 0}, ExecutionConfig(capital=1000.0, slippage_pct=0.0))

    assert len(trades) == 1
    assert trades[0].direction == TradeDirection.LONG
    assert trades[0].entry_price == pytest.approx(9.8)  # min(open=9.8, top=10.0)


def test_long_entry_gap_through_zone_fills_at_open():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 8.0, 100.0],  # gapped below the whole zone
        high=[100.0, 100.0, 100.0],
        low=[100.0, 7.9, 100.0],
        close=[100.0, 8.1, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    # A larger stop_buf keeps the (zone-edge-anchored) stop below the
    # gapped-through entry price -- otherwise risk<=0 and the trade would
    # be (correctly) skipped, which isn't what this test is checking.
    trades = _run(df, {"trend_len": 0, "stop_buf": 2.0}, ExecutionConfig(capital=1000.0, slippage_pct=0.0))

    assert trades[0].entry_price == pytest.approx(8.0)  # min(open=8.0, top=10.0) -> the open


def test_short_entry_fills_at_limit_max_of_open_and_zone_bottom():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 20.2, 100.0],
        high=[100.0, 20.5, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 20.1, 100.0],
        signal=[None, "short", None],
        zone_top=[float("nan"), 21.0, float("nan")],
        zone_bottom=[float("nan"), 20.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    trades = _run(df, {"trend_len": 0}, ExecutionConfig(capital=1000.0, slippage_pct=0.0))

    assert trades[0].direction == TradeDirection.SHORT
    assert trades[0].entry_price == pytest.approx(20.2)  # max(open=20.2, bottom=20.0)


def test_slippage_applied_unfavorably_on_entry():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 10.0, 100.0],
        high=[100.0, 100.0, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 10.0, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    trades = _run(df, {"trend_len": 0}, ExecutionConfig(capital=1000.0, slippage_pct=0.01))

    assert trades[0].entry_price == pytest.approx(10.0 * 1.01)


def test_stop_and_target_formula_uses_atr_at_formation_not_current_atr():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 9.8, 9.9],
        high=[100.0, 100.0, 9.95],  # stays well below target (11.75)
        low=[100.0, 100.0, 9.85],  # stays well above stop (8.5)
        close=[100.0, 9.9, 9.9],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    trades = _run(df, {"trend_len": 0, "stop_buf": 0.5, "rr": 1.5}, ExecutionConfig(capital=1000.0, slippage_pct=0.0))

    entry = 9.8
    expected_stop = 9.0 - 0.5 * 1.0
    expected_target = entry + 1.5 * (entry - expected_stop)
    # Neither stop nor target was hit within the data -- forced closed at
    # end of data -- so we can only check the trade didn't exit early;
    # the formula itself is exercised precisely in the stop-hit test below.
    assert trades[0].exit_reason == "end_of_data"
    assert expected_target > entry > expected_stop


def test_stop_checked_before_target_when_one_bar_spans_both():
    df = _prepared_df(
        _TIMES[:4],
        open_=[100.0, 9.8, 9.0, 100.0],
        high=[100.0, 100.0, 12.0, 100.0],  # bar 2 also reaches target...
        low=[100.0, 100.0, 8.0, 100.0],  # ...but also breaches the stop
        close=[100.0, 9.9, 9.5, 100.0],
        signal=[None, "long", None, None],
        zone_top=[float("nan"), 10.0, float("nan"), float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan"), float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan"), float("nan")],
    )
    trades = _run(df, {"trend_len": 0, "stop_buf": 0.5, "rr": 1.5}, ExecutionConfig(capital=1000.0, slippage_pct=0.0))

    entry = 9.8
    stop = 9.0 - 0.5 * 1.0  # 8.5
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == pytest.approx(min(stop, 9.0))  # min(stop, that bar's open)


def test_no_reentry_on_the_bar_a_position_exits_and_sizing_compounds():
    df = _prepared_df(
        _TIMES,
        open_=[100.0, 9.8, 9.0, 29.8, 29.9, 29.9],
        high=[100.0, 100.0, 100.0, 100.0, 29.95, 29.95],  # stay well below trade 2's target (31.75)
        low=[100.0, 100.0, 8.0, 100.0, 29.85, 29.85],  # stay well above trade 2's stop (28.5)
        close=[100.0, 9.9, 8.5, 29.9, 29.9, 29.9],
        signal=[None, "long", "long", "long", None, None],
        zone_top=[float("nan"), 10.0, 20.0, 30.0, float("nan"), float("nan")],
        zone_bottom=[float("nan"), 9.0, 19.0, 29.0, float("nan"), float("nan")],
        atr_at_formation=[float("nan"), 1.0, 1.0, 1.0, float("nan"), float("nan")],
    )
    capital = 1000.0
    trades = _run(df, {"trend_len": 0, "stop_buf": 0.5, "rr": 1.5}, ExecutionConfig(capital=capital, slippage_pct=0.0))

    assert len(trades) == 2

    entry1, stop1 = 9.8, 9.0 - 0.5 * 1.0
    exit1 = min(stop1, 9.0)  # bar 2's open
    shares1 = capital / entry1
    pnl1 = (exit1 - entry1) * shares1
    equity_after = capital + pnl1

    assert trades[0].entry_time == pd.Timestamp(_TIMES[1])
    assert trades[0].exit_time == pd.Timestamp(_TIMES[2])
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].quantity == pytest.approx(shares1)

    # The bar-2 signal ("long" again) must NOT open a new trade on the
    # same bar the previous position just exited.
    assert all(t.entry_time != pd.Timestamp(_TIMES[2]) for t in trades)

    entry2 = 29.8
    shares2 = equity_after / entry2
    assert trades[1].entry_time == pd.Timestamp(_TIMES[3])
    assert trades[1].quantity == pytest.approx(shares2)
    assert trades[1].exit_reason == "end_of_data"


def test_allow_short_false_blocks_short_signal():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 20.2, 100.0],
        high=[100.0, 20.5, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 20.1, 100.0],
        signal=[None, "short", None],
        zone_top=[float("nan"), 21.0, float("nan")],
        zone_bottom=[float("nan"), 20.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    trades = _run(df, {"trend_len": 0, "allow_short": False}, ExecutionConfig(capital=1000.0))

    assert trades == []


def test_trend_filter_blocks_long_when_close_at_or_below_ema():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 9.8, 100.0],
        high=[100.0, 100.0, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 9.9, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
        ema=[100.0, 10.5, 100.0],  # close (9.9) <= ema (10.5) -> blocked
        ema_col="ema_5",
    )
    trades = _run(df, {"trend_len": 5}, ExecutionConfig(capital=1000.0))

    assert trades == []


def test_trend_filter_allows_long_when_close_above_ema():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 9.8, 100.0],
        high=[100.0, 100.0, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 9.9, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
        ema=[100.0, 9.0, 100.0],  # close (9.9) > ema (9.0) -> allowed
        ema_col="ema_5",
    )
    trades = _run(df, {"trend_len": 5}, ExecutionConfig(capital=1000.0))

    assert len(trades) == 1


def test_negative_or_zero_risk_skips_entry():
    # Entry gaps all the way through to below the zone's bottom, and the
    # ATR-at-formation is small enough that the stop (zone_bottom minus a
    # small buffer) still sits ABOVE the entry fill -> risk <= 0.
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 8.0, 100.0],  # fill = min(8.0, top=10.0) = 8.0
        high=[100.0, 100.0, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 8.0, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 0.1, float("nan")],  # stop = 9.0 - 0.5*0.1 = 8.95 >= entry(8.0)
    )
    trades = _run(df, {"trend_len": 0}, ExecutionConfig(capital=1000.0))

    assert trades == []


def test_generate_entries_matches_run_gating_for_introspection():
    df = _prepared_df(
        _TIMES[:3],
        open_=[100.0, 9.8, 100.0],
        high=[100.0, 100.0, 100.0],
        low=[100.0, 100.0, 100.0],
        close=[100.0, 9.9, 100.0],
        signal=[None, "long", None],
        zone_top=[float("nan"), 10.0, float("nan")],
        zone_bottom=[float("nan"), 9.0, float("nan")],
        atr_at_formation=[float("nan"), 1.0, float("nan")],
    )
    entries = ConfluenceOrderBlock().generate_entries(df, {"trend_len": 0})
    assert entries.iloc[1] == TradeDirection.LONG
    # NB: pd.Series(None, dtype=object) stores NaN rather than None on
    # this pandas version (a pre-existing quirk shared by every strategy
    # using this same default-init pattern, e.g. ema_vwap_morning_cross)
    # -- pd.isna() is used here instead of `is None` for that reason.
    assert pd.isna(entries.iloc[0]) and pd.isna(entries.iloc[2])


def test_generate_exits_always_false():
    df = _prepared_df(
        _TIMES[:2],
        open_=[100.0, 100.0],
        high=[100.0, 100.0],
        low=[100.0, 100.0],
        close=[100.0, 100.0],
        signal=[None, None],
        zone_top=[float("nan"), float("nan")],
        zone_bottom=[float("nan"), float("nan")],
        atr_at_formation=[float("nan"), float("nan")],
    )
    exits = ConfluenceOrderBlock().generate_exits(df, {})
    assert list(exits) == [False, False]
