"""Average Holding Time, in minutes."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("average_holding_time")
class AverageHoldingTime(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="average_holding_time",
            display_name="Avg Holding Time",
            description="Mean duration a position was held, in minutes.",
            category="behavior",
            higher_is_better=False,  # context-dependent, but shorter is the intraday norm
            format="duration_minutes",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if not context.trades:
            return None
        durations = [
            (t.exit_time - t.entry_time).total_seconds() / 60.0
            for t in context.trades
            if t.exit_time is not None
        ]
        if not durations:
            return None
        return float(sum(durations) / len(durations))
