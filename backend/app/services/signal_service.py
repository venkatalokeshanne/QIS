"""
Signal Service.

Re-runs one strategy's entry/exit logic against the freshest bars for
a symbol+interval, the same way the levels service takes a live,
throwaway Tastytrade snapshot (see app.services.levels_service's
docstring) rather than a saved dataset. Reuses the exact backtest
execution engine (Strategy.run -> simulate_trades) so a "live" signal
is judged by identical logic to a backtest, not a re-implementation
that could quietly drift from it.

A signal is only "new" if the entry or exit it produced actually lands
on the LAST bar of the freshest fetch -- everything earlier already
happened and would have been reported by a prior poll.
"""

from dataclasses import dataclass, replace

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv
from app.data.validator import validate_ohlcv
from app.domain.interfaces.strategy import TradeDirection
from app.integrations import tastytrade_client
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import get_strategy

# End-of-data force-closes are an artifact of where the fetch window
# happened to end, not a real exit signal -- excluded from "new event"
# detection below.
_ARTIFICIAL_EXIT_REASON = "end_of_data"

# A live fetch window always ends at "now", not at the real end of the
# trading session -- simulate_trades' own forced_close_at_session_end
# groups by calendar date, so it would otherwise treat every freshest
# bar as "last bar of the session" and spuriously force-close open
# positions on every single check. Forced off in check_signal/
# live_signal_engine regardless of what a caller's execution_config
# says; the always-present unconditional end-of-data closure (excluded
# above) is what actually represents "nothing new happened," and real
# strategy exit signals still fire normally through generate_exits.
# Fallback default when no execution_config is supplied at all (e.g. a
# watch created before execution-settings snapshotting existed).
LIVE_EXECUTION_CONFIG = ExecutionConfig(force_close_at_session_end=False)

# Enough warm-up room for every strategy's slowest indicator (longest
# moving averages / lookback periods in use) at any supported interval.
# Public: app.services.live_signal_engine fetches the same initial
# warm-up window for its cached historical bars.
OUTPUTSIZE = 500


@dataclass(frozen=True)
class SignalCheck:
    symbol: str
    interval: str
    strategy_name: str
    as_of: pd.Timestamp
    price: float
    event: str | None  # "entry" | "exit" | None (no new signal on the latest bar)
    direction: str | None  # TradeDirection value, only set when event == "entry"
    exit_reason: str | None  # only set when event == "exit"


def fetch_symbol_bars(
    symbol: str, interval: str, fetch_bars=tastytrade_client.fetch_historical_bars
) -> pd.DataFrame:
    raw = fetch_bars(symbol, interval=interval, outputsize=OUTPUTSIZE)
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Received unusable bars for '{symbol}' from the live data source.", issues=report.errors)
    return normalized


def event_for_bar(trades: list, bar_time) -> tuple[str | None, str | None, str | None]:
    """
    Does the LAST trade produced by a strategy run land exactly on
    `bar_time` as either its entry or its exit? Shared by check_signal
    (the on-demand snapshot the Live Signal tab polls) and
    app.services.live_signal_engine (the live, event-driven alerting
    path) so "what counts as a new signal" can never drift between the
    two -- everything earlier than the last trade already happened and
    would have been reported already.

    Returns (event, direction, exit_reason), each None when nothing new
    landed on this bar.
    """
    if not trades:
        return None, None, None

    last_trade = trades[-1]
    if last_trade.entry_time == bar_time:
        direction = (
            last_trade.direction.value
            if isinstance(last_trade.direction, TradeDirection)
            else last_trade.direction
        )
        return "entry", direction, None
    if last_trade.exit_time == bar_time and last_trade.exit_reason != _ARTIFICIAL_EXIT_REASON:
        return "exit", None, last_trade.exit_reason
    return None, None, None


def check_signal(
    symbol: str,
    interval: str,
    strategy_name: str,
    strategy_params: dict,
    fetch_bars=tastytrade_client.fetch_historical_bars,
    execution_config: ExecutionConfig | None = None,
    cached_df: pd.DataFrame | None = None,
) -> SignalCheck:
    """
    `execution_config`, when given, should reflect the SAME risk/sizing
    settings a backtest would use (stop loss, take profit, direction
    filter, etc.) so a live check's entries/exits match what a backtest
    with those settings would have produced. force_close_at_session_end
    is always overridden to False regardless of what's passed in --
    see LIVE_EXECUTION_CONFIG's comment for why. Omit entirely to fall
    back to bare defaults (pre-existing behavior).

    `cached_df`, when given (app.services.live_signal_engine's already-
    subscribed, continuously live-updated bars for this symbol+
    interval), is used instead of opening a brand-new short-lived
    DXLink connection via fetch_bars -- avoids hammering Tastytrade
    with a fresh connection on every single poll for symbols already
    being tracked live.
    """
    df = cached_df if cached_df is not None else fetch_symbol_bars(symbol, interval, fetch_bars=fetch_bars)
    strategy = get_strategy(strategy_name)
    params = strategy.validate_params(strategy_params)
    config = replace(execution_config or ExecutionConfig(), force_close_at_session_end=False)
    trades = strategy.run(df, params, config)

    last_bar_time = df.index[-1]
    last_price = float(df["close"].iloc[-1])
    event, direction, exit_reason = event_for_bar(trades, last_bar_time)

    return SignalCheck(
        symbol=symbol.upper(),
        interval=interval,
        strategy_name=strategy_name,
        as_of=last_bar_time,
        price=last_price,
        event=event,
        direction=direction,
        exit_reason=exit_reason,
    )
