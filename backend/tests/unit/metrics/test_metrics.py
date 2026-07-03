"""Correctness tests for individual metrics, using hand-computable trade lists."""

from app.metrics.context import build_context
from app.metrics.net_profit import NetProfit
from app.metrics.win_rate import WinRate
from app.metrics.profit_factor import ProfitFactor
from app.metrics.average_trade import AverageTrade
from app.metrics.expectancy import Expectancy
from app.metrics.max_drawdown import MaxDrawdown
from app.metrics.recovery_factor import RecoveryFactor
from app.metrics.total_trades import TotalTrades
from app.metrics.consecutive_winners import ConsecutiveWinners
from app.metrics.consecutive_losers import ConsecutiveLosers
from app.metrics.average_holding_time import AverageHoldingTime


CAPITAL = 10_000.0


def test_net_profit(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    assert NetProfit().calculate(ctx) == 15.0


def test_net_profit_empty(empty_trades):
    ctx = build_context(empty_trades, CAPITAL)
    assert NetProfit().calculate(ctx) == 0.0


def test_total_trades(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    assert TotalTrades().calculate(ctx) == 5.0


def test_win_rate(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    assert WinRate().calculate(ctx) == 60.0  # 3 of 5


def test_win_rate_undefined_for_no_trades(empty_trades):
    ctx = build_context(empty_trades, CAPITAL)
    assert WinRate().calculate(ctx) is None


def test_profit_factor(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    # gross profit = 10+20+5 = 35, gross loss = 8+12 = 20
    assert ProfitFactor().calculate(ctx) == 35 / 20


def test_profit_factor_undefined_with_no_losses(all_winning_trades):
    ctx = build_context(all_winning_trades, CAPITAL)
    assert ProfitFactor().calculate(ctx) is None


def test_average_trade(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    assert AverageTrade().calculate(ctx) == 15 / 5


def test_expectancy_matches_average_trade_mathematically(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    expectancy = Expectancy().calculate(ctx)
    avg_trade = AverageTrade().calculate(ctx)
    assert round(expectancy, 6) == round(avg_trade, 6)


def test_max_drawdown(mixed_trades):
    # Equity: 10000 -> 10010 -> 10002 -> 10022 -> 10010 -> 10015
    # Peak before worst dip is 10022, trough after is 10010 -> dd = 12/10022*100
    ctx = build_context(mixed_trades, CAPITAL)
    dd = MaxDrawdown().calculate(ctx)
    assert round(dd, 4) == round(12 / 10022 * 100, 4)


def test_max_drawdown_zero_for_single_trade():
    from tests.unit.metrics.conftest import _trade
    ctx = build_context([_trade(50)], CAPITAL)
    assert MaxDrawdown().calculate(ctx) == 0.0


def test_recovery_factor(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    rf = RecoveryFactor().calculate(ctx)
    assert rf == 15 / 12  # net_profit / max_drawdown_abs


def test_recovery_factor_undefined_with_no_drawdown(all_winning_trades):
    ctx = build_context(all_winning_trades, CAPITAL)
    assert RecoveryFactor().calculate(ctx) is None


def test_consecutive_winners_and_losers(mixed_trades):
    # pnl sequence: +10, -8, +20, -12, +5 -> max win streak 1, max loss streak 1
    ctx = build_context(mixed_trades, CAPITAL)
    assert ConsecutiveWinners().calculate(ctx) == 1.0
    assert ConsecutiveLosers().calculate(ctx) == 1.0


def test_consecutive_winners_longer_streak():
    from tests.unit.metrics.conftest import _trade
    trades = [_trade(1), _trade(1), _trade(1), _trade(-1), _trade(1)]
    ctx = build_context(trades, CAPITAL)
    assert ConsecutiveWinners().calculate(ctx) == 3.0


def test_average_holding_time(mixed_trades):
    ctx = build_context(mixed_trades, CAPITAL)
    assert AverageHoldingTime().calculate(ctx) == 5.0  # all trades held 5 min
