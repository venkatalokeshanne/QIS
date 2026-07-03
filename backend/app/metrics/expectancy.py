"""
Expectancy.

Computed via the classic win-rate / average-win / average-loss
decomposition (rather than just re-using average_trade) because that's
the conventional definition traders expect, even though it's
numerically equivalent to mean(pnl).
"""

from app.domain.interfaces.metric import Metric, MetricMetadata
from app.metrics.context import MetricsContext
from app.metrics.registry import metric_registry


@metric_registry.register("expectancy")
class Expectancy(Metric):
    @property
    def metadata(self) -> MetricMetadata:
        return MetricMetadata(
            name="expectancy",
            display_name="Expectancy",
            description="(Win rate * avg win) - (loss rate * avg loss), per trade.",
            category="profitability",
            higher_is_better=True,
            format="currency",
        )

    def calculate(self, context: MetricsContext) -> float | None:
        if context.pnl.empty:
            return None
        wins = context.pnl[context.pnl > 0]
        losses = context.pnl[context.pnl < 0]
        n = len(context.pnl)

        win_rate = len(wins) / n
        loss_rate = len(losses) / n
        avg_win = wins.mean() if not wins.empty else 0.0
        avg_loss = abs(losses.mean()) if not losses.empty else 0.0

        return float(win_rate * avg_win - loss_rate * avg_loss)
