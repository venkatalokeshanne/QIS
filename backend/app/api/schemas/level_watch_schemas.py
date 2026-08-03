"""Pydantic schemas for the Daily Levels S/R-change Level Watches API."""

from pydantic import BaseModel


class LevelWatchCreateRequest(BaseModel):
    symbol: str


class LevelWatchResponse(BaseModel):
    id: str
    symbol: str
    last_levels: list[float] | None
    last_checked_at: str | None
    created_at: str
