"""Net Profit."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("net_profit")
class NetProfit(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="net_profit",
            display_name="Net Profit",
            description="Sum of all trade P&L.",
            category="profitability",
            higher_is_better=True,
            format="currency",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return 0.0
        return float(context.pnl.sum())
