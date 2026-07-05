"""Pydantic schemas for the signal-alert Watches API."""

from typing import Any

from pydantic import BaseModel


class WatchCreateRequest(BaseModel):
    expo_push_token: str
    symbol: str
    strategy_name: str
    strategy_params: dict[str, Any] = {}
    interval: str  # "1min" | "5min" | "15min"


class TestNotificationRequest(BaseModel):
    expo_push_token: str


class WatchResponse(BaseModel):
    id: str
    symbol: str
    strategy_name: str
    strategy_params: dict[str, Any]
    interval: str
    last_notified_bar_time: str | None
    last_checked_at: str | None
    created_at: str
