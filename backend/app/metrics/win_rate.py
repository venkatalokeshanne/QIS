"""Win Rate."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("win_rate")
class WinRate(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="win_rate",
            display_name="Win Rate",
            description="Percentage of trades with positive P&L.",
            category="profitability",
            higher_is_better=True,
            format="percent",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        wins = (context.pnl > 0).sum()
        return float(wins / len(context.pnl) * 100)
