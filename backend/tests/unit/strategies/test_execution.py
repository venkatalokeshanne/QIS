"""Tests for app.strategies.execution.simulate_trades."""

import pandas as pd
import pytest

from app.domain.interfaces.strategy import TradeDirection
from app.strategies.execution import ExecutionConfig, simulate_trades


def _bars(prices, freq="1min", start="2024-01-02 09:30"):
    idx = pd.date_range(start, periods=len(prices), freq=freq)
    return pd.DataFrame({"close": prices}, index=idx)


def _ohlc(rows, freq="1min", start="2024-01-02 09:30"):
    """rows: list of (open, high, low, close) tuples."""
    idx = pd.date_range(start, periods=len(rows), freq=freq)
    return pd.DataFrame(
        {
            "open": [r[0] for r in rows],
            "high": [r[1] for r in rows],
            "low": [r[2] for r in rows],
            "close": [r[3] for r in rows],
        },
        index=idx,
    )


def test_long_trade_pnl_without_costs():
    df = _bars([100, 101, 102, 103])
    entries = pd.Series([TradeDirection.LONG, None, None, None], index=df.index)
    exits = pd.Series([False, False, True, False], index=df.index)

    trades = simulate_trades(df, entries, exits, ExecutionConfig(quantity=2, force_close_at_session_end=False))

    assert len(trades) == 1
    t = trades[0]
    assert t.direction == TradeDirection.LONG
    assert t.entry_price == 100
    assert t.exit_price == 102
    assert t.pnl == (102 - 100) * 2


def test_short_trade_pnl_without_costs():
    df = _bars([100, 98, 97])
    entries = pd.Series([TradeDirection.SHORT, None, None], index=df.index)
    exits = pd.Series([False, True, False], index=df.index)

    trades = simulate_trades(df, entries, exits, ExecutionConfig(quantity=1, force_close_at_session_end=False))

    assert len(trades) == 1
    assert trades[0].pnl == (100 - 98)


def test_commission_reduces_pnl():
    df = _bars([100, 105])
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, True], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(quantity=1, commission_per_trade=1.5, force_close_at_session_end=False)
    )
    assert trades[0].pnl == (105 - 100) - 1.5


def test_slippage_worsens_fills_for_both_entry_and_exit():
    df = _bars([100, 110])
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, True], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(quantity=1, slippage_pct=0.01, force_close_at_session_end=False)
    )
    t = trades[0]
    assert t.entry_price == 100 * 1.01
    assert t.exit_price == 110 * 0.99


def test_no_new_entry_while_position_open():
    df = _bars([100, 101, 102, 103])
    # Entry signals on bars 0 AND 1 -- the second should be ignored
    # because a position is already open.
    entries = pd.Series([TradeDirection.LONG, TradeDirection.LONG, None, None], index=df.index)
    exits = pd.Series([False, False, False, True], index=df.index)

    trades = simulate_trades(df, entries, exits, ExecutionConfig(force_close_at_session_end=False))
    assert len(trades) == 1
    assert trades[0].entry_price == 100


def test_open_position_force_closed_at_end_of_data():
    df = _bars([100, 101, 102])
    entries = pd.Series([TradeDirection.LONG, None, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(df, entries, exits, ExecutionConfig(force_close_at_session_end=False))
    assert len(trades) == 1
    assert trades[0].exit_reason == "end_of_data"
    assert trades[0].exit_price == 102


def test_direction_filter_long_only_drops_short_entries():
    df = _bars([100, 99, 98, 97])
    entries = pd.Series([TradeDirection.SHORT, None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False, True], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(direction_filter="long_only", force_close_at_session_end=False)
    )
    assert len(trades) == 1
    assert trades[0].direction == TradeDirection.LONG
    assert trades[0].entry_price == 98


def test_direction_filter_short_only_drops_long_entries():
    df = _bars([100, 99, 98, 97])
    entries = pd.Series([TradeDirection.LONG, None, TradeDirection.SHORT, None], index=df.index)
    exits = pd.Series([False, False, False, True], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(direction_filter="short_only", force_close_at_session_end=False)
    )
    assert len(trades) == 1
    assert trades[0].direction == TradeDirection.SHORT
    assert trades[0].entry_price == 98


def test_direction_filter_both_keeps_all_entries():
    df = _bars([100, 99])
    entries = pd.Series([TradeDirection.SHORT, None], index=df.index)
    exits = pd.Series([False, True], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(direction_filter="both", force_close_at_session_end=False)
    )
    assert len(trades) == 1
    assert trades[0].direction == TradeDirection.SHORT


def test_invalid_direction_filter_raises():
    df = _bars([100, 101])
    entries = pd.Series([None, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    with pytest.raises(ValueError):
        simulate_trades(df, entries, exits, ExecutionConfig(direction_filter="sideways"))


def test_forced_session_close_exits_at_last_bar_of_day():
    # Two 1-minute bars in session 1, then a new session starts.
    idx = pd.to_datetime(
        ["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-03 09:30", "2024-01-03 09:31"]
    )
    df = pd.DataFrame({"close": [100, 101, 200, 201]}, index=idx)
    entries = pd.Series([TradeDirection.LONG, None, None, None], index=idx)
    exits = pd.Series([False, False, False, False], index=idx)

    trades = simulate_trades(df, entries, exits, ExecutionConfig(force_close_at_session_end=True))
    assert len(trades) == 1
    assert trades[0].exit_reason == "forced_session_close"
    assert trades[0].exit_time == idx[1]
    assert trades[0].exit_price == 101


# --- Risk management: stop-loss / take-profit / trailing-stop / position sizing ---


def test_atr_period_alone_without_any_multiple_does_not_touch_high_low():
    # Regression guard: a close-only df (no high/low columns) must still work
    # as long as no *_atr_multiple field is set, even if atr_period is set.
    df = _bars([100, 101, 102, 103])
    entries = pd.Series([TradeDirection.LONG, None, None, None], index=df.index)
    exits = pd.Series([False, False, True, False], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(atr_period=5, force_close_at_session_end=False)
    )
    assert len(trades) == 1
    assert trades[0].exit_price == 102


def test_stop_loss_exits_at_stop_price_when_low_breaches_it_long():
    df = _ohlc(
        [
            (100, 101, 99, 100),  # warm-up bar
            (100, 101, 99, 100),  # entry bar: TR=2, atr_2=2
            (100, 101, 97, 100),  # low breaches stop (98)
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(quantity=1, atr_period=2, stop_loss_atr_multiple=1.0, force_close_at_session_end=False),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == 98
    assert trades[0].pnl == -2


def test_stop_loss_exits_at_stop_price_when_high_breaches_it_short():
    df = _ohlc(
        [
            (100, 101, 99, 100),
            (100, 101, 99, 100),  # entry bar: TR=2, atr_2=2
            (100, 103, 99, 100),  # high breaches stop (102)
        ]
    )
    entries = pd.Series([None, TradeDirection.SHORT, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(quantity=1, atr_period=2, stop_loss_atr_multiple=1.0, force_close_at_session_end=False),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == 102
    assert trades[0].pnl == -2


def test_take_profit_exits_at_target_price_when_high_reaches_it_long():
    df = _ohlc(
        [
            (100, 101, 99, 100),
            (100, 101, 99, 100),  # entry bar: TR=2, atr_2=2
            (100, 103, 99, 100),  # high reaches target (102)
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(quantity=1, atr_period=2, take_profit_atr_multiple=1.0, force_close_at_session_end=False),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "take_profit"
    assert trades[0].exit_price == 102
    assert trades[0].pnl == 2


def test_stop_loss_takes_priority_over_take_profit_when_both_hit_same_bar():
    df = _ohlc(
        [
            (100, 101, 99, 100),
            (100, 101, 99, 100),  # entry bar: TR=2, atr_2=2 -> stop=98, target=102
            (100, 103, 97, 100),  # bar range spans both stop and target
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            quantity=1,
            atr_period=2,
            stop_loss_atr_multiple=1.0,
            take_profit_atr_multiple=1.0,
            force_close_at_session_end=False,
        ),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == 98


def test_stop_not_checked_on_entry_bar_itself():
    # Entry bar's own low would breach a (very tight) same-bar-derived stop
    # if checked -- the engine must not check stop/target until the NEXT bar.
    df = _ohlc(
        [
            (50, 50.5, 49.5, 50),  # warm-up
            (50, 50.2, 40, 50),  # entry bar: low=40 would breach stop 49.49 if checked here
            (50, 50.5, 49.6, 50),  # safe bar afterward
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            quantity=1, atr_period=1, stop_loss_atr_multiple=0.05, force_close_at_session_end=False
        ),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "end_of_data"


def test_trailing_stop_ratchets_favorably_and_never_loosens():
    df = _ohlc(
        [
            (100, 100.5, 99.5, 100),  # warm-up
            (100, 100.5, 99.5, 100),  # entry bar: TR=1, atr_1=1 -> trailing distance=3, initial=97
            (103, 104, 102.5, 103),  # uptrend: ratchet trailing to 104-3=101
            (106, 107, 105.5, 106),  # uptrend: ratchet trailing to 107-3=104
            (103, 103.5, 100, 101),  # pullback: candidate 103.5-3=100.5 < 104 -> stays 104; low breaches 104
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None, None, None], index=df.index)
    exits = pd.Series([False, False, False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            quantity=1, atr_period=1, trailing_stop_atr_multiple=3.0, force_close_at_session_end=False
        ),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "trailing_stop"
    assert trades[0].exit_price == 104
    assert trades[0].pnl == 4


def test_risk_per_trade_pct_sizes_quantity_and_uses_fixed_initial_capital():
    df = _ohlc(
        [
            (100, 101, 99, 100),  # warm-up: TR=2
            (100, 101, 99, 100),  # entry 1 (LONG) @100: TR=2, atr_2=2 -> stop_distance=2 -> qty=(10000*0.01)/2=50
            (99, 99, 98, 98),  # TR=2, low=98 breaches stop (98) -> loss of exactly the risked $100
            (98, 99, 97, 98),  # entry 2 (LONG) @98: TR=2, atr_2=2 -> stop_distance=2 -> qty should STILL be 50
            (103, 103.5, 102.5, 103),  # signal exit
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False, False, True], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            capital=10_000,
            atr_period=2,
            stop_loss_atr_multiple=1.0,
            risk_per_trade_pct=0.01,
            force_close_at_session_end=False,
        ),
    )
    assert len(trades) == 2
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].quantity == 50
    assert trades[0].pnl == -100
    # If sizing used running (post-loss) equity instead of fixed initial
    # capital, this would be 49.5, not 50.
    assert trades[1].quantity == 50
    assert trades[1].pnl == 250


def test_risk_per_trade_pct_without_stop_or_trailing_raises_value_error():
    df = _bars([100, 101])
    entries = pd.Series([None, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    with pytest.raises(ValueError):
        simulate_trades(df, entries, exits, ExecutionConfig(risk_per_trade_pct=0.01))


def test_stop_skipped_when_atr_is_nan_during_warmup():
    df = _ohlc(
        [
            (100, 101, 99, 100),
            (100, 101, 99, 100),
            (100, 101, 99, 100),
        ]
    )
    entries = pd.Series([TradeDirection.LONG, None, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        # period=5 needs 5 valid TR observations; this df only has 3 bars,
        # so ATR is NaN for the entire series.
        ExecutionConfig(atr_period=5, stop_loss_atr_multiple=1.0, force_close_at_session_end=False),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "end_of_data"


def test_intrabar_stop_takes_priority_over_forced_session_close_same_bar():
    idx = pd.to_datetime(["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-03 09:30"])
    df = pd.DataFrame(
        {
            "open": [100, 95, 200],
            "high": [101, 96, 201],
            "low": [99, 94, 199],
            "close": [100, 95, 200],
        },
        index=idx,
    )
    entries = pd.Series([TradeDirection.LONG, None, None], index=idx)
    exits = pd.Series([False, False, False], index=idx)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(atr_period=1, stop_loss_atr_multiple=1.0, force_close_at_session_end=True),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_time == idx[1]
    assert trades[0].exit_price == 98


# --- stop_loss_pct: flat percentage stop, independent of ATR ---


def test_stop_loss_pct_exits_at_stop_price_when_low_breaches_it_long():
    df = _ohlc(
        [
            (100, 101, 99, 100),  # entry bar
            (99, 100, 98, 99),  # low (98) breaches 1% stop (99)
        ]
    )
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(quantity=1, stop_loss_pct=0.01, force_close_at_session_end=False)
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == 99
    assert trades[0].pnl == -1


def test_stop_loss_pct_exits_at_stop_price_when_high_breaches_it_short():
    df = _ohlc(
        [
            (100, 101, 99, 100),  # entry bar
            (101, 102, 100, 101),  # high (102) breaches 1% stop (101)
        ]
    )
    entries = pd.Series([TradeDirection.SHORT, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    trades = simulate_trades(
        df, entries, exits, ExecutionConfig(quantity=1, stop_loss_pct=0.01, force_close_at_session_end=False)
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == 101
    assert trades[0].pnl == -1


def test_stop_loss_pct_does_not_require_valid_atr():
    # No high/low needed for the entry-price math itself, but the engine
    # still requires high/low columns whenever any risk field is set
    # (for the intrabar stop check) -- this uses a very short df where
    # ATR would be NaN, proving stop_loss_pct doesn't depend on it.
    df = _ohlc(
        [
            (100, 101, 99, 100),
            (99, 100, 98, 99),
        ]
    )
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(atr_period=14, quantity=1, stop_loss_pct=0.01, force_close_at_session_end=False),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"


def test_stop_loss_pct_takes_precedence_over_stop_loss_atr_multiple():
    df = _ohlc(
        [
            (100, 101, 99, 100),  # warm-up
            (100, 101, 99, 100),  # entry bar: TR=2, atr_2=2 -> ATR-based stop would be 90 (10x multiple)
            (99, 100, 98, 99),  # low (98) breaches the 1% pct stop (99), not the ATR stop
        ]
    )
    entries = pd.Series([None, TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            quantity=1,
            atr_period=2,
            stop_loss_atr_multiple=10.0,
            stop_loss_pct=0.01,
            force_close_at_session_end=False,
        ),
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].exit_price == 99


def test_risk_per_trade_pct_sizes_using_stop_loss_pct():
    df = _ohlc(
        [
            (100, 101, 99, 100),  # entry @100, stop_distance = 100*0.01 = 1 -> qty = (10000*0.01)/1 = 100
            (99, 100, 98, 99),  # low (98) breaches stop (99)
        ]
    )
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            capital=10_000, stop_loss_pct=0.01, risk_per_trade_pct=0.01, force_close_at_session_end=False
        ),
    )
    assert len(trades) == 1
    assert trades[0].quantity == 100
    assert trades[0].pnl == -100


def test_stop_loss_pct_must_be_positive():
    df = _bars([100, 101])
    entries = pd.Series([None, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    with pytest.raises(ValueError):
        simulate_trades(df, entries, exits, ExecutionConfig(stop_loss_pct=0))

def test_max_position_value_pct_caps_fixed_quantity():
    df = _bars([100, 101])
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, True], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            capital=1_000, quantity=10, max_position_value_pct=0.5, force_close_at_session_end=False
        ),
    )
    # Cap: 1000 * 0.5 / 100 = 5 shares, below the configured quantity of 10.
    assert trades[0].quantity == 5


def test_max_position_value_pct_caps_risk_based_sizing():
    # Flat bars so neither the 1% stop nor anything else fires intrabar.
    df = _ohlc([(100, 100, 100, 100), (100, 100, 100, 100)])
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, True], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            capital=100_000,
            risk_per_trade_pct=0.02,
            stop_loss_pct=0.01,
            max_position_value_pct=1.0,
            force_close_at_session_end=False,
        ),
    )
    # Risk sizing alone: (100000 * 0.02) / (100 * 0.01) = 2000 shares =
    # a $200k position on $100k capital. The cap holds it to 1000 shares.
    assert trades[0].quantity == 1000


def test_max_position_value_pct_leaves_smaller_positions_alone():
    df = _bars([100, 101])
    entries = pd.Series([TradeDirection.LONG, None], index=df.index)
    exits = pd.Series([False, True], index=df.index)

    trades = simulate_trades(
        df,
        entries,
        exits,
        ExecutionConfig(
            capital=1_000_000, quantity=10, max_position_value_pct=1.0, force_close_at_session_end=False
        ),
    )
    assert trades[0].quantity == 10


def test_max_position_value_pct_must_be_positive():
    df = _bars([100, 101])
    entries = pd.Series([None, None], index=df.index)
    exits = pd.Series([False, False], index=df.index)

    with pytest.raises(ValueError):
        simulate_trades(df, entries, exits, ExecutionConfig(max_position_value_pct=0))
