"""
Levels Service.

Fetches the freshest available bars for a symbol through the same
Twelve Data integration used for dataset imports (detect -> normalize
-> validate), but does NOT persist a dataset -- this is a live,
throwaway snapshot, not something meant to be saved and re-run later.
Runs a curated set of already-built indicators against those bars and
distills them into a single "important levels for today" report.

This is a REST-polled snapshot (Twelve Data's /time_series endpoint),
not a tick-level live feed -- "as of" reflects the most recent bar
Twelve Data had available at fetch time, not literal real-time.
"""

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv
from app.data.validator import validate_ohlcv
from app.indicators.adr import AverageDailyRange
from app.indicators.auto_support_resistance import AutoSupportResistance
from app.indicators.camarilla_pivots import CamarillaPivots
from app.indicators.demark_pivots import DeMarkPivots
from app.indicators.fibonacci_retracement import FibonacciRetracement
from app.indicators.pivot_points import PivotPoints
from app.indicators.session_opening_range import SessionOpeningRange
from app.indicators.vwap import VWAP
from app.integrations import twelvedata_client

_OPENING_RANGE_MINUTES = 15
_ADR_PERIOD = 14
_FIBONACCI_PERIOD = 50


@dataclass(frozen=True)
class DailyLevels:
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
    auto_support_resistance: list[float] = field(default_factory=list)
    fibonacci_retracement: dict[str, float | None] = field(default_factory=dict)


def fetch_symbol_bars(symbol: str, fetch_bars=twelvedata_client.fetch_historical_bars) -> pd.DataFrame:
    """
    Same detect -> normalize -> validate pipeline a Twelve-Data dataset
    import uses (see app.services.dataset_service), just not persisted.
    5-minute bars, max page size -- ~2-3 months of history, enough
    warm-up room for ADR's 14-session lookback and every other
    indicator here, in a single API call.
    """
    raw = fetch_bars(symbol, interval="5min", outputsize=5000)
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Twelve Data returned unusable bars for '{symbol}'.", issues=report.errors)
    return normalized


def _prior_and_current_session_ohlc(df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp, pd.Series, pd.Series]:
    session_date = pd.Series(df.index.date, index=df.index)
    daily_high = df["high"].groupby(session_date).transform("max")
    daily_low = df["low"].groupby(session_date).transform("min")
    daily_close = df["close"].groupby(session_date).transform("last")
    daily_open = df["open"].groupby(session_date).transform("first")

    per_session = pd.DataFrame(
        {
            "high": daily_high.groupby(session_date).first(),
            "low": daily_low.groupby(session_date).first(),
            "close": daily_close.groupby(session_date).first(),
            "open": daily_open.groupby(session_date).first(),
        }
    )
    if len(per_session) < 2:
        raise DataValidationError("Not enough sessions of data to compute prior-day levels yet.")

    current_session, prior_session = per_session.index[-1], per_session.index[-2]
    return current_session, prior_session, per_session.loc[current_session], per_session.loc[prior_session]


def _safe(value) -> float | None:
    return None if pd.isna(value) else float(value)


def get_daily_levels(symbol: str, fetch_bars=twelvedata_client.fetch_historical_bars) -> DailyLevels:
    df = fetch_symbol_bars(symbol, fetch_bars=fetch_bars)

    enriched = SessionOpeningRange().calculate(df, {"session": "new_york", "minutes": _OPENING_RANGE_MINUTES})
    enriched = VWAP().calculate(enriched, {})
    enriched = AverageDailyRange().calculate(enriched, {"period": _ADR_PERIOD})
    enriched = PivotPoints().calculate(enriched, {})
    enriched = CamarillaPivots().calculate(enriched, {})
    enriched = DeMarkPivots().calculate(enriched, {})
    enriched = AutoSupportResistance().calculate(enriched, {})
    enriched = FibonacciRetracement().calculate(enriched, {"period": _FIBONACCI_PERIOD})

    _, _, current_ohlc, prior_ohlc = _prior_and_current_session_ohlc(enriched)
    latest = enriched.iloc[-1]
    as_of = enriched.index[-1]

    session_open = float(current_ohlc["open"])
    prior_close = float(prior_ohlc["close"])
    current_price = float(latest["close"])
    gap_pct = (session_open - prior_close) / prior_close * 100

    or_suffix = f"new_york_{_OPENING_RANGE_MINUTES}"
    adr = _safe(latest[f"adr_{_ADR_PERIOD}"])

    return DailyLevels(
        symbol=symbol.upper(),
        as_of=as_of.to_pydatetime(),
        current_price=current_price,
        session_open=session_open,
        prior_close=prior_close,
        prior_high=float(prior_ohlc["high"]),
        prior_low=float(prior_ohlc["low"]),
        gap_pct=gap_pct,
        opening_range_high=_safe(latest[f"session_or_high_{or_suffix}"]),
        opening_range_low=_safe(latest[f"session_or_low_{or_suffix}"]),
        vwap=_safe(latest["vwap"]),
        adr=adr,
        adr_expected_high=(session_open + adr) if adr is not None else None,
        adr_expected_low=(session_open - adr) if adr is not None else None,
        pivot_points={
            "s3": _safe(latest["pivot_s3"]),
            "s2": _safe(latest["pivot_s2"]),
            "s1": _safe(latest["pivot_s1"]),
            "pivot": _safe(latest["pivot_point"]),
            "r1": _safe(latest["pivot_r1"]),
            "r2": _safe(latest["pivot_r2"]),
            "r3": _safe(latest["pivot_r3"]),
        },
        camarilla_pivots={
            "s4": _safe(latest["camarilla_s4"]),
            "s3": _safe(latest["camarilla_s3"]),
            "s2": _safe(latest["camarilla_s2"]),
            "s1": _safe(latest["camarilla_s1"]),
            "r1": _safe(latest["camarilla_r1"]),
            "r2": _safe(latest["camarilla_r2"]),
            "r3": _safe(latest["camarilla_r3"]),
            "r4": _safe(latest["camarilla_r4"]),
        },
        demark_pivots={
            "support": _safe(latest["demark_support"]),
            "pivot": _safe(latest["demark_pivot"]),
            "resistance": _safe(latest["demark_resistance"]),
        },
        auto_support_resistance=sorted(
            v for v in (_safe(latest[f"auto_sr_level_{i}"]) for i in range(1, 6)) if v is not None
        ),
        fibonacci_retracement={
            "236": _safe(latest["fib_retracement_236"]),
            "382": _safe(latest["fib_retracement_382"]),
            "50": _safe(latest["fib_retracement_5"]),
            "618": _safe(latest["fib_retracement_618"]),
            "786": _safe(latest["fib_retracement_786"]),
        },
    )
