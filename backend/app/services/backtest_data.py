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


def fetch_backtest_bars(
    symbol: str,
    interval: str,
    start_date: str | None = None,
    end_date: str | None = None,
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
    """
    fetch_start_date = start_date
    if start_date:
        fetch_start_date = (pd.Timestamp(start_date) - pd.Timedelta(days=WARMUP_CALENDAR_DAYS)).date().isoformat()
    raw = fetch_bars(symbol, interval=interval, outputsize=5000, start_date=fetch_start_date, end_date=end_date)
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Received unusable bars for '{symbol}' from the live data source.", issues=report.errors)
    return normalized
