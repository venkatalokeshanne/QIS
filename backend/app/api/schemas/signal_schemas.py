"""Pydantic schemas for the live Signal Check API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SignalCheckRequest(BaseModel):
    symbol: str
    interval: str  # "1min" | "5min" | "15min"
    strategy_name: str
    strategy_params: dict[str, Any] = {}


class SignalCheckResponse(BaseModel):
    symbol: str
    interval: str
    strategy_name: str
    as_of: datetime
    price: float
    event: str | None  # "entry" | "exit" | None
    direction: str | None  # only set when event == "entry"
    exit_reason: str | None  # only set when event == "exit"
