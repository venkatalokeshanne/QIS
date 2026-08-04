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


class ScannerRunResponse(BaseModel):
    signals: list[ScanSignal]
    failed_symbols: list[str] = []
