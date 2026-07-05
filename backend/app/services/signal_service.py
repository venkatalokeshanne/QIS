"""
Signal Service.

Re-runs one strategy's entry/exit logic against the freshest bars for
a symbol+interval, the same way the levels service takes a live,
throwaway Twelve Data snapshot (see app.services.levels_service's
docstring) rather than a saved dataset. Reuses the exact backtest
execution engine (Strategy.run -> simulate_trades) so a "live" signal
is judged by identical logic to a backtest, not a re-implementation
that could quietly drift from it.

A signal is only "new" if the entry or exit it produced actually lands
on the LAST bar of the freshest fetch -- everything earlier already
happened and would have been reported by a prior poll.
"""

from dataclasses import dataclass

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv
from app.data.validator import validate_ohlcv
from app.domain.interfaces.strategy import TradeDirection
from app.integrations import twelvedata_client
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
# positions on every single check. Disabled here; the always-present
# unconditional end-of-data closure (excluded above) is what actually
# represents "nothing new happened," and real strategy exit signals
# still fire normally through generate_exits.
_LIVE_EXECUTION_CONFIG = ExecutionConfig(force_close_at_session_end=False)

# Enough warm-up room for every strategy's slowest indicator (longest
# moving averages / lookback periods in use) at any supported interval.
_OUTPUTSIZE = 500


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
    symbol: str, interval: str, fetch_bars=twelvedata_client.fetch_historical_bars
) -> pd.DataFrame:
    raw = fetch_bars(symbol, interval=interval, outputsize=_OUTPUTSIZE)
    detection = detect_columns(raw)
    normalized = normalize_ohlcv(raw, detection)
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Twelve Data returned unusable bars for '{symbol}'.", issues=report.errors)
    return normalized


def check_signal(
    symbol: str,
    interval: str,
    strategy_name: str,
    strategy_params: dict,
    fetch_bars=twelvedata_client.fetch_historical_bars,
) -> SignalCheck:
    df = fetch_symbol_bars(symbol, interval, fetch_bars=fetch_bars)
    strategy = get_strategy(strategy_name)
    params = strategy.validate_params(strategy_params)
    trades = strategy.run(df, params, _LIVE_EXECUTION_CONFIG)

    last_bar_time = df.index[-1]
    last_price = float(df["close"].iloc[-1])

    event = None
    direction = None
    exit_reason = None

    if trades:
        last_trade = trades[-1]
        if last_trade.entry_time == last_bar_time:
            event = "entry"
            direction = last_trade.direction.value if isinstance(last_trade.direction, TradeDirection) else last_trade.direction
        elif last_trade.exit_time == last_bar_time and last_trade.exit_reason != _ARTIFICIAL_EXIT_REASON:
            event = "exit"
            exit_reason = last_trade.exit_reason

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
