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

    # Risk management — all disabled (None) unless explicitly set.
    atr_period: int = 14
    stop_loss_atr_multiple: float | None = None
    stop_loss_pct: float | None = None  # flat % of entry price; e.g. 0.01 = 1%
    take_profit_atr_multiple: float | None = None
    trailing_stop_atr_multiple: float | None = None
    risk_per_trade_pct: float | None = None


class RunBacktestRequest(BaseModel):
    dataset_ids: list[str] = Field(min_length=1, description="One or more datasets (tickers) to run against.")
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


class DatasetBacktestResult(BaseModel):
    dataset_id: str
    dataset_name: str
    results: list[StrategyResultResponse]


class RunBacktestResponse(BaseModel):
    dataset_results: list[DatasetBacktestResult]
