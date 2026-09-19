"""
Signal Service.

Fetches the freshest bars for a symbol+interval, the same way the
levels service takes a live, throwaway TwelveData snapshot (see
app.services.levels_service's docstring) rather than a saved dataset.
Shared by app.services.scanner_service and app.services.day_prep_service.
"""

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv
from app.data.validator import validate_ohlcv
from app.domain.interfaces.strategy import TradeDirection
from app.integrations import twelvedata_client

# Enough warm-up room for every strategy's slowest indicator (longest
# moving averages / lookback periods in use) at any supported interval.
OUTPUTSIZE = 500


def fetch_symbol_bars(
    symbol: str,
    interval: str,
    fetch_bars=twelvedata_client.fetch_historical_bars,
    include_extended_hours: bool = False,
    include_overnight: bool = False,
) -> pd.DataFrame:
    raw = fetch_bars(
        symbol,
        interval=interval,
        outputsize=OUTPUTSIZE,
        include_extended_hours=include_extended_hours,
        include_overnight=include_overnight,
    )
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Received unusable bars for '{symbol}' from the live data source.", issues=report.errors)
    normalized.attrs["symbol"] = symbol.upper()
    return normalized


def _trade_direction(trade) -> str:
    return trade.direction.value if isinstance(trade.direction, TradeDirection) else trade.direction
