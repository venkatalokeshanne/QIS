"""Consecutive Winners (longest winning streak)."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics._streak_utils import longest_streak
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("consecutive_winners")
class ConsecutiveWinners(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="consecutive_winners",
            display_name="Max Consecutive Winners",
            description="Longest streak of consecutive winning trades.",
            category="behavior",
            higher_is_better=True,
            format="count",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        return float(longest_streak(context.pnl, winning=True))
