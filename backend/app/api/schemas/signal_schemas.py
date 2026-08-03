"""Pydantic schemas for the live Signal Check API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.api.schemas.backtest_schemas import ExecutionSettings


class SignalCheckRequest(BaseModel):
    symbol: str
    interval: str  # "1min" | "5min" | "15min"
    strategy_name: str
    strategy_params: dict[str, Any] = {}
    # Same execution settings a backtest would use (stop loss, take
    # profit, direction filter, etc.) so the Live Signal tab's preview
    # matches what a backtest with these settings would show.
    # force_close_at_session_end is always ignored for this live check
    # regardless of what's sent -- see signal_service.check_signal.
    execution: ExecutionSettings = ExecutionSettings()


class SignalEvent(BaseModel):
    time: datetime
    event: str  # "entry" | "exit"
    direction: str | None  # only set when event == "entry"
    exit_reason: str | None  # only set when event == "exit"


class SignalCheckResponse(BaseModel):
    symbol: str
    interval: str
    strategy_name: str
    as_of: datetime
    price: float
    event: str | None  # "entry" | "exit" | None
    direction: str | None  # only set when event == "entry"
    exit_reason: str | None  # only set when event == "exit"
    position: str  # "long" | "short" | "flat"
    today_events: list[SignalEvent] = []
