"""
Shared drawdown calculation.

Not a registered Metric itself — just a helper so max_drawdown.py and
recovery_factor.py don't each compute the running-peak/drawdown series
independently.
"""

import pandas as pd

from app.metrics.context import MetricsContext


def max_drawdown_abs(context: MetricsContext) -> float:
    """Largest peak-to-trough decline in equity, in dollar terms (>= 0)."""
    equity = context.equity_curve
    if len(equity) < 2:
        return 0.0
    running_peak = equity.cummax()
    drawdown = equity - running_peak
    return float(abs(drawdown.min()))
