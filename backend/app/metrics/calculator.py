"""
Metrics calculator: the single entry point the rest of the app uses.

`calculate_all_metrics(trades, starting_capital)` is intentionally the
ONLY function other modules (the Strategy Runner, the Ranking Engine,
the API layer) need to know about. It builds the shared context once
and runs every registered metric against it.
"""

from collections import defaultdict

from app.domain.interfaces.strategy import Trade
from app.metrics.context import build_context
from app.metrics.registry import discover_metrics, metric_registry


def calculate_all_metrics(trades: list[Trade], starting_capital: float) -> dict[str, float | None]:
    """
    Returns a dict of {metric_name: value}. Value is None for metrics
    that are undefined for this trade list (e.g. profit factor with no
    losing trades), so callers must handle None explicitly rather than
    assuming every metric always has a number.
    """
    discover_metrics()
    context = build_context(trades, starting_capital)

    results: dict[str, float | None] = {}
    for name, cls in metric_registry.all().items():
        results[name] = cls().calculate(context)
    return results


def calculate_monthly_metrics(trades: list[Trade], starting_capital: float) -> dict[str, dict[str, float | None]]:
    """
    Same full metrics suite as calculate_all_metrics, but sliced by the
    calendar month each trade CLOSED in (P&L realizes at exit, so that's
    when it should count toward a given month) -- {"2026-04": {...}, ...}.

    This is the SAME continuous backtest, just reported month by month:
    each month's starting capital is the actual running equity carried
    over from the end of the prior month, so the per-trade returns feeding
    Sharpe/PF/etc. reflect real compounding rather than resetting to the
    original capital every month.
    """
    closed = [t for t in trades if t.pnl is not None and t.exit_time is not None]
    if not closed:
        return {}

    by_month: dict[str, list[Trade]] = defaultdict(list)
    for t in sorted(closed, key=lambda t: t.exit_time):
        by_month[t.exit_time.strftime("%Y-%m")].append(t)

    monthly: dict[str, dict[str, float | None]] = {}
    running_capital = starting_capital
    for month_key in sorted(by_month):
        month_trades = by_month[month_key]
        monthly[month_key] = calculate_all_metrics(month_trades, running_capital)
        running_capital += sum(t.pnl for t in month_trades)

    return monthly
