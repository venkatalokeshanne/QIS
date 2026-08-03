"""Pydantic schemas for the signal-alert Watches API."""

from typing import Any

from pydantic import BaseModel

from app.api.schemas.backtest_schemas import ExecutionSettings


class WatchCreateRequest(BaseModel):
    symbol: str
    strategy_name: str
    strategy_params: dict[str, Any] = {}
    interval: str  # "1min" | "5min" | "15min" | "1h" | "1day"
    # Snapshotted at creation time from the Settings page, so a live
    # alert's entries/exits match what a backtest with these same
    # settings would have produced -- see WatchRepository's docstring.
    execution: ExecutionSettings = ExecutionSettings()


class WatchResponse(BaseModel):
    id: str
    symbol: str
    strategy_name: str
    strategy_params: dict[str, Any]
    interval: str
    execution_settings: dict[str, Any]
    last_notified_bar_time: str | None
    last_checked_at: str | None
    created_at: str
