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
    Run Backtests stay optional rather than required.
    """
    raw = fetch_bars(symbol, interval=interval, outputsize=5000, start_date=start_date, end_date=end_date)
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Received unusable bars for '{symbol}' from the live data source.", issues=report.errors)
    return normalized
