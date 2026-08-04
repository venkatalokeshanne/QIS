"""Pydantic schemas for the Scanner API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.api.schemas.backtest_schemas import ExecutionSettings
from app.services.scanner_service import DEFAULT_LOOKBACK_BARS


class ScannerRunRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, description="Tickers to scan.")
    interval: str = Field(description="Bar interval to fetch live, e.g. '5min'.")
    strategy_names: list[str] | None = Field(
        default=None, description="Omit or null to scan every discovered strategy."
    )
    strategy_params: dict[str, dict[str, Any]] | None = None
    execution: ExecutionSettings = ExecutionSettings()
    lookback_bars: int = Field(
        default=DEFAULT_LOOKBACK_BARS,
        ge=1,
        description="A signal counts as 'recent' if its entry landed within this many of the freshest bars.",
    )


class ScanSignal(BaseModel):
    symbol: str
    strategy_name: str
    strategy_display_name: str
    interval: str
    as_of: datetime
    price: float
    signal_direction: str  # "long" | "short"
    signal_time: datetime
    bars_ago: int
    still_active: bool

    # Trailing-year trust check for this exact symbol+strategy (see
    # scanner_service.HISTORICAL_LOOKBACK_DAYS) -- "has this setup
    # actually worked here before, or is this its first time firing."
    # None when it couldn't be computed rather than a fabricated 0.
    historical_trade_count: int | None = None
    historical_win_rate: float | None = None
    historical_profit_factor: float | None = None
    historical_net_profit: float | None = None


class ScannerRunResponse(BaseModel):
    signals: list[ScanSignal]
    failed_symbols: list[str] = []


class DayPrepRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, description="Tickers to evaluate.")
    interval: str = Field(description="Bar interval to fetch live, e.g. '5min'.")
    strategy_names: list[str] | None = Field(
        default=None, description="Omit or null to evaluate every discovered strategy."
    )
    strategy_params: dict[str, dict[str, Any]] | None = None
    execution: ExecutionSettings = ExecutionSettings()


class StrategyEdgeResponse(BaseModel):
    strategy_name: str
    strategy_display_name: str
    trade_count: int
    win_rate: float | None
    profit_factor: float | None
    net_profit: float | None
    recent_trade_count: int
    has_live_signal: bool
    signal_direction: str | None
    signal_bars_ago: int | None


class TickerConcentrationResponse(BaseModel):
    symbol: str
    price: float
    concentration_score: float
    activity_count: int
    gap_pct: float | None
    gap_as_of: datetime | None
    top_strategies: list[StrategyEdgeResponse]


class DayPrepResponse(BaseModel):
    tickers: list[TickerConcentrationResponse]
    failed_symbols: list[str] = []
