"""
Levels Backtest Service.

Answers "historically, how reliable have these levels actually been
for this stock?" -- fetches the freshest available bars for a symbol
(same live Tastytrade path the Daily Levels snapshot uses, see
app.services.levels_service), runs the SAME indicators across that
whole window (every level here is computed from data known strictly
BEFORE the session it applies to -- prior-session pivots, trailing ADR
-- so there's no lookahead), then measures how often price actually
touched/respected/broke each level across every session fetched.

Auto Support/Resistance and Fibonacci Retracement are intentionally
excluded here (unlike the live snapshot) -- their rolling lookback
windows can straddle INTO the same session being evaluated on intraday
bar counts, which would leak same-day information into what's supposed
to be a "known before today" level.
"""

from dataclasses import dataclass, field

import pandas as pd

from app.indicators.adr import AverageDailyRange
from app.indicators.camarilla_pivots import CamarillaPivots
from app.indicators.demark_pivots import DeMarkPivots
from app.indicators.pivot_points import PivotPoints
from app.indicators.session_opening_range import SessionOpeningRange
from app.indicators.vwap import VWAP
from app.integrations import tastytrade_client
from app.services.levels_service import fetch_symbol_bars

_ADR_PERIOD = 14
_OPENING_RANGE_MINUTES = 15

# The resistance/support level "families" (beyond prior-day H/L, which
# is handled separately since it isn't a column produced by an
# indicator here) that count toward the single overall success-rate
# headline stat -- directional references (the pivot itself, VWAP) and
# ADR/opening-range containment are excluded since "held vs broken"
# isn't a meaningful frame for them.
_RESISTANCE_SUPPORT_COLUMNS: list[tuple[str, str]] = [
    ("pivot_r1", "resistance"),
    ("pivot_r2", "resistance"),
    ("pivot_r3", "resistance"),
    ("pivot_s1", "support"),
    ("pivot_s2", "support"),
    ("pivot_s3", "support"),
    ("camarilla_r1", "resistance"),
    ("camarilla_r2", "resistance"),
    ("camarilla_r3", "resistance"),
    ("camarilla_r4", "resistance"),
    ("camarilla_s1", "support"),
    ("camarilla_s2", "support"),
    ("camarilla_s3", "support"),
    ("camarilla_s4", "support"),
    ("demark_resistance", "resistance"),
    ("demark_support", "support"),
]


@dataclass(frozen=True)
class HitRateStats:
    """How often price touched a resistance/support level, and of those
    touches, how often it held (rejected) vs broke through."""

    sample_days: int
    touched_pct: float | None
    held_pct: float | None
    broken_pct: float | None


@dataclass(frozen=True)
class DirectionalStats:
    """For a reference level with no inherent support/resistance side
    (the pivot itself, VWAP) -- just where price ended up relative to it."""

    sample_days: int
    closed_above_pct: float | None


@dataclass(frozen=True)
class ADRStats:
    sample_days: int
    contained_pct: float | None
    exceeded_upside_pct: float | None
    exceeded_downside_pct: float | None


@dataclass(frozen=True)
class OpeningRangeStats:
    sample_days: int
    closed_above_range_pct: float | None
    closed_below_range_pct: float | None
    stayed_inside_range_pct: float | None


@dataclass(frozen=True)
class LevelOutcome:
    """A single resistance/support level's actual outcome on one specific day."""

    level: float
    touched: bool
    outcome: str  # "held" | "broken" | "untouched"


@dataclass(frozen=True)
class DirectionalOutcome:
    level: float
    closed_above: bool


@dataclass(frozen=True)
class ADROutcome:
    adr: float
    expected_high: float
    expected_low: float
    outcome: str  # "contained" | "exceeded_upside" | "exceeded_downside" | "exceeded_both"


@dataclass(frozen=True)
class OpeningRangeOutcome:
    high: float
    low: float
    outcome: str  # "closed_above" | "closed_below" | "closed_inside"
    stayed_inside_all_day: bool


@dataclass(frozen=True)
class DayLevelsReport:
    """One specific historical day: the levels that were known going
    into it, and exactly what price actually did against each one."""

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
    prior_day_high: LevelOutcome | None
    prior_day_low: LevelOutcome | None
    pivot_point: DirectionalOutcome | None
    pivot_r1: LevelOutcome | None
    pivot_r2: LevelOutcome | None
    pivot_r3: LevelOutcome | None
    pivot_s1: LevelOutcome | None
    pivot_s2: LevelOutcome | None
    pivot_s3: LevelOutcome | None
    camarilla_r1: LevelOutcome | None
    camarilla_r2: LevelOutcome | None
    camarilla_r3: LevelOutcome | None
    camarilla_r4: LevelOutcome | None
    camarilla_s1: LevelOutcome | None
    camarilla_s2: LevelOutcome | None
    camarilla_s3: LevelOutcome | None
    camarilla_s4: LevelOutcome | None
    demark_pivot: DirectionalOutcome | None
    demark_resistance: LevelOutcome | None
    demark_support: LevelOutcome | None
    vwap: DirectionalOutcome | None
    adr: ADROutcome | None
    opening_range: OpeningRangeOutcome | None


@dataclass(frozen=True)
class LevelsBacktestReport:
    symbol: str
    total_sessions: int
    available_dates: list[str]
    # The headline number: across every resistance/support level family
    # combined (pivots, Camarilla, DeMark -- NOT prior-day H/L, which is
    # reported separately since it's not a "produced level" the same way),
    # what fraction of the times price actually tested a level did it
    # hold rather than break through.
    overall_success_rate_pct: float | None
    overall_levels_touched: int
    overall_levels_held: int
    overall_levels_broken: int
    prior_day_high: HitRateStats
    prior_day_low: HitRateStats
    pivot_point: DirectionalStats
    pivot_r1: HitRateStats
    pivot_r2: HitRateStats
    pivot_r3: HitRateStats
    pivot_s1: HitRateStats
    pivot_s2: HitRateStats
    pivot_s3: HitRateStats
    camarilla_r1: HitRateStats
    camarilla_r2: HitRateStats
    camarilla_r3: HitRateStats
    camarilla_r4: HitRateStats
    camarilla_s1: HitRateStats
    camarilla_s2: HitRateStats
    camarilla_s3: HitRateStats
    camarilla_s4: HitRateStats
    demark_pivot: DirectionalStats
    demark_resistance: HitRateStats
    demark_support: HitRateStats
    vwap: DirectionalStats
    adr: ADRStats
    opening_range: OpeningRangeStats


def _session_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    session_date = pd.Series(df.index.date, index=df.index)
    return pd.DataFrame(
        {
            "open": df["open"].groupby(session_date).first(),
            "high": df["high"].groupby(session_date).max(),
            "low": df["low"].groupby(session_date).min(),
            "close": df["close"].groupby(session_date).last(),
        }
    )


def _per_session(df: pd.DataFrame, column: str) -> pd.Series:
    """A per-bar column that's constant across each session (every
    level indicator here holds one value per session) -- collapse to
    one row per session."""
    session_date = pd.Series(df.index.date, index=df.index)
    return df[column].groupby(session_date).first()


def _touch_counts(session_ohlc: pd.DataFrame, level_per_session: pd.Series, side: str) -> tuple[int, int, int]:
    """Raw (touched, held, broken) counts -- shared by _hit_rate_stats
    (per-level %) and the overall cross-level success rate (raw sums)."""
    valid = level_per_session.notna()
    days = session_ohlc.loc[valid]
    levels = level_per_session.loc[valid]
    if len(days) == 0:
        return 0, 0, 0

    if side == "resistance":
        touched = days["high"] >= levels
        broken = touched & (days["close"] >= levels)
    else:
        touched = days["low"] <= levels
        broken = touched & (days["close"] <= levels)
    held = touched & ~broken
    return int(touched.sum()), int(held.sum()), int(broken.sum())


def _hit_rate_stats(session_ohlc: pd.DataFrame, level_per_session: pd.Series, side: str) -> HitRateStats:
    sample_days = int(level_per_session.notna().sum())
    if sample_days == 0:
        return HitRateStats(sample_days=0, touched_pct=None, held_pct=None, broken_pct=None)

    touched_n, held_n, broken_n = _touch_counts(session_ohlc, level_per_session, side)
    return HitRateStats(
        sample_days=sample_days,
        touched_pct=float(touched_n / sample_days * 100),
        held_pct=(float(held_n / touched_n * 100) if touched_n else None),
        broken_pct=(float(broken_n / touched_n * 100) if touched_n else None),
    )


def _directional_stats(session_ohlc: pd.DataFrame, level_per_session: pd.Series) -> DirectionalStats:
    valid = level_per_session.notna()
    days = session_ohlc.loc[valid]
    levels = level_per_session.loc[valid]
    n = len(days)
    if n == 0:
        return DirectionalStats(sample_days=0, closed_above_pct=None)
    return DirectionalStats(sample_days=n, closed_above_pct=float((days["close"] > levels).mean() * 100))


def _adr_stats(session_ohlc: pd.DataFrame, adr_per_session: pd.Series) -> ADRStats:
    valid = adr_per_session.notna()
    days = session_ohlc.loc[valid]
    adr = adr_per_session.loc[valid]
    n = len(days)
    if n == 0:
        return ADRStats(sample_days=0, contained_pct=None, exceeded_upside_pct=None, exceeded_downside_pct=None)

    expected_high = days["open"] + adr
    expected_low = days["open"] - adr
    contained = (days["high"] <= expected_high) & (days["low"] >= expected_low)
    return ADRStats(
        sample_days=n,
        contained_pct=float(contained.mean() * 100),
        exceeded_upside_pct=float((days["high"] > expected_high).mean() * 100),
        exceeded_downside_pct=float((days["low"] < expected_low).mean() * 100),
    )


def _opening_range_stats(
    session_ohlc: pd.DataFrame, or_high_per_session: pd.Series, or_low_per_session: pd.Series
) -> OpeningRangeStats:
    valid = or_high_per_session.notna() & or_low_per_session.notna()
    days = session_ohlc.loc[valid]
    or_high = or_high_per_session.loc[valid]
    or_low = or_low_per_session.loc[valid]
    n = len(days)
    if n == 0:
        return OpeningRangeStats(
            sample_days=0, closed_above_range_pct=None, closed_below_range_pct=None, stayed_inside_range_pct=None
        )

    stayed_inside = (days["high"] <= or_high) & (days["low"] >= or_low)
    return OpeningRangeStats(
        sample_days=n,
        closed_above_range_pct=float((days["close"] > or_high).mean() * 100),
        closed_below_range_pct=float((days["close"] < or_low).mean() * 100),
        stayed_inside_range_pct=float(stayed_inside.mean() * 100),
    )


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    enriched = SessionOpeningRange().calculate(df, {"session": "new_york", "minutes": _OPENING_RANGE_MINUTES})
    enriched = VWAP().calculate(enriched, {})
    enriched = AverageDailyRange().calculate(enriched, {"period": _ADR_PERIOD})
    enriched = PivotPoints().calculate(enriched, {})
    enriched = CamarillaPivots().calculate(enriched, {})
    enriched = DeMarkPivots().calculate(enriched, {})
    return enriched


def run_levels_backtest(
    symbol: str, fetch_bars=tastytrade_client.fetch_historical_bars
) -> LevelsBacktestReport:
    df = fetch_symbol_bars(symbol, fetch_bars=fetch_bars)
    enriched = _enrich(df)

    session_ohlc = _session_ohlc(enriched)
    prior_high = session_ohlc["high"].shift(1)
    prior_low = session_ohlc["low"].shift(1)

    # VWAP at end-of-day is a same-day, progressively-known reference
    # (not a lookahead level) -- take each session's LAST vwap reading.
    session_date = pd.Series(enriched.index.date, index=enriched.index)
    vwap_end_of_day = enriched["vwap"].groupby(session_date).last()

    or_suffix = f"new_york_{_OPENING_RANGE_MINUTES}"

    # Overall success rate: sum raw touched/held/broken across prior-day
    # H/L plus every pivot/Camarilla/DeMark resistance-support level.
    overall_touched, overall_held, overall_broken = 0, 0, 0
    for level_series, side in [(prior_high, "resistance"), (prior_low, "support")] + [
        (_per_session(enriched, col), side) for col, side in _RESISTANCE_SUPPORT_COLUMNS
    ]:
        t, h, b = _touch_counts(session_ohlc, level_series, side)
        overall_touched += t
        overall_held += h
        overall_broken += b

    return LevelsBacktestReport(
        symbol=symbol.upper(),
        total_sessions=len(session_ohlc),
        available_dates=[d.isoformat() for d in session_ohlc.index],
        overall_success_rate_pct=(float(overall_held / overall_touched * 100) if overall_touched else None),
        overall_levels_touched=overall_touched,
        overall_levels_held=overall_held,
        overall_levels_broken=overall_broken,
        prior_day_high=_hit_rate_stats(session_ohlc, prior_high, "resistance"),
        prior_day_low=_hit_rate_stats(session_ohlc, prior_low, "support"),
        pivot_point=_directional_stats(session_ohlc, _per_session(enriched, "pivot_point")),
        pivot_r1=_hit_rate_stats(session_ohlc, _per_session(enriched, "pivot_r1"), "resistance"),
        pivot_r2=_hit_rate_stats(session_ohlc, _per_session(enriched, "pivot_r2"), "resistance"),
        pivot_r3=_hit_rate_stats(session_ohlc, _per_session(enriched, "pivot_r3"), "resistance"),
        pivot_s1=_hit_rate_stats(session_ohlc, _per_session(enriched, "pivot_s1"), "support"),
        pivot_s2=_hit_rate_stats(session_ohlc, _per_session(enriched, "pivot_s2"), "support"),
        pivot_s3=_hit_rate_stats(session_ohlc, _per_session(enriched, "pivot_s3"), "support"),
        camarilla_r1=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_r1"), "resistance"),
        camarilla_r2=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_r2"), "resistance"),
        camarilla_r3=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_r3"), "resistance"),
        camarilla_r4=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_r4"), "resistance"),
        camarilla_s1=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_s1"), "support"),
        camarilla_s2=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_s2"), "support"),
        camarilla_s3=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_s3"), "support"),
        camarilla_s4=_hit_rate_stats(session_ohlc, _per_session(enriched, "camarilla_s4"), "support"),
        demark_pivot=_directional_stats(session_ohlc, _per_session(enriched, "demark_pivot")),
        demark_resistance=_hit_rate_stats(session_ohlc, _per_session(enriched, "demark_resistance"), "resistance"),
        demark_support=_hit_rate_stats(session_ohlc, _per_session(enriched, "demark_support"), "support"),
        vwap=_directional_stats(session_ohlc, vwap_end_of_day),
        adr=_adr_stats(session_ohlc, _per_session(enriched, f"adr_{_ADR_PERIOD}")),
        opening_range=_opening_range_stats(
            session_ohlc,
            _per_session(enriched, f"session_or_high_{or_suffix}"),
            _per_session(enriched, f"session_or_low_{or_suffix}"),
        ),
    )


def _classify_level(day: pd.Series, level: float, side: str) -> LevelOutcome | None:
    if pd.isna(level):
        return None
    if side == "resistance":
        touched = bool(day["high"] >= level)
        broken = touched and day["close"] >= level
    else:
        touched = bool(day["low"] <= level)
        broken = touched and day["close"] <= level
    outcome = "untouched" if not touched else ("broken" if broken else "held")
    return LevelOutcome(level=float(level), touched=touched, outcome=outcome)


def _classify_directional(day: pd.Series, level: float) -> DirectionalOutcome | None:
    if pd.isna(level):
        return None
    return DirectionalOutcome(level=float(level), closed_above=bool(day["close"] > level))


def _classify_adr(day: pd.Series, adr: float) -> ADROutcome | None:
    if pd.isna(adr):
        return None
    expected_high = day["open"] + adr
    expected_low = day["open"] - adr
    exceeded_up = day["high"] > expected_high
    exceeded_down = day["low"] < expected_low
    if exceeded_up and exceeded_down:
        outcome = "exceeded_both"
    elif exceeded_up:
        outcome = "exceeded_upside"
    elif exceeded_down:
        outcome = "exceeded_downside"
    else:
        outcome = "contained"
    return ADROutcome(
        adr=float(adr), expected_high=float(expected_high), expected_low=float(expected_low), outcome=outcome
    )


def _classify_opening_range(day: pd.Series, or_high: float, or_low: float) -> OpeningRangeOutcome | None:
    if pd.isna(or_high) or pd.isna(or_low):
        return None
    if day["close"] > or_high:
        outcome = "closed_above"
    elif day["close"] < or_low:
        outcome = "closed_below"
    else:
        outcome = "closed_inside"
    stayed_inside = bool(day["high"] <= or_high and day["low"] >= or_low)
    return OpeningRangeOutcome(high=float(or_high), low=float(or_low), outcome=outcome, stayed_inside_all_day=stayed_inside)


def get_day_reports(
    symbol: str, dates: list[str], fetch_bars=tastytrade_client.fetch_historical_bars
) -> list[DayLevelsReport]:
    """
    The same levels as run_levels_backtest, but for specific individual
    days -- what were the levels, and exactly what did price do against
    each one that day (not an aggregate rate across the whole window).
    Dates outside the freshest fetched window simply won't appear in
    the result -- the caller can diff requested vs. returned dates.
    """
    df = fetch_symbol_bars(symbol, fetch_bars=fetch_bars)
    enriched = _enrich(df)
    session_ohlc = _session_ohlc(enriched)
    prior_high = session_ohlc["high"].shift(1)
    prior_low = session_ohlc["low"].shift(1)
    prior_close = session_ohlc["close"].shift(1)

    session_date_series = pd.Series(enriched.index.date, index=enriched.index)
    vwap_end_of_day = enriched["vwap"].groupby(session_date_series).last()

    or_suffix = f"new_york_{_OPENING_RANGE_MINUTES}"
    pivot_r1 = _per_session(enriched, "pivot_r1")
    pivot_r2 = _per_session(enriched, "pivot_r2")
    pivot_r3 = _per_session(enriched, "pivot_r3")
    pivot_s1 = _per_session(enriched, "pivot_s1")
    pivot_s2 = _per_session(enriched, "pivot_s2")
    pivot_s3 = _per_session(enriched, "pivot_s3")
    pivot_point = _per_session(enriched, "pivot_point")
    camarilla_r1 = _per_session(enriched, "camarilla_r1")
    camarilla_r2 = _per_session(enriched, "camarilla_r2")
    camarilla_r3 = _per_session(enriched, "camarilla_r3")
    camarilla_r4 = _per_session(enriched, "camarilla_r4")
    camarilla_s1 = _per_session(enriched, "camarilla_s1")
    camarilla_s2 = _per_session(enriched, "camarilla_s2")
    camarilla_s3 = _per_session(enriched, "camarilla_s3")
    camarilla_s4 = _per_session(enriched, "camarilla_s4")
    demark_pivot = _per_session(enriched, "demark_pivot")
    demark_resistance = _per_session(enriched, "demark_resistance")
    demark_support = _per_session(enriched, "demark_support")
    adr_series = _per_session(enriched, f"adr_{_ADR_PERIOD}")
    or_high_series = _per_session(enriched, f"session_or_high_{or_suffix}")
    or_low_series = _per_session(enriched, f"session_or_low_{or_suffix}")

    requested = {pd.Timestamp(d).date() for d in dates}
    reports: list[DayLevelsReport] = []

    for session_date in session_ohlc.index:
        if session_date not in requested:
            continue
        day = session_ohlc.loc[session_date]

        outcomes = [
            _classify_level(day, prior_high.get(session_date), "resistance"),
            _classify_level(day, prior_low.get(session_date), "support"),
            _classify_level(day, pivot_r1.get(session_date), "resistance"),
            _classify_level(day, pivot_r2.get(session_date), "resistance"),
            _classify_level(day, pivot_r3.get(session_date), "resistance"),
            _classify_level(day, pivot_s1.get(session_date), "support"),
            _classify_level(day, pivot_s2.get(session_date), "support"),
            _classify_level(day, pivot_s3.get(session_date), "support"),
            _classify_level(day, camarilla_r1.get(session_date), "resistance"),
            _classify_level(day, camarilla_r2.get(session_date), "resistance"),
            _classify_level(day, camarilla_r3.get(session_date), "resistance"),
            _classify_level(day, camarilla_r4.get(session_date), "resistance"),
            _classify_level(day, camarilla_s1.get(session_date), "support"),
            _classify_level(day, camarilla_s2.get(session_date), "support"),
            _classify_level(day, camarilla_s3.get(session_date), "support"),
            _classify_level(day, camarilla_s4.get(session_date), "support"),
            _classify_level(day, demark_resistance.get(session_date), "resistance"),
            _classify_level(day, demark_support.get(session_date), "support"),
        ]
        touched_count = sum(1 for o in outcomes if o and o.touched)
        held_count = sum(1 for o in outcomes if o and o.outcome == "held")
        broken_count = sum(1 for o in outcomes if o and o.outcome == "broken")

        prior_c = prior_close.get(session_date)
        gap_pct = (
            float((day["open"] - prior_c) / prior_c * 100) if prior_c is not None and not pd.isna(prior_c) else None
        )

        reports.append(
            DayLevelsReport(
                date=session_date.isoformat(),
                session_open=float(day["open"]),
                session_high=float(day["high"]),
                session_low=float(day["low"]),
                session_close=float(day["close"]),
                prior_close=(float(prior_c) if prior_c is not None and not pd.isna(prior_c) else None),
                gap_pct=gap_pct,
                levels_touched_count=touched_count,
                levels_held_count=held_count,
                levels_broken_count=broken_count,
                prior_day_high=outcomes[0],
                prior_day_low=outcomes[1],
                pivot_point=_classify_directional(day, pivot_point.get(session_date)),
                pivot_r1=outcomes[2],
                pivot_r2=outcomes[3],
                pivot_r3=outcomes[4],
                pivot_s1=outcomes[5],
                pivot_s2=outcomes[6],
                pivot_s3=outcomes[7],
                camarilla_r1=outcomes[8],
                camarilla_r2=outcomes[9],
                camarilla_r3=outcomes[10],
                camarilla_r4=outcomes[11],
                camarilla_s1=outcomes[12],
                camarilla_s2=outcomes[13],
                camarilla_s3=outcomes[14],
                camarilla_s4=outcomes[15],
                demark_pivot=_classify_directional(day, demark_pivot.get(session_date)),
                demark_resistance=outcomes[16],
                demark_support=outcomes[17],
                vwap=_classify_directional(day, vwap_end_of_day.get(session_date)),
                adr=_classify_adr(day, adr_series.get(session_date)),
                opening_range=_classify_opening_range(day, or_high_series.get(session_date), or_low_series.get(session_date)),
            )
        )

    return sorted(reports, key=lambda r: r.date)
