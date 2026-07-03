"""
Scorer.

Metrics come in wildly different units (dollars, percentages,
unitless ratios), so a weighted sum of raw values would be dominated
by whichever metric happens to have the largest magnitude. This module
min-max normalizes each metric to [0, 1] ACROSS the batch of strategies
being ranked (so scores are only meaningful relative to strategies run
in the same batch, which matches "which strategy performs best on
THIS dataset").

Metrics whose metadata says higher_is_better=False (e.g. max_drawdown)
are inverted after normalization so "1.0" always means "best".
"""

from app.metrics.registry import discover_metrics, metric_registry
from app.ranking.models import RankingConfig, StrategyResult


def _metric_is_higher_better(name: str) -> bool:
    discover_metrics()
    cls = metric_registry.get(name)
    return cls().metadata.higher_is_better


def _normalize_metric_across_batch(
    values: list[float | None], higher_is_better: bool
) -> list[float | None]:
    """Min-max normalize one metric's values across all strategies, preserving None."""
    present = [v for v in values if v is not None]
    if len(present) < 2 or max(present) == min(present):
        # Can't meaningfully differentiate with 0-1 data points or a constant value.
        return [0.5 if v is not None else None for v in values]

    lo, hi = min(present), max(present)
    normalized = []
    for v in values:
        if v is None:
            normalized.append(None)
            continue
        scaled = (v - lo) / (hi - lo)
        normalized.append(scaled if higher_is_better else 1 - scaled)
    return normalized


def score_results(
    raw_results: list[tuple[str, str, dict[str, float | None], int, list, dict | None]],
    config: RankingConfig | None = None,
) -> list[StrategyResult]:
    """
    Args:
        raw_results: list of (strategy_name, display_name, metrics_dict, trade_count, trades, monthly_metrics)
        config: ranking weights + minimum trade threshold.

    Returns:
        StrategyResult list, sorted best-first (rank 1 = best), with
        strategies below min_trades or with no usable metrics scored as None
        and sorted to the end.
    """
    config = config or RankingConfig()

    # Normalize each weighted metric across the batch.
    normalized_by_metric: dict[str, list[float | None]] = {}
    for metric_name in config.weights:
        raw_values = [metrics.get(metric_name) for _, _, metrics, _, _, _ in raw_results]
        higher_is_better = _metric_is_higher_better(metric_name)
        normalized_by_metric[metric_name] = _normalize_metric_across_batch(raw_values, higher_is_better)

    results: list[StrategyResult] = []
    for i, (name, display_name, metrics, trade_count, trades, monthly_metrics) in enumerate(raw_results):
        score = None
        if trade_count >= config.min_trades:
            weighted_sum = 0.0
            total_weight = 0.0
            for metric_name, weight in config.weights.items():
                norm_value = normalized_by_metric[metric_name][i]
                if norm_value is None:
                    continue
                weighted_sum += norm_value * weight
                total_weight += weight
            if total_weight > 0:
                score = (weighted_sum / total_weight) * 100  # scale to 0-100

        results.append(
            StrategyResult(
                strategy_name=name,
                strategy_display_name=display_name,
                metrics=metrics,
                trade_count=trade_count,
                overall_score=score,
                trades=trades,
                monthly_metrics=monthly_metrics,
            )
        )

    # Sort: scored strategies first (best score first), unscored strategies last.
    scored = sorted([r for r in results if r.overall_score is not None], key=lambda r: -r.overall_score)
    unscored = [r for r in results if r.overall_score is None]

    ranked = []
    for i, r in enumerate(scored, start=1):
        ranked.append(StrategyResult(**{**r.__dict__, "rank": i}))
    ranked.extend(unscored)
    return ranked
