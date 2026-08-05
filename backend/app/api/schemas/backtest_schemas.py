"""Pydantic schemas for the Run Backtests / Results API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExecutionSettings(BaseModel):
    capital: float = 10_000.0
    quantity: float = 1.0
    commission_per_trade: float = 0.0
    slippage_pct: float = 0.0
    force_close_at_session_end: bool = True
    direction_filter: str = "both"  # "long_only" | "short_only" | "both"

    # Data-fetch scope (see ExecutionConfig's matching fields) -- both
    # False means regular-hours-only bars, the original behavior.
    include_extended_hours: bool = False
    include_overnight: bool = False

    # Risk management — all disabled (None) unless explicitly set.
    atr_period: int = 14
    stop_loss_atr_multiple: float | None = None
    stop_loss_pct: float | None = None  # flat % of entry price; e.g. 0.01 = 1%
    take_profit_atr_multiple: float | None = None
    trailing_stop_atr_multiple: float | None = None
    risk_per_trade_pct: float | None = None
    max_position_value_pct: float | None = None  # cap position value at capital * this; 1.0 = no leverage


class RunBacktestRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, description="One or more tickers to run against.")
    interval: str = Field(description="Bar interval to fetch live, e.g. '5min'.")
    start_date: str | None = Field(default=None, description="Optional override; omit for a sensible default lookback.")
    end_date: str | None = None
    strategy_names: list[str] | None = Field(
        default=None, description="Omit or null to run every discovered strategy."
    )
    strategy_params: dict[str, dict[str, Any]] | None = None
    execution: ExecutionSettings = ExecutionSettings()
    ranking_weights: dict[str, float] | None = None
    breakdown_by_month: bool = Field(
        default=False,
        description="Also slice the same backtest's results by calendar month (of trade exit).",
    )


class TradeResponse(BaseModel):
    entry_time: datetime
    exit_time: datetime | None
    direction: str
    entry_price: float
    exit_price: float | None
    quantity: float
    pnl: float | None
    exit_reason: str | None


class StrategyResultResponse(BaseModel):
    strategy_name: str
    strategy_display_name: str
    metrics: dict[str, float | None]
    trade_count: int
    overall_score: float | None
    trades: list[TradeResponse]
    rank: int | None
    monthly_metrics: dict[str, dict[str, float | None]] | None = None


class TickerBacktestResult(BaseModel):
    symbol: str
    results: list[StrategyResultResponse]


class RunBacktestResponse(BaseModel):
    ticker_results: list[TickerBacktestResult]
    # Symbols whose bars couldn't be fetched (bad ticker, no data, or a
    # network/connection failure that survived a retry -- see
    # backtest_routes._run_backtest_for_symbol) -- reported here rather
    # than one bad ticker failing the entire batch response.
    failed_symbols: list[str] = []


class HistoricalPerformanceRequest(BaseModel):
    """Fetched lazily, one strategy at a time, only when the user opens
    the Historical Performance popup for it -- see backtest_routes.py.
    Doing this for every strategy on every /run call was the eager
    version's real cost: two ~20s-capped network fetches (requested
    range + historical window) instead of one, paid even for the other
    34 strategies nobody ever looks at."""

    symbol: str
    interval: str = Field(description="Bar interval to fetch live, e.g. '5min'.")
    strategy_name: str
    strategy_params: dict[str, Any] | None = None
    execution: ExecutionSettings = ExecutionSettings()
    end_date: str | None = Field(default=None, description="Historical window ends here; omit for today.")


class HistoricalPerformanceResponse(BaseModel):
    historical_metrics: dict[str, float | None] | None = None
    historical_trade_count: int | None = None
    historical_period_start: datetime | None = None
    historical_period_end: datetime | None = None
    historical_monthly_metrics: dict[str, dict[str, float | None]] | None = None
