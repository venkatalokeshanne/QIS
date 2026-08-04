"""
Scanner Service.

Runs every requested strategy against every requested symbol and
reports back only the (symbol, strategy) combos that produced an entry
signal recently -- i.e. "what's flashing long or short right now
across my whole watchlist", rather than the single symbol+strategy
view signal_service.check_signal gives you.

Reuses the exact same fetch + Strategy.run path as check_signal (same
bars, same execution engine) so a scan match is judged identically to
what the Live Signal tab or a backtest would have produced -- this
module only adds the "loop over many symbols/strategies and keep the
recent ones" layer on top.

Bars are fetched ONCE per symbol (not once per symbol+strategy) and
reused across every strategy run against that symbol -- a strategy run
is a cheap in-memory pandas operation, the network fetch is not.
"""

from dataclasses import dataclass, replace
from typing import Any, Callable

import pandas as pd

from app.integrations import tastytrade_client
from app.services.signal_service import _trade_direction, fetch_symbol_bars
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import get_strategy, list_strategies

# How many of the most recent bars count as "recent" for a scan match.
# 1 would only catch a signal on the single freshest bar (easy to miss
# between scans); a small window still means "acted on very recently"
# without drowning the results in stale entries.
DEFAULT_LOOKBACK_BARS = 3


@dataclass(frozen=True)
class ScanResult:
    symbol: str
    strategy_name: str
    strategy_display_name: str
    interval: str
    as_of: pd.Timestamp
    price: float
    signal_direction: str  # "long" | "short"
    signal_time: pd.Timestamp
    bars_ago: int  # 0 == the freshest bar
    still_active: bool  # True if the trade this signal opened hasn't exited yet


def _most_recent_entry(trades: list, df: pd.DataFrame, lookback_bars: int) -> tuple | None:
    """The latest trade (if any) whose entry landed within the last
    `lookback_bars` bars of `df`. Returns (trade, bars_ago) or None."""
    if not trades or lookback_bars <= 0:
        return None
    last_index = len(df.index) - 1
    for trade in reversed(trades):
        try:
            entry_loc = df.index.get_loc(trade.entry_time)
        except KeyError:
            continue
        bars_ago = last_index - entry_loc
        if 0 <= bars_ago < lookback_bars:
            return trade, bars_ago
        if bars_ago >= lookback_bars:
            # Trades are in chronological order -- once we're past the
            # lookback window, nothing older can qualify either.
            break
    return None


def scan_for_signals(
    symbols: list[str],
    interval: str,
    strategy_names: list[str] | None = None,
    strategy_params_by_name: dict[str, dict[str, Any]] | None = None,
    execution_config: ExecutionConfig | None = None,
    lookback_bars: int = DEFAULT_LOOKBACK_BARS,
    fetch_bars=tastytrade_client.fetch_historical_bars,
    get_cached_bars: Callable[[str, str], pd.DataFrame | None] | None = None,
) -> tuple[list[ScanResult], list[str]]:
    """
    Returns (results, failed_symbols). `results` is sorted most-recent-
    signal-first (bars_ago ascending), then symbol, then strategy name.
    `failed_symbols` lists any symbol whose bars couldn't be fetched
    (bad ticker, no data, etc.) -- scanning the rest continues rather
    than failing the whole scan.
    """
    strategy_meta = list_strategies()
    names = strategy_names or [meta["name"] for meta in strategy_meta]
    display_names = {meta["name"]: meta["display_name"] for meta in strategy_meta}
    strategy_params_by_name = strategy_params_by_name or {}
    config = execution_config or ExecutionConfig()

    results: list[ScanResult] = []
    failed_symbols: list[str] = []

    for raw_symbol in symbols:
        symbol = raw_symbol.upper()
        try:
            cached = get_cached_bars(symbol, interval) if get_cached_bars else None
            if cached is not None:
                df = tastytrade_client.filter_by_session(cached, config.include_extended_hours, config.include_overnight)
            else:
                df = fetch_symbol_bars(
                    symbol,
                    interval,
                    fetch_bars=fetch_bars,
                    include_extended_hours=config.include_extended_hours,
                    include_overnight=config.include_overnight,
                )
        except Exception:
            failed_symbols.append(symbol)
            continue

        if df.empty:
            failed_symbols.append(symbol)
            continue

        as_of = df.index[-1]
        price = float(df["close"].iloc[-1])
        run_config = replace(config, force_close_at_session_end=False)

        for name in names:
            try:
                strategy = get_strategy(name)
                params = strategy.validate_params(strategy_params_by_name.get(name, {}))
                trades = strategy.run(df, params, run_config)
            except Exception:
                continue

            match = _most_recent_entry(trades, df, lookback_bars)
            if match is None:
                continue
            trade, bars_ago = match

            results.append(
                ScanResult(
                    symbol=symbol,
                    strategy_name=name,
                    strategy_display_name=display_names.get(name, name),
                    interval=interval,
                    as_of=as_of,
                    price=price,
                    signal_direction=_trade_direction(trade),
                    signal_time=trade.entry_time,
                    bars_ago=bars_ago,
                    still_active=trade.exit_time is None,
                )
            )

    results.sort(key=lambda r: (r.bars_ago, r.symbol, r.strategy_name))
    return results, failed_symbols
