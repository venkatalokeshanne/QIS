"""
Strategy Runner.

Orchestrates: pick strategies -> run each independently -> collect
Trades -> compute metrics -> rank. This is the service the API's
"Run Backtests" endpoint calls; it is intentionally the only place
that ties Strategy execution, the Metrics Engine, and the Ranking
Engine together.
"""

from dataclasses import dataclass

import pandas as pd

from app.core.exceptions import NotFoundError
from app.metrics.calculator import calculate_all_metrics, calculate_monthly_metrics
from app.ranking.models import RankingConfig, StrategyResult
from app.ranking.scorer import score_results
from app.strategies.execution import ExecutionConfig, simulate_trades
from app.strategies.registry import discover_strategies, get_strategy, strategy_registry


@dataclass(frozen=True)
class RunRequest:
    strategy_names: list[str] | None  # None = run every discovered strategy
    strategy_params: dict[str, dict] | None = None  # per-strategy param overrides, keyed by strategy name
    execution_config: ExecutionConfig = ExecutionConfig()
    ranking_config: RankingConfig = RankingConfig()
    # When True, the SAME backtest is also sliced and reported per
    # calendar month (see calculate_monthly_metrics) -- off by default
    # since it's extra computation nobody needs for a quick batch scan.
    breakdown_by_month: bool = False


def _resolve_strategy_names(requested: list[str] | None) -> list[str]:
    discover_strategies()
    available = strategy_registry.names()
    if requested is None:
        return available

    unknown = [name for name in requested if name not in available]
    if unknown:
        raise NotFoundError(f"Unknown strategy name(s): {unknown}. Available: {available}")
    return requested


def run_strategies(df: pd.DataFrame, request: RunRequest) -> list[StrategyResult]:
    """
    Run each requested strategy independently against the given
    dataset and return ranked results. A failure in one strategy does
    not abort the batch — it's recorded with zero trades so the
    person can still see and compare everything else that ran.
    """
    names = _resolve_strategy_names(request.strategy_names)
    param_overrides = request.strategy_params or {}

    raw_results: list[tuple[str, str, dict[str, float | None], int, list, dict | None]] = []

    for name in names:
        strategy = get_strategy(name)
        params = strategy.validate_params(param_overrides.get(name, {}))

        try:
            enriched = strategy.prepare(df, params)
            entries = strategy.generate_entries(enriched, params)
            exits = strategy.generate_exits(enriched, params)
            trades = simulate_trades(enriched, entries, exits, request.execution_config)
        except Exception:
            trades = []  # strategy failed to run; report it with zero trades rather than crash the batch

        metrics = calculate_all_metrics(trades, request.execution_config.capital)
        monthly_metrics = (
            calculate_monthly_metrics(trades, request.execution_config.capital)
            if request.breakdown_by_month
            else None
        )
        raw_results.append((name, strategy.metadata.display_name, metrics, len(trades), trades, monthly_metrics))

    return score_results(raw_results, request.ranking_config)
