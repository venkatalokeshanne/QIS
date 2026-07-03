"""Profit Factor."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("profit_factor")
class ProfitFactor(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="profit_factor",
            display_name="Profit Factor",
            description="Gross profit divided by gross loss (absolute value).",
            category="profitability",
            higher_is_better=True,
            format="ratio",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        gross_profit = context.pnl[context.pnl > 0].sum()
        gross_loss = context.pnl[context.pnl < 0].sum()
        if gross_loss == 0:
            return None  # undefined: no losing trades to divide by
        return float(gross_profit / abs(gross_loss))
