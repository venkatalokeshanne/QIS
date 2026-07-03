"""Recovery Factor."""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics._drawdown_utils import max_drawdown_abs
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("recovery_factor")
class RecoveryFactor(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="recovery_factor",
            display_name="Recovery Factor",
            description="Net profit divided by max drawdown (dollar terms).",
            category="risk",
            higher_is_better=True,
            format="ratio",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        net_profit = float(context.pnl.sum())
        dd = max_drawdown_abs(context)
        if dd == 0:
            return None  # undefined: no drawdown to recover from
        return net_profit / dd
