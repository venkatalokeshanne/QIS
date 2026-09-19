"""
Daily Strategy Selector routes.

Separate from /api/backtests -- this is regime-aware strategy +
parameter SWITCHING, not a single fixed-strategy backtest. See
app.services.calibration_service (the offline "build the playbook"
step) and app.services.daily_selector_service (the live "what to do
today" / backtest "did switching actually help" steps).
"""

import dataclasses
import logging

from fastapi import APIRouter

from app.api.schemas.daily_selection_schemas import (
    CalibrateRequest,
    CalibrateResponse,
    DailySelectionBatchResponse,
    DailySelectionRequest,
    DailySelectionResponse,
    SelectionBacktestRequest,
    SelectionBacktestResponse,
    TickerProfileResponse,
)
from app.config.market_proxies import STARTER_TICKERS, market_proxies_for
from app.core.exceptions import NotFoundError
from app.services import calibration_store
from app.services.calibration_service import calibrate_ticker
from app.services.daily_selector_service import backtest_selection, select_for_today

_logger = logging.getLogger("quant_platform")

router = APIRouter(prefix="/api/daily-selection", tags=["daily-selection"])


@router.post("/calibrate", response_model=CalibrateResponse)
def run_calibration(payload: CalibrateRequest):
    symbols = payload.symbols or STARTER_TICKERS
    proxies_override = payload.market_proxies or {}

    profiles: list[TickerProfileResponse] = []
    failed_symbols: list[str] = []

    for raw_symbol in symbols:
        symbol = raw_symbol.upper()
        market_proxies = proxies_override.get(symbol, market_proxies_for(symbol))
        try:
            profile = calibrate_ticker(
                symbol,
                payload.interval,
                market_proxies,
                payload.start_date,
                payload.cutoff_date,
                payload.strategy_names,
            )
        except Exception:
            _logger.exception("daily-selection calibrate %s: failed, excluding from results", symbol)
            failed_symbols.append(symbol)
            continue
        calibration_store.save_profile(profile)
        profiles.append(TickerProfileResponse(**dataclasses.asdict(profile)))

    return CalibrateResponse(profiles=profiles, failed_symbols=failed_symbols)


@router.get("/profile/{symbol}", response_model=TickerProfileResponse)
def get_profile(symbol: str):
    profile = calibration_store.load_profile(symbol)
    if profile is None:
        raise NotFoundError(f"'{symbol.upper()}' has not been calibrated yet -- POST /api/daily-selection/calibrate first.")
    return TickerProfileResponse(**dataclasses.asdict(profile))


@router.post("/run", response_model=DailySelectionBatchResponse)
def run_daily_selection(payload: DailySelectionRequest):
    selections: list[DailySelectionResponse] = []
    failed_symbols: list[str] = []

    for raw_symbol in payload.symbols:
        symbol = raw_symbol.upper()
        try:
            selection = select_for_today(symbol, payload.interval)
        except Exception:
            _logger.exception("daily-selection run %s: failed, excluding from results", symbol)
            failed_symbols.append(symbol)
            continue
        selections.append(DailySelectionResponse(**dataclasses.asdict(selection)))

    return DailySelectionBatchResponse(selections=selections, failed_symbols=failed_symbols)


@router.post("/backtest", response_model=SelectionBacktestResponse)
def run_selection_backtest(payload: SelectionBacktestRequest):
    """Tests the symbol's ALREADY-CALIBRATED playbook -- 404s (via
    backtest_selection's NotFoundError) if it hasn't been calibrated
    yet. Does not recalibrate; see SelectionBacktestRequest's docstring."""
    result = backtest_selection(payload.symbol, payload.interval, payload.start_date, payload.test_end_date)
    return SelectionBacktestResponse(**dataclasses.asdict(result))
