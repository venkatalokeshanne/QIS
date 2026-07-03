"""Maximum Drawdown (percentage decline from peak equity)."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("max_drawdown")
class MaxDrawdown(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="max_drawdown",
            display_name="Max Drawdown",
            description="Largest peak-to-trough decline in equity, as a percentage.",
            category="risk",
            higher_is_better=False,
            format="percent",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        equity = context.equity_curve
        if len(equity) < 2:
            return 0.0
        running_peak = equity.cummax()
        drawdown_pct = (equity - running_peak) / running_peak * 100
        return float(abs(drawdown_pct.min()))
