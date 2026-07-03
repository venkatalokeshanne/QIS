"""Total Trades."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("total_trades")
class TotalTrades(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="total_trades",
            display_name="Total Trades",
            description="Number of closed trades.",
            category="volume",
            higher_is_better=True,
            format="count",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        return float(len(context.trades))
