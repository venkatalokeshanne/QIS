"""Pydantic schemas for the Daily Levels API."""

from datetime import datetime

from pydantic import BaseModel


class LevelsBacktestRequest(BaseModel):
    symbol: str


class HitRateStatsResponse(BaseModel):
    sample_days: int
    touched_pct: float | None
    held_pct: float | None
    broken_pct: float | None


class DirectionalStatsResponse(BaseModel):
    sample_days: int
    closed_above_pct: float | None


class ADRStatsResponse(BaseModel):
    sample_days: int
    contained_pct: float | None
    exceeded_upside_pct: float | None
    exceeded_downside_pct: float | None


class OpeningRangeStatsResponse(BaseModel):
    sample_days: int
    closed_above_range_pct: float | None
    closed_below_range_pct: float | None
    stayed_inside_range_pct: float | None


class LevelsBacktestResponse(BaseModel):
    symbol: str
    total_sessions: int
    available_dates: list[str]
    overall_success_rate_pct: float | None
    overall_levels_touched: int
    overall_levels_held: int
    overall_levels_broken: int
    prior_day_high: HitRateStatsResponse
    prior_day_low: HitRateStatsResponse
    pivot_point: DirectionalStatsResponse
    pivot_r1: HitRateStatsResponse
    pivot_r2: HitRateStatsResponse
    pivot_r3: HitRateStatsResponse
    pivot_s1: HitRateStatsResponse
    pivot_s2: HitRateStatsResponse
    pivot_s3: HitRateStatsResponse
    camarilla_r1: HitRateStatsResponse
    camarilla_r2: HitRateStatsResponse
    camarilla_r3: HitRateStatsResponse
    camarilla_r4: HitRateStatsResponse
    camarilla_s1: HitRateStatsResponse
    camarilla_s2: HitRateStatsResponse
    camarilla_s3: HitRateStatsResponse
    camarilla_s4: HitRateStatsResponse
    demark_pivot: DirectionalStatsResponse
    demark_resistance: HitRateStatsResponse
    demark_support: HitRateStatsResponse
    vwap: DirectionalStatsResponse
    adr: ADRStatsResponse
    opening_range: OpeningRangeStatsResponse


class DayReportsRequest(BaseModel):
    symbol: str
    dates: list[str]


class LevelOutcomeResponse(BaseModel):
    level: float
    touched: bool
    outcome: str


class DirectionalOutcomeResponse(BaseModel):
    level: float
    closed_above: bool


class ADROutcomeResponse(BaseModel):
    adr: float
    expected_high: float
    expected_low: float
    outcome: str


class OpeningRangeOutcomeResponse(BaseModel):
    high: float
    low: float
    outcome: str
    stayed_inside_all_day: bool


class DayLevelsReportResponse(BaseModel):
    date: str
    session_open: float
    session_high: float
    session_low: float
    session_close: float
    prior_close: float | None
    gap_pct: float | None
    levels_touched_count: int
    levels_held_count: int
    levels_broken_count: int
    prior_day_high: LevelOutcomeResponse | None
    prior_day_low: LevelOutcomeResponse | None
    pivot_point: DirectionalOutcomeResponse | None
    pivot_r1: LevelOutcomeResponse | None
    pivot_r2: LevelOutcomeResponse | None
    pivot_r3: LevelOutcomeResponse | None
    pivot_s1: LevelOutcomeResponse | None
    pivot_s2: LevelOutcomeResponse | None
    pivot_s3: LevelOutcomeResponse | None
    camarilla_r1: LevelOutcomeResponse | None
    camarilla_r2: LevelOutcomeResponse | None
    camarilla_r3: LevelOutcomeResponse | None
    camarilla_r4: LevelOutcomeResponse | None
    camarilla_s1: LevelOutcomeResponse | None
    camarilla_s2: LevelOutcomeResponse | None
    camarilla_s3: LevelOutcomeResponse | None
    camarilla_s4: LevelOutcomeResponse | None
    demark_pivot: DirectionalOutcomeResponse | None
    demark_resistance: LevelOutcomeResponse | None
    demark_support: LevelOutcomeResponse | None
    vwap: DirectionalOutcomeResponse | None
    adr: ADROutcomeResponse | None
    opening_range: OpeningRangeOutcomeResponse | None


class DayReportsResponse(BaseModel):
    symbol: str
    reports: list[DayLevelsReportResponse]
    dates_not_found: list[str]


class DailyLevelsResponse(BaseModel):
    symbol: str
    as_of: datetime
    current_price: float
    session_open: float
    prior_close: float
    prior_high: float
    prior_low: float
    gap_pct: float
    opening_range_high: float | None
    opening_range_low: float | None
    vwap: float | None
    adr: float | None
    adr_expected_high: float | None
    adr_expected_low: float | None
    pivot_points: dict[str, float | None]
    camarilla_pivots: dict[str, float | None]
    demark_pivots: dict[str, float | None]
    auto_support_resistance: list[float]
    fibonacci_retracement: dict[str, float | None]
