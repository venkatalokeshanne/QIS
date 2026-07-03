"""Consecutive Losers (longest losing streak)."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics._streak_utils import longest_streak
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("consecutive_losers")
class ConsecutiveLosers(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="consecutive_losers",
            display_name="Max Consecutive Losers",
            description="Longest streak of consecutive losing trades.",
            category="behavior",
            higher_is_better=False,
            format="count",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        return float(longest_streak(context.pnl, winning=False))
