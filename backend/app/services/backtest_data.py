"""
Backtest Data.

Fetches the bars a backtest runs against live, via Tastytrade (see
app.integrations.tastytrade_client.fetch_historical_bars) -- there's no
persisted "dataset" anymore. Same detect -> normalize -> validate
pipeline every other bar source in this app uses (see
app.services.levels_service.fetch_symbol_bars for the live-snapshot
sibling of this), just parameterized for an arbitrary interval and
optional date range instead of levels' fixed 5-minute lookback.

No caching -- every backtest run fetches fresh, same as Live Signal and
Daily Levels already do.
"""

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv
from app.data.validator import validate_ohlcv
from app.integrations import tastytrade_client

# A narrow (e.g. single-day) start_date would otherwise be fetched
# with NO bars before it -- starving every indicator/zone-tracking
# strategy (order blocks, ATR, moving averages, ...) of the warm-up
# history it needs, and silently producing different signals than the
# same day would show inside a wider range or Live Signal's own
# always-generous window (see signal_service.OUTPUTSIZE). Fetching
# this many extra calendar days before start_date and letting
# app.services.strategy_runner trim the resulting TRADES (not the
# bars) back to the requested window is what keeps "10 trades in a
# 1-day backtest" from ever meaning "the strategy behaved differently
# for narrower ranges."
WARMUP_CALENDAR_DAYS = 45

# Rough bars-per-session estimate per interval, used to size a
# generous-but-bounded `outputsize` for a calendar-day lookback window
# -- shared by backtest_routes' multi-year "historical performance"
# fetch and scanner_service's shorter "is this strategy actually good
# on this ticker" trust check, so a wide date range doesn't silently
# collapse to whatever tiny recent slice fits in a small default
# outputsize (see fetch_historical_bars' own outputsize contract).
_BARS_PER_SESSION = {"1min": 390, "5min": 78, "15min": 26, "30min": 13, "1h": 7, "1day": 1}


def historical_outputsize(interval: str, lookback_days: int, max_outputsize: int) -> int:
    trading_days = int(lookback_days * 5 / 7)  # rough weekday fraction of calendar days
    bars_per_session = _BARS_PER_SESSION.get(interval, 78)
    return min(max_outputsize, trading_days * bars_per_session)


def fetch_backtest_bars(
    symbol: str,
    interval: str,
    start_date: str | None = None,
    end_date: str | None = None,
    include_extended_hours: bool = False,
    include_overnight: bool = False,
    outputsize: int = 5000,
    fetch_bars=tastytrade_client.fetch_historical_bars,
) -> pd.DataFrame:
    """
    Fetch and validate historical bars for a backtest.

    `start_date`/`end_date` are an optional override -- when omitted,
    `fetch_historical_bars`'s own lookback heuristic already produces a
    generous default range, which is what lets the date-range picker on
    Run Backtests stay optional rather than required. When `start_date`
    IS given, bars are actually fetched from WARMUP_CALENDAR_DAYS
    earlier -- see that constant's comment.

    `include_extended_hours`/`include_overnight` are passed straight
    through to fetch_bars -- see tastytrade_client.filter_by_session.

    `outputsize` defaults to a plain backtest's usual 5000, but a wide
    date range (e.g. backtest_routes' multi-year "historical
    performance" fetch) needs a much larger override -- otherwise
    fetch_historical_bars silently keeps only the freshest 5000 bars
    and a requested multi-year window collapses to whatever tiny slice
    of it that caps out to for an intraday interval.
    """
    fetch_start_date = start_date
    if start_date:
        fetch_start_date = (pd.Timestamp(start_date) - pd.Timedelta(days=WARMUP_CALENDAR_DAYS)).date().isoformat()
    raw = fetch_bars(
        symbol,
        interval=interval,
        outputsize=outputsize,
        start_date=fetch_start_date,
        end_date=end_date,
        include_extended_hours=include_extended_hours,
        include_overnight=include_overnight,
    )
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Received unusable bars for '{symbol}' from the live data source.", issues=report.errors)
    return normalized
