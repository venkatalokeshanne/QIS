"""
Scanner Service.

Runs every requested strategy against every requested symbol and
reports back only the (symbol, strategy) combos that produced an entry
signal recently -- i.e. "what's flashing long or short right now
across my whole watchlist", rather than the single symbol+strategy
view signal_service.check_signal gives you. This is the engine behind
the "which tickers should I actually watch today" view -- see
Scanner.jsx's per-ticker grouping.

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
from datetime import date, timedelta
from typing import Any, Callable

import pandas as pd

from app.integrations import tastytrade_client
from app.metrics.calculator import calculate_all_metrics
from app.services.backtest_data import fetch_backtest_bars, historical_outputsize
from app.services.signal_service import _trade_direction, fetch_symbol_bars
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import get_strategy, list_strategies

# How many of the most recent bars count as "recent" for a scan match.
# 1 would only catch a signal on the single freshest bar (easy to miss
# between scans); a small window still means "acted on very recently"
# without drowning the results in stale entries.
DEFAULT_LOOKBACK_BARS = 3

# "Is this strategy actually good on this ticker, or did it just
# happen to fire" -- a trailing-year trust check run ONLY for the
# (symbol, strategy) pairs that actually matched (a handful, not the
# full symbols x strategies cross product), so it stays cheap. Shorter
# than backtest_routes' 5-year "historical performance" window since
# this only needs to answer "is it worth watching," not deep multi-
# regime validation -- the user can always open the full backtest for
# that.
HISTORICAL_LOOKBACK_DAYS = 365
HISTORICAL_MAX_OUTPUTSIZE = 20_000


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
    # Trailing-year trust check for this exact symbol+strategy (see
    # HISTORICAL_LOOKBACK_DAYS) -- None when it couldn't be computed
    # (fetch failed) rather than a fabricated 0.
    historical_trade_count: int | None = None
    historical_win_rate: float | None = None
    historical_profit_factor: float | None = None
    historical_net_profit: float | None = None


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


def _attach_historical_trust(
    results: list[ScanResult],
    interval: str,
    strategy_params_by_name: dict[str, dict[str, Any]],
    execution_config: ExecutionConfig,
    fetch_bars,
) -> list[ScanResult]:
    """For every matched (symbol, strategy), run that strategy over a
    trailing-year window and attach win-rate/profit-factor/trade-count
    -- "does this setup actually have a track record, or is this its
    first time firing." Historical bars are fetched once per SYMBOL
    (not once per match) and reused across every strategy matched on
    that symbol, same principle as the live scan's own bar fetch."""
    if not results:
        return results

    outputsize = historical_outputsize(interval, HISTORICAL_LOOKBACK_DAYS, HISTORICAL_MAX_OUTPUTSIZE)
    start_date = (date.today() - timedelta(days=HISTORICAL_LOOKBACK_DAYS)).isoformat()
    end_date = date.today().isoformat()
    run_config = replace(execution_config, force_close_at_session_end=False)

    historical_df_by_symbol: dict[str, pd.DataFrame | None] = {}
    enriched: list[ScanResult] = []

    for r in results:
        if r.symbol not in historical_df_by_symbol:
            try:
                historical_df_by_symbol[r.symbol] = fetch_backtest_bars(
                    r.symbol,
                    interval,
                    start_date=start_date,
                    end_date=end_date,
                    outputsize=outputsize,
                    fetch_bars=fetch_bars,
                )
            except Exception:
                historical_df_by_symbol[r.symbol] = None

        hdf = historical_df_by_symbol[r.symbol]
        if hdf is None or hdf.empty:
            enriched.append(r)
            continue

        try:
            strategy = get_strategy(r.strategy_name)
            params = strategy.validate_params(strategy_params_by_name.get(r.strategy_name, {}))
            trades = strategy.run(hdf, params, run_config)
        except Exception:
            enriched.append(r)
            continue

        metrics = calculate_all_metrics(trades, execution_config.capital)
        enriched.append(
            replace(
                r,
                historical_trade_count=len(trades),
                historical_win_rate=metrics.get("win_rate"),
                historical_profit_factor=metrics.get("profit_factor"),
                historical_net_profit=metrics.get("net_profit"),
            )
        )

    return enriched


def scan_for_signals(
    symbols: list[str],
    interval: str,
    strategy_names: list[str] | None = None,
    strategy_params_by_name: dict[str, dict[str, Any]] | None = None,
    execution_config: ExecutionConfig | None = None,
    lookback_bars: int = DEFAULT_LOOKBACK_BARS,
    fetch_bars=tastytrade_client.fetch_historical_bars,
    get_cached_bars: Callable[[str, str], pd.DataFrame | None] | None = None,
    include_historical_trust: bool = True,
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

    if include_historical_trust:
        results = _attach_historical_trust(results, interval, strategy_params_by_name, config, fetch_bars)

    return results, failed_symbols
