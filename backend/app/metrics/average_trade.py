"""Average Trade."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("average_trade")
class AverageTrade(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="average_trade",
            display_name="Average Trade",
            description="Mean P&L per trade.",
            category="profitability",
            higher_is_better=True,
            format="currency",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        return float(context.pnl.mean())
