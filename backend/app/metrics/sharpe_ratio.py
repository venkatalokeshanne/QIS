"""
Sharpe Ratio.

Computed on a per-trade return basis (pnl / starting_capital per
trade), unannualized. Intraday trade counts per day vary, so a
clean annualization factor (e.g. sqrt(252)) doesn't cleanly apply
without a fixed bar/trade frequency assumption -- this is documented
here rather than silently baked into the number. The ranking engine
should compare this value across strategies run on the SAME dataset,
where the comparison is still meaningful.
"""

import numpy as np

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("sharpe_ratio")
class SharpeRatio(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="sharpe_ratio",
            display_name="Sharpe Ratio",
            description="Mean per-trade return divided by its standard deviation (unannualized).",
            category="risk",
            higher_is_better=True,
            format="ratio",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        returns = context.returns
        if len(returns) < 2:
            return None
        std = returns.std(ddof=1)
        if std == 0 or np.isnan(std):
            return None
        return float(returns.mean() / std)
