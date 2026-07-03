"""
Consistency.

Measures how closely the equity curve tracks a straight line (R^2
against a linear fit over trade sequence). A strategy that grinds out
steady gains scores near 1.0; one with a few huge wins and long flat
stretches scores much lower, even with the same net profit.
"""

import numpy as np

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("consistency")
class Consistency(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="consistency",
            display_name="Consistency",
            description="R^2 of the equity curve against a straight-line fit (0-1).",
            category="risk",
            higher_is_better=True,
            format="ratio",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        equity = context.equity_curve.to_numpy()
        if len(equity) < 3:
            return None

        x = np.arange(len(equity))
        slope, intercept = np.polyfit(x, equity, 1)
        fitted = slope * x + intercept

        ss_res = np.sum((equity - fitted) ** 2)
        ss_tot = np.sum((equity - equity.mean()) ** 2)
        if ss_tot == 0:
            return None  # flat equity curve, no variance to explain
        return float(1 - ss_res / ss_tot)
