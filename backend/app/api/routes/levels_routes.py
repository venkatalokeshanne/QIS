"""Daily Levels routes — thin wrapper around app.services.levels_service / levels_backtest_service."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.schemas.levels_schemas import (
    DailyLevelsResponse,
    DayLevelsReportResponse,
    DayReportsRequest,
    DayReportsResponse,
    LevelsBacktestRequest,
    LevelsBacktestResponse,
)
from app.services.levels_backtest_service import get_day_reports, run_levels_backtest
from app.services.levels_service import get_daily_levels

router = APIRouter(prefix="/api/levels", tags=["levels"])


@router.post("/backtest", response_model=LevelsBacktestResponse)
def backtest_levels(payload: LevelsBacktestRequest):
    report = run_levels_backtest(payload.symbol)
    return LevelsBacktestResponse(**asdict(report))


@router.post("/backtest/days", response_model=DayReportsResponse)
def backtest_levels_days(payload: DayReportsRequest):
    reports = get_day_reports(payload.symbol, payload.dates)
    found_dates = {r.date for r in reports}
    dates_not_found = [d for d in payload.dates if d not in found_dates]
    return DayReportsResponse(
        symbol=payload.symbol.upper(),
        reports=[DayLevelsReportResponse(**asdict(r)) for r in reports],
        dates_not_found=dates_not_found,
    )


@router.get("/{symbol}", response_model=DailyLevelsResponse)
def get_levels(symbol: str):
    levels = get_daily_levels(symbol)
    return DailyLevelsResponse(**levels.__dict__)
