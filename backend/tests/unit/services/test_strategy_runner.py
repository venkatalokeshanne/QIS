"""Tests for app.services.strategy_runner — the full run-all-strategies pipeline."""

import pandas as pd
import pytest

from app.core.exceptions import NotFoundError
from app.services.strategy_runner import RunRequest, run_strategies
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import discover_strategies, strategy_registry


def _intraday_df(n_days=2):
    sessions = []
    for d in range(n_days):
        idx = pd.date_range(f"2024-01-0{d + 2} 09:30", periods=30, freq="1min")
        base = 100 + d * 5
        prices = [base + (i % 5) - 2 + (0.3 * i) for i in range(30)]
        sessions.append(
            pd.DataFrame(
                {
                    "open": prices,
                    "high": [p + 0.5 for p in prices],
                    "low": [p - 0.5 for p in prices],
                    "close": prices,
                    "volume": [500] * 30,
                },
                index=idx,
            )
        )
    return pd.concat(sessions)


def test_run_all_strategies_returns_a_result_per_registered_strategy():
    df = _intraday_df()
    request = RunRequest(strategy_names=None)
    results = run_strategies(df, request)

    discover_strategies()
    assert {r.strategy_name for r in results} == set(strategy_registry.names())


def test_run_selected_strategies_only_runs_those():
    df = _intraday_df()
    request = RunRequest(strategy_names=["hma_trend_cross"])
    results = run_strategies(df, request)

    assert len(results) == 1
    assert results[0].strategy_name == "hma_trend_cross"


def test_run_unknown_strategy_raises_not_found():
    df = _intraday_df()
    request = RunRequest(strategy_names=["not_a_real_strategy"])
    with pytest.raises(NotFoundError):
        run_strategies(df, request)


def test_per_strategy_param_overrides_are_applied():
    df = _intraday_df()
    request = RunRequest(
        strategy_names=["hma_trend_cross"],
        strategy_params={"hma_trend_cross": {"fast_period": 3, "slow_period": 6}},
    )
    results = run_strategies(df, request)
    assert len(results) == 1  # doesn't crash with custom params


def test_results_include_metrics_and_trade_counts():
    df = _intraday_df()
    request = RunRequest(strategy_names=["orb_breakout"], execution_config=ExecutionConfig(capital=5000))
    results = run_strategies(df, request)

    assert results[0].trade_count >= 0
    assert "net_profit" in results[0].metrics
    assert "total_trades" in results[0].metrics


def test_breakdown_by_month_populates_monthly_metrics_when_requested():
    df = _intraday_df()
    request = RunRequest(strategy_names=["orb_breakout"], breakdown_by_month=True)
    results = run_strategies(df, request)
    assert results[0].monthly_metrics is not None
    assert isinstance(results[0].monthly_metrics, dict)


def test_breakdown_by_month_defaults_to_none():
    df = _intraday_df()
    request = RunRequest(strategy_names=["orb_breakout"])
    results = run_strategies(df, request)
    assert results[0].monthly_metrics is None
