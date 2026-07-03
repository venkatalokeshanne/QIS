"""
Sortino Ratio.

Like Sharpe, but only penalizes downside volatility (negative
returns), which is generally preferred for asymmetric strategies.
Same per-trade, unannualized basis as Sharpe -- see sharpe_ratio.py
for the rationale.
"""

import numpy as np

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("sortino_ratio")
class SortinoRatio(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="sortino_ratio",
            display_name="Sortino Ratio",
            description="Mean per-trade return divided by downside deviation (unannualized).",
            category="risk",
            higher_is_better=True,
            format="ratio",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        returns = context.returns
        if len(returns) < 2:
            return None
        downside = returns[returns < 0]
        if downside.empty:
            return None  # undefined: no downside to measure
        downside_std = downside.std(ddof=1) if len(downside) > 1 else abs(downside.iloc[0])
        if downside_std == 0 or np.isnan(downside_std):
            return None
        return float(returns.mean() / downside_std)
