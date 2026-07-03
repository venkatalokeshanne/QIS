"""
MetricsContext: the one place that derives equity curve / per-trade
returns from a raw trade list. Every metric reads from this instead of
recomputing it, so there's exactly one definition of "the equity curve"
across Net Profit, Drawdown, Sharpe, Recovery Factor, etc.
"""

from dataclasses import dataclass

import pandas as pd

from app.domain.interfaces.strategy import Trade


@dataclass(frozen=True)
class MetricsContext:
    trades: list[Trade]
    starting_capital: float
    pnl: pd.Series  # one value per trade, in chronological order
    equity_curve: pd.Series  # starting_capital, then cumulative equity after each trade
    returns: pd.Series  # per-trade pnl / starting_capital (simple return basis)


def build_context(trades: list[Trade], starting_capital: float) -> MetricsContext:
    """
    Build the shared context from a raw trade list.

    Trades are assumed to already be in chronological order (the
    execution engine produces them that way). Handles the zero-trade
    case gracefully so metrics can decide individually how to report
    "undefined" rather than crashing here.
    """
    closed = [t for t in trades if t.pnl is not None]
    pnl = pd.Series([t.pnl for t in closed], dtype=float)

    if pnl.empty:
        equity_curve = pd.Series([starting_capital], dtype=float)
    else:
        equity_curve = pd.Series(
            [starting_capital, *(starting_capital + pnl.cumsum())], dtype=float
        )

    returns = pnl / starting_capital if starting_capital else pnl * 0

    return MetricsContext(
        trades=closed,
        starting_capital=starting_capital,
        pnl=pnl,
        equity_curve=equity_curve,
        returns=returns,
    )
