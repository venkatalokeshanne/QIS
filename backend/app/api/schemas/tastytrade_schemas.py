"""Pydantic schemas for the Tastytrade live-quote API."""

from datetime import datetime

from pydantic import BaseModel


class TastytradeQuoteResponse(BaseModel):
    symbol: str
    bid: float | None
    ask: float | None
    last: float | None
    updated_at: datetime | None
    available: bool  # False while a freshly-subscribed symbol has no data yet
