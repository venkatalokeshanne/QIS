"""Tests for metric discovery and the calculate_all_metrics entry point."""

from app.metrics.calculator import calculate_all_metrics
from app.metrics.registry import discover_metrics, list_metric_definitions

EXPECTED_METRICS = {
    "net_profit",
    "profit_factor",
    "sharpe_ratio",
    "sortino_ratio",
    "max_drawdown",
    "win_rate",
    "expectancy",
    "average_trade",
    "recovery_factor",
    "consistency",
    "average_holding_time",
    "total_trades",
    "consecutive_winners",
    "consecutive_losers",
}


def test_discovery_finds_all_built_in_metrics():
    discover_metrics()
    names = {m["name"] for m in list_metric_definitions()}
    assert EXPECTED_METRICS.issubset(names)


def test_every_metric_declares_higher_is_better_and_format():
    discover_metrics()
    for meta in list_metric_definitions():
        assert isinstance(meta["higher_is_better"], bool)
        assert meta["format"]


def test_calculate_all_metrics_returns_every_registered_metric(mixed_trades):
    results = calculate_all_metrics(mixed_trades, starting_capital=10_000.0)
    names = {m["name"] for m in list_metric_definitions()}
    assert set(results.keys()) == names


def test_calculate_all_metrics_handles_empty_trades_without_crashing(empty_trades):
    results = calculate_all_metrics(empty_trades, starting_capital=10_000.0)
    assert results["total_trades"] == 0.0
    assert results["win_rate"] is None
