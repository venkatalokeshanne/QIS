"""Pydantic schemas for the Daily Strategy Selector API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CalibrateRequest(BaseModel):
    symbols: list[str] | None = Field(
        default=None, description="Omit or null to calibrate the starter ticker set (see market_proxies.STARTER_TICKERS)."
    )
    interval: str = Field(description="Bar interval to calibrate/trade at, e.g. '5min'.")
    start_date: str = Field(description="Calibration window start.")
    cutoff_date: str = Field(
        default="2026-04-30",
        description="Calibration uses ONLY data up to (and including) this date -- see /backtest for testing what happens after it.",
    )
    market_proxies: dict[str, list[str]] | None = Field(
        default=None, description="Per-symbol market-proxy override; omit to use market_proxies.market_proxies_for()'s defaults."
    )
    strategy_names: list[str] | None = Field(
        default=None, description="Omit or null to consider every discovered strategy."
    )


class TickerProfileResponse(BaseModel):
    symbol: str
    interval: str
    calibrated_through: str
    market_proxies: list[str]
    default_strategy: str
    strategy_by_regime: dict[str, str]
    regime_trade_counts: dict[str, int]
    stop_loss_atr_multiple: float
    take_profit_atr_multiple: float
    entry_time_start: str | None
    entry_time_end: str | None
    regime_params: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-regime-bucket parameter overrides (stop_loss_atr_multiple, take_profit_atr_multiple, "
        "entry_time_start, entry_time_end) for buckets where the bucket's own winning strategy was tuned "
        "separately and out-scored the ticker-wide defaults. Buckets absent here use the ticker-wide params above.",
    )


class CalibrateResponse(BaseModel):
    profiles: list[TickerProfileResponse]
    failed_symbols: list[str] = []


class DailySelectionRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, description="Tickers to select today's strategy for.")
    interval: str = Field(description="Bar interval to trade at, e.g. '5min'.")


class DailySelectionResponse(BaseModel):
    symbol: str
    interval: str
    as_of: datetime
    price: float | None
    ticker_regime: str | None
    market_regime: str | None
    regime_bucket: str | None
    selected_strategy: str
    used_fallback: bool
    stop_loss_atr_multiple: float
    take_profit_atr_multiple: float
    entry_time_start: str | None
    entry_time_end: str | None
    has_live_signal: bool
    signal_direction: str | None
    signal_time: datetime | None
    bars_ago: int | None


class DailySelectionBatchResponse(BaseModel):
    selections: list[DailySelectionResponse]
    failed_symbols: list[str] = []


class SelectionBacktestRequest(BaseModel):
    """Tests the symbol's ALREADY-CALIBRATED playbook (POST /calibrate
    must have been run for it first, or this 404s) -- does NOT
    recalibrate. switching-vs-baseline is always evaluated against the
    exact same playbook Today's Picks (/run) is currently reading from."""

    symbol: str
    interval: str = Field(description="Bar interval to trade at, e.g. '5min'.")
    start_date: str = Field(
        description="Requested test window start -- clamped up to the profile's calibrated_through date if it "
        "predates the calibration cutoff, to preserve the out-of-sample guarantee. The response's test_start "
        "reports whichever date actually got used."
    )
    test_end_date: str = Field(description="Backtest window end.")


class RegimeSegmentResponse(BaseModel):
    regime_bucket: str
    strategy_used: str
    start_date: str
    end_date: str
    trade_count: int
    stop_loss_atr_multiple: float
    take_profit_atr_multiple: float
    entry_time_start: str | None
    entry_time_end: str | None
    metrics: dict[str, float | None]


class SwitchingTradeResponse(BaseModel):
    """One trade from the switching backtest -- same shape as
    TradeResponse (see backtest_schemas.py) plus WHICH strategy
    generated it, since different trades in the same backtest can come
    from different strategies as the regime switches day to day."""

    strategy_name: str
    entry_time: datetime
    exit_time: datetime | None
    direction: str
    entry_price: float
    exit_price: float | None
    quantity: float
    pnl: float | None
    exit_reason: str | None


class SelectionBacktestResponse(BaseModel):
    symbol: str
    interval: str
    calibrated_through: str
    test_start: str
    test_end: str
    switching_metrics: dict[str, float | None]
    switching_trade_count: int
    switching_trades: list[SwitchingTradeResponse]
    baseline_strategy: str
    baseline_metrics: dict[str, float | None]
    baseline_trade_count: int
    segments: list[RegimeSegmentResponse]
