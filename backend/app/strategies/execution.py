"""
Trade simulation engine.

Takes a strategy's entry/exit signals and turns them into a sequence
of Trades, applying execution realism (commission, slippage, forced
intraday close, and optional risk management). This is intentionally
the ONLY place that understands "what does it mean to hold a
position" — strategies just emit signals.

Kept here (not inside Strategy subclasses) so every strategy gets
identical execution behavior, and improvements to fill/commission/risk
modeling benefit every strategy at once.
"""

from dataclasses import dataclass

import pandas as pd

from app.domain.interfaces.strategy import Trade, TradeDirection
from app.indicators.atr import ATR
from app.utils.sessions import is_last_bar_of_session


@dataclass(frozen=True)
class ExecutionConfig:
    """Runner-level execution settings (NOT strategy parameters)."""

    capital: float = 10_000.0
    quantity: float = 1.0
    commission_per_trade: float = 0.0  # flat, applied once per round-trip
    slippage_pct: float = 0.0  # fraction of price, applied unfavorably on fills
    force_close_at_session_end: bool = True

    # Global trade-direction filter, applied uniformly on top of whatever
    # a strategy's own params allow (e.g. ORB's "direction" param). Lives
    # here rather than per-strategy so "only take longs" works the same
    # way for every strategy without each one reimplementing it.
    direction_filter: str = "both"  # "long_only" | "short_only" | "both"

    # Risk management — all disabled by default (None) so existing
    # behavior is unchanged unless a caller opts in.
    atr_period: int = 14  # inert unless a *_atr_multiple field below is set
    stop_loss_atr_multiple: float | None = None
    stop_loss_pct: float | None = None  # flat % of entry price; e.g. 0.01 = 1%
    take_profit_atr_multiple: float | None = None
    trailing_stop_atr_multiple: float | None = None  # if set, takes precedence over stop_loss_atr_multiple/stop_loss_pct
    risk_per_trade_pct: float | None = None  # requires a stop (atr_multiple, pct, or trailing) to be set
    # Cap quantity so entry position value never exceeds capital * this
    # (1.0 = full capital, i.e. no leverage). Applied to BOTH fixed and
    # risk-based sizing — risk sizing on a tight stop can otherwise
    # imply a position worth many times the account.
    max_position_value_pct: float | None = None

    # Priority when multiple stop mechanisms are configured at once:
    # trailing_stop_atr_multiple > stop_loss_pct > stop_loss_atr_multiple.
    # stop_loss_pct is intentionally independent of ATR — it never needs
    # a valid ATR reading, unlike the two ATR-based mechanisms above.


def _risk_management_enabled(config: ExecutionConfig) -> bool:
    return (
        config.stop_loss_atr_multiple is not None
        or config.stop_loss_pct is not None
        or config.take_profit_atr_multiple is not None
        or config.trailing_stop_atr_multiple is not None
    )


def _validate_config(config: ExecutionConfig) -> None:
    if (
        config.risk_per_trade_pct is not None
        and config.stop_loss_atr_multiple is None
        and config.stop_loss_pct is None
        and config.trailing_stop_atr_multiple is None
    ):
        raise ValueError(
            "risk_per_trade_pct requires stop_loss_atr_multiple, stop_loss_pct, or trailing_stop_atr_multiple to be set."
        )
    if config.stop_loss_pct is not None and config.stop_loss_pct <= 0:
        raise ValueError(f"stop_loss_pct must be > 0 (got {config.stop_loss_pct!r}).")
    if config.max_position_value_pct is not None and config.max_position_value_pct <= 0:
        raise ValueError(f"max_position_value_pct must be > 0 (got {config.max_position_value_pct!r}).")
    if config.direction_filter not in ("long_only", "short_only", "both"):
        raise ValueError(
            f"direction_filter must be 'long_only', 'short_only', or 'both' (got {config.direction_filter!r})."
        )


def _apply_direction_filter(entries: pd.Series, direction_filter: str) -> pd.Series:
    """Drop entry signals that don't match the allowed direction, leaving
    everything else (including exits) untouched.

    Uses element-wise .map (not a vectorized comparison) because
    TradeDirection is a str Enum: pandas can infer a specialized string
    dtype for an entries Series built without an explicit dtype=object,
    under which a vectorized `series != TradeDirection.X` silently
    compares wrong and matches everything.
    """
    if direction_filter == "both":
        return entries
    disallowed = TradeDirection.SHORT if direction_filter == "long_only" else TradeDirection.LONG
    return entries.map(lambda v: None if v == disallowed else v).astype(object)


def _fill_price(price: float, direction: TradeDirection, *, entering: bool, slippage_pct: float) -> float:
    """
    Apply slippage unfavorably: buys fill higher, sells fill lower.

    entering=True + LONG  -> buy  -> price up
    entering=True + SHORT -> sell -> price down
    entering=False (exit) + LONG  -> sell -> price down
    entering=False (exit) + SHORT -> buy  -> price up
    """
    is_buy = (direction == TradeDirection.LONG) == entering
    factor = 1 + slippage_pct if is_buy else 1 - slippage_pct
    return price * factor


def _pnl(direction: TradeDirection, entry_price: float, exit_price: float, quantity: float) -> float:
    if direction == TradeDirection.LONG:
        return (exit_price - entry_price) * quantity
    return (entry_price - exit_price) * quantity


def simulate_trades(
    df: pd.DataFrame,
    entries: pd.Series,
    exits: pd.Series,
    config: ExecutionConfig = ExecutionConfig(),
) -> list[Trade]:
    """
    Sequentially walk the bars, maintaining at most one open position
    at a time (no pyramiding/averaging in v1 — keeps results easy to
    reason about and compare across strategies).

    Args:
        df: indicator-enriched OHLCV dataframe (DatetimeIndex). Only
            needs a "close" column unless risk management (stop-loss /
            take-profit / trailing-stop) is enabled via config, in
            which case "high" and "low" are also required.
        entries: object Series of TradeDirection | None, from generate_entries.
        exits: boolean Series, from generate_exits.
        config: execution realism + risk-management settings.

    Returns:
        List of completed Trade objects (any position still open at
        the end of the data is force-closed at the last price).
    """
    if len(df) != len(entries) or len(df) != len(exits):
        raise ValueError("df, entries, and exits must be the same length.")

    _validate_config(config)
    entries = _apply_direction_filter(entries, config.direction_filter)

    forced_close = (
        is_last_bar_of_session(df.index)
        if config.force_close_at_session_end and isinstance(df.index, pd.DatetimeIndex)
        else pd.Series(False, index=df.index)
    )

    risk_enabled = _risk_management_enabled(config)
    atr_series = None
    if risk_enabled:
        atr_col = f"atr_{config.atr_period}"
        atr_series = ATR().calculate(df, {"period": config.atr_period})[atr_col]

    trades: list[Trade] = []
    open_direction: TradeDirection | None = None
    open_entry_time = None
    open_entry_price = None
    open_entry_index: int | None = None
    open_quantity = config.quantity
    open_stop_price: float | None = None
    open_trailing_price: float | None = None
    open_trailing_distance: float | None = None
    open_target_price: float | None = None

    def _reset_open_state() -> None:
        nonlocal open_direction, open_entry_time, open_entry_price, open_entry_index
        nonlocal open_quantity, open_stop_price, open_trailing_price, open_trailing_distance, open_target_price
        open_direction = None
        open_entry_time = None
        open_entry_price = None
        open_entry_index = None
        open_quantity = config.quantity
        open_stop_price = None
        open_trailing_price = None
        open_trailing_distance = None
        open_target_price = None

    for i, ts in enumerate(df.index):
        close_price = df["close"].iloc[i]

        if open_direction is not None:
            # 1. Intrabar stop-loss / take-profit / trailing-stop check (never on the entry bar itself).
            stop_hit = False
            target_hit = False
            risk_exit_price = None
            risk_exit_reason = None

            if risk_enabled and i > open_entry_index:
                bar_high = df["high"].iloc[i]
                bar_low = df["low"].iloc[i]

                if open_trailing_price is not None:
                    if open_direction == TradeDirection.LONG:
                        open_trailing_price = max(open_trailing_price, bar_high - open_trailing_distance)
                    else:
                        open_trailing_price = min(open_trailing_price, bar_low + open_trailing_distance)

                # A fixed stop and a trailing stop are mutually exclusive per trade
                # (trailing subsumes the fixed stop at entry) -- exactly one of
                # these two is ever set for a given open position.
                active_stop_price = open_trailing_price if open_trailing_price is not None else open_stop_price
                if active_stop_price is not None:
                    if open_direction == TradeDirection.LONG and bar_low <= active_stop_price:
                        stop_hit = True
                    elif open_direction == TradeDirection.SHORT and bar_high >= active_stop_price:
                        stop_hit = True
                    if stop_hit:
                        risk_exit_price = active_stop_price
                        risk_exit_reason = "trailing_stop" if open_trailing_price is not None else "stop_loss"

                # Take-profit only checked if the stop didn't already fire this bar --
                # conservative assumption when a single bar's range could plausibly
                # have hit both (OHLC data can't tell us which came first intrabar).
                if not stop_hit and open_target_price is not None:
                    if open_direction == TradeDirection.LONG and bar_high >= open_target_price:
                        target_hit = True
                    elif open_direction == TradeDirection.SHORT and bar_low <= open_target_price:
                        target_hit = True
                    if target_hit:
                        risk_exit_price = open_target_price
                        risk_exit_reason = "take_profit"

            if stop_hit or target_hit:
                fill = _fill_price(risk_exit_price, open_direction, entering=False, slippage_pct=config.slippage_pct)
                pnl = _pnl(open_direction, open_entry_price, fill, open_quantity) - config.commission_per_trade
                trades.append(
                    Trade(
                        entry_time=open_entry_time,
                        exit_time=ts,
                        direction=open_direction,
                        entry_price=open_entry_price,
                        exit_price=fill,
                        quantity=open_quantity,
                        pnl=pnl,
                        exit_reason=risk_exit_reason,
                    )
                )
                _reset_open_state()
                continue  # don't re-enter on the same bar we just exited

            # 2. Signal exit / forced session close (intrabar risk exits above take priority).
            exit_now = bool(exits.iloc[i]) or bool(forced_close.iloc[i])
            if exit_now:
                reason = "forced_session_close" if forced_close.iloc[i] and not exits.iloc[i] else "signal_exit"
                fill = _fill_price(close_price, open_direction, entering=False, slippage_pct=config.slippage_pct)
                pnl = _pnl(open_direction, open_entry_price, fill, open_quantity) - config.commission_per_trade
                trades.append(
                    Trade(
                        entry_time=open_entry_time,
                        exit_time=ts,
                        direction=open_direction,
                        entry_price=open_entry_price,
                        exit_price=fill,
                        quantity=open_quantity,
                        pnl=pnl,
                        exit_reason=reason,
                    )
                )
                _reset_open_state()
                continue  # don't re-enter on the same bar we just exited

        if open_direction is None:
            signal = entries.iloc[i]
            if signal in (TradeDirection.LONG, TradeDirection.SHORT):
                open_direction = signal
                open_entry_time = ts
                open_entry_index = i
                open_entry_price = _fill_price(
                    close_price, signal, entering=True, slippage_pct=config.slippage_pct
                )

                stop_distance_for_sizing = None
                if risk_enabled:
                    # ATR is NaN during the indicator's warm-up window; treat
                    # ATR-based stop/target/trailing as disabled for THIS
                    # trade only rather than crashing or sizing against a
                    # NaN distance. stop_loss_pct never depends on ATR, so
                    # it's handled outside this validity check.
                    entry_atr = atr_series.iloc[i]
                    atr_valid = pd.notna(entry_atr) and entry_atr > 0

                    if config.trailing_stop_atr_multiple is not None and atr_valid:
                        open_trailing_distance = entry_atr * config.trailing_stop_atr_multiple
                        open_trailing_price = (
                            open_entry_price - open_trailing_distance
                            if signal == TradeDirection.LONG
                            else open_entry_price + open_trailing_distance
                        )
                        stop_distance_for_sizing = open_trailing_distance
                    elif config.stop_loss_pct is not None:
                        stop_distance = open_entry_price * config.stop_loss_pct
                        open_stop_price = (
                            open_entry_price - stop_distance
                            if signal == TradeDirection.LONG
                            else open_entry_price + stop_distance
                        )
                        stop_distance_for_sizing = stop_distance
                    elif config.stop_loss_atr_multiple is not None and atr_valid:
                        stop_distance = entry_atr * config.stop_loss_atr_multiple
                        open_stop_price = (
                            open_entry_price - stop_distance
                            if signal == TradeDirection.LONG
                            else open_entry_price + stop_distance
                        )
                        stop_distance_for_sizing = stop_distance

                    if config.take_profit_atr_multiple is not None and atr_valid:
                        target_distance = entry_atr * config.take_profit_atr_multiple
                        open_target_price = (
                            open_entry_price + target_distance
                            if signal == TradeDirection.LONG
                            else open_entry_price - target_distance
                        )

                if config.risk_per_trade_pct is not None and stop_distance_for_sizing:
                    open_quantity = (config.capital * config.risk_per_trade_pct) / stop_distance_for_sizing
                else:
                    open_quantity = config.quantity

                if config.max_position_value_pct is not None and open_entry_price > 0:
                    max_quantity = (config.capital * config.max_position_value_pct) / open_entry_price
                    open_quantity = min(open_quantity, max_quantity)

    # Any position still open at the end of the data: force-close at the last bar.
    if open_direction is not None:
        last_price = df["close"].iloc[-1]
        fill = _fill_price(last_price, open_direction, entering=False, slippage_pct=config.slippage_pct)
        pnl = _pnl(open_direction, open_entry_price, fill, open_quantity) - config.commission_per_trade
        trades.append(
            Trade(
                entry_time=open_entry_time,
                exit_time=df.index[-1],
                direction=open_direction,
                entry_price=open_entry_price,
                exit_price=fill,
                quantity=open_quantity,
                pnl=pnl,
                exit_reason="end_of_data",
            )
        )

    return trades
