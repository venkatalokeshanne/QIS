"""
Ranking domain models.

A RankingConfig is a set of {metric_name: weight} pairs — this is what
makes "the ranking algorithm should be configurable" concrete: change
the weights dict (or pass a different one per request) and the score
changes, with no code edits.
"""

from dataclasses import dataclass, field

from app.domain.interfaces.strategy import Trade


DEFAULT_RANKING_WEIGHTS: dict[str, float] = {
    "net_profit": 1.0,
    "profit_factor": 1.0,
    "sharpe_ratio": 1.0,
    "sortino_ratio": 0.5,
    "max_drawdown": 1.0,  # lower_is_better handled via metric metadata, not sign-flipped here
    "win_rate": 0.5,
    "expectancy": 0.75,
    "recovery_factor": 0.75,
    "consistency": 0.5,
}


@dataclass(frozen=True)
class RankingConfig:
    """weights: {metric_name: weight}. Metrics not listed are ignored by the score
    (still shown in results, just not part of ranking)."""

    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_RANKING_WEIGHTS))
    min_trades: int = 1  # strategies with fewer closed trades than this get score=None


@dataclass(frozen=True)
class StrategyResult:
    """One strategy's full result: raw metrics, trade count, and its overall score."""

    strategy_name: str
    strategy_display_name: str
    metrics: dict[str, float | None]
    trade_count: int
    overall_score: float | None
    trades: list[Trade] = field(default_factory=list)
    rank: int | None = None
    # {"2026-04": {metric_name: value}, ...} -- only populated when the
    # caller requested a monthly breakdown; None otherwise.
    monthly_metrics: dict[str, dict[str, float | None]] | None = None
