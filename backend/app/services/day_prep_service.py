"""
Day Prep Service.

Answers "which of my tickers are worth concentrating on today," not
just "which ones happen to have an entry inside a tight recent-bars
window" (see scanner_service.scan_for_signals, the older/narrower
"what's flashing right now" view). A ticker can be worth watching all
day even with nothing signaling in the last few bars -- this looks at
the whole picture instead.

For every symbol, three transparent, independently-reported signals
are computed (no hidden black-box reasoning):
  - activity: how many times ANY of the requested strategies entered a
    trade on this ticker in the trailing ACTIVITY_LOOKBACK_DAYS -- a
    ticker my strategies trade often is worth more attention than one
    that hasn't set up in months.
  - edge: the best trailing EDGE_LOOKBACK_DAYS win_rate/profit_factor
    among the requested strategies on this ticker -- activity only
    matters if the strategies that fire on it have actually been
    profitable there.
  - movement: today's overnight/pre-market gap vs. the prior regular
    session's close -- a ticker already on the move is more likely to
    produce a real intraday setup than one sitting dead flat.

These three are min-max normalized across the batch and blended into
one concentration_score purely to provide a default sort order --
every input is still returned individually (per ticker AND per
strategy) so "why is this ticker ranked here" is always inspectable.
Tickers where none of the requested strategies have ever traded in the
lookback window are dropped entirely -- "worth watching" requires at
least some track record, not just a ticker existing.
"""

from dataclasses import dataclass, replace
from datetime import timedelta
from typing import Any

import pandas as pd

from app.integrations import tastytrade_client
from app.metrics.calculator import calculate_all_metrics
from app.services.backtest_data import fetch_backtest_bars, historical_outputsize
from app.services.signal_service import _trade_direction
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import get_strategy, list_strategies

# How far back "how often does this ticker actually set up" looks --
# about a trading month, recent enough to reflect current behavior.
ACTIVITY_LOOKBACK_DAYS = 20

# How far back the win-rate/profit-factor "is this strategy actually
# good here" check looks -- long enough for a handful of trades on
# most strategies, short enough to fetch quickly and stay relevant to
# current market behavior (the Results page's historical performance
# view is the place for deep multi-year validation, not this).
EDGE_LOOKBACK_DAYS = 180
EDGE_MAX_OUTPUTSIZE = 20_000

# Below this many trades, a win_rate/profit_factor is just noise --
# such a strategy can still show up (sorted behind trusted ones) but
# never becomes a ticker's headline "top strategy."
MIN_EDGE_TRADES = 3

# A strategy's most recent entry counts as "live right now" if it
# landed within this many of the freshest bars -- slightly more
# forgiving than scan_for_signals' own default since day prep is a
# once-in-the-morning read, not a tight polling loop.
SIGNAL_LOOKBACK_BARS = 5

# Small, fast snapshot fetch for today's gap -- only needs the single
# freshest price, not a real backtest window.
_SNAPSHOT_INTERVAL = "5min"
_SNAPSHOT_LOOKBACK_DAYS = 4
_SNAPSHOT_OUTPUTSIZE = 300

# Weighted blend for the default sort order -- edge and activity
# matter most (a strategy needs both a track record AND to actually
# be setting up), movement is a smaller tiebreaker (nice to have, not
# essential -- a ticker can be worth watching even sitting still if
# the setups have historically been reliable).
_WEIGHTS = {"activity": 0.35, "edge": 0.40, "movement": 0.25}


@dataclass(frozen=True)
class StrategyEdge:
    strategy_name: str
    strategy_display_name: str
    trade_count: int
    win_rate: float | None
    profit_factor: float | None
    net_profit: float | None
    recent_trade_count: int  # entries within ACTIVITY_LOOKBACK_DAYS
    has_live_signal: bool  # entered within SIGNAL_LOOKBACK_BARS of the freshest bar
    signal_direction: str | None
    signal_bars_ago: int | None


@dataclass(frozen=True)
class TickerConcentration:
    symbol: str
    price: float
    concentration_score: float
    activity_count: int  # total recent entries across every requested strategy
    gap_pct: float | None
    gap_as_of: pd.Timestamp | None
    top_strategies: list[StrategyEdge]  # sorted best-first (live signal, then profit factor), capped to a few


def _prior_regular_close(df: pd.DataFrame, as_of: pd.Timestamp) -> tuple[pd.Timestamp, float] | None:
    prior = df[df.index.normalize() < as_of.normalize()]
    if prior.empty:
        return None
    return prior.index[-1], float(prior["close"].iloc[-1])


def _current_gap_pct(
    symbol: str, regular_df: pd.DataFrame, now: pd.Timestamp, fetch_bars
) -> tuple[float, pd.Timestamp] | None:
    """Gap between the freshest known price (pre-market/overnight, or
    already-regular if queried after the open) and the prior completed
    regular session's close. None when there's no prior session to
    compare against, the snapshot fetch fails, or there's no print
    newer than that prior close yet."""
    prior = _prior_regular_close(regular_df, now)
    if prior is None:
        return None
    prior_time, prior_close = prior
    if prior_close <= 0:
        return None

    try:
        raw = fetch_bars(
            symbol,
            interval=_SNAPSHOT_INTERVAL,
            outputsize=_SNAPSHOT_OUTPUTSIZE,
            start_date=(now - pd.Timedelta(days=_SNAPSHOT_LOOKBACK_DAYS)).date().isoformat(),
            include_extended_hours=True,
            include_overnight=True,
        )
    except Exception:
        return None
    if raw is None or raw.empty:
        return None

    latest_time = raw["date"].iloc[-1]
    latest_price = float(raw["close"].iloc[-1])
    if latest_time <= prior_time:
        return None
    return (latest_price - prior_close) / prior_close, latest_time


def _most_recent_entry_bars_ago(trades: list, df: pd.DataFrame) -> tuple[Any, int] | None:
    """The latest trade (if any) whose entry lands within
    SIGNAL_LOOKBACK_BARS of the freshest bar in `df`. Mirrors
    scanner_service._most_recent_entry -- kept as its own small copy
    here rather than a cross-module private import, since day prep's
    lookback window is intentionally different."""
    if not trades:
        return None
    last_index = len(df.index) - 1
    for trade in reversed(trades):
        try:
            entry_loc = df.index.get_loc(trade.entry_time)
        except KeyError:
            continue
        bars_ago = last_index - entry_loc
        if 0 <= bars_ago < SIGNAL_LOOKBACK_BARS:
            return trade, bars_ago
        if bars_ago >= SIGNAL_LOOKBACK_BARS:
            break
    return None


def _normalize(values: list[float | None]) -> list[float]:
    """Min-max normalize to [0, 1] across the batch, treating missing
    values as the lowest possible (0) rather than excluding them --
    "no data" shouldn't accidentally score as "average.\""""
    present = [v for v in values if v is not None]
    if len(present) < 2 or max(present) == min(present):
        return [0.5 if v is not None else 0.0 for v in values]
    lo, hi = min(present), max(present)
    return [((v - lo) / (hi - lo)) if v is not None else 0.0 for v in values]


def prepare_day(
    symbols: list[str],
    interval: str,
    strategy_names: list[str] | None = None,
    strategy_params_by_name: dict[str, dict[str, Any]] | None = None,
    execution_config: ExecutionConfig | None = None,
    fetch_bars=tastytrade_client.fetch_historical_bars,
    now: pd.Timestamp | None = None,
) -> tuple[list[TickerConcentration], list[str]]:
    """
    Returns (results, failed_symbols). `results` is sorted best-
    concentration-score-first. Tickers with zero trades from every
    requested strategy over EDGE_LOOKBACK_DAYS are dropped -- no track
    record means nothing useful to say about that ticker today.
    """
    strategy_meta = list_strategies()
    names = strategy_names or [m["name"] for m in strategy_meta]
    display_names = {m["name"]: m["display_name"] for m in strategy_meta}
    strategy_params_by_name = strategy_params_by_name or {}
    config = execution_config or ExecutionConfig()
    now = now or pd.Timestamp.now(tz="America/New_York").tz_localize(None)
    today = now.date()

    outputsize = historical_outputsize(interval, EDGE_LOOKBACK_DAYS, EDGE_MAX_OUTPUTSIZE)
    start_date = (today - timedelta(days=EDGE_LOOKBACK_DAYS)).isoformat()
    end_date = today.isoformat()
    activity_cutoff = today - timedelta(days=ACTIVITY_LOOKBACK_DAYS)
    run_config = replace(config, force_close_at_session_end=False)

    raw: list[dict] = []
    failed: list[str] = []

    for raw_symbol in symbols:
        symbol = raw_symbol.upper()
        try:
            df = fetch_backtest_bars(
                symbol,
                interval,
                start_date=start_date,
                end_date=end_date,
                outputsize=outputsize,
                fetch_bars=fetch_bars,
            )
        except Exception:
            failed.append(symbol)
            continue
        if df.empty:
            failed.append(symbol)
            continue

        edges: list[StrategyEdge] = []
        total_activity = 0
        for name in names:
            try:
                strategy = get_strategy(name)
                params = strategy.validate_params(strategy_params_by_name.get(name, {}))
                trades = strategy.run(df, params, run_config)
            except Exception:
                continue
            if not trades:
                continue

            recent = [t for t in trades if t.entry_time.date() >= activity_cutoff]
            total_activity += len(recent)
            metrics = calculate_all_metrics(trades, config.capital)
            signal_match = _most_recent_entry_bars_ago(trades, df)

            edges.append(
                StrategyEdge(
                    strategy_name=name,
                    strategy_display_name=display_names.get(name, name),
                    trade_count=len(trades),
                    win_rate=metrics.get("win_rate"),
                    profit_factor=metrics.get("profit_factor"),
                    net_profit=metrics.get("net_profit"),
                    recent_trade_count=len(recent),
                    has_live_signal=signal_match is not None,
                    signal_direction=_trade_direction(signal_match[0]) if signal_match else None,
                    signal_bars_ago=signal_match[1] if signal_match else None,
                )
            )

        if not edges:
            # No requested strategy has ever traded this ticker in the
            # lookback window -- nothing useful to watch it for.
            continue

        trusted = [e for e in edges if e.trade_count >= MIN_EDGE_TRADES and e.profit_factor is not None]
        pool = trusted or edges
        top_strategies = sorted(pool, key=lambda e: (not e.has_live_signal, -(e.profit_factor or 0)))[:3]
        best_profit_factor = max((e.profit_factor for e in trusted), default=None)

        try:
            gap_result = _current_gap_pct(symbol, df, now, fetch_bars)
        except Exception:
            gap_result = None
        gap_pct, gap_as_of = gap_result if gap_result else (None, None)

        raw.append(
            {
                "symbol": symbol,
                "price": float(df["close"].iloc[-1]),
                "activity_count": total_activity,
                "gap_pct": gap_pct,
                "gap_as_of": gap_as_of,
                "top_strategies": top_strategies,
                "best_profit_factor": best_profit_factor,
            }
        )

    if not raw:
        return [], failed

    activity_norm = _normalize([r["activity_count"] for r in raw])
    edge_norm = _normalize([r["best_profit_factor"] for r in raw])
    movement_norm = _normalize([abs(r["gap_pct"]) if r["gap_pct"] is not None else None for r in raw])

    results: list[TickerConcentration] = []
    for i, r in enumerate(raw):
        score = (
            _WEIGHTS["activity"] * activity_norm[i]
            + _WEIGHTS["edge"] * edge_norm[i]
            + _WEIGHTS["movement"] * movement_norm[i]
        ) * 100
        results.append(
            TickerConcentration(
                symbol=r["symbol"],
                price=r["price"],
                concentration_score=round(score, 1),
                activity_count=r["activity_count"],
                gap_pct=r["gap_pct"],
                gap_as_of=r["gap_as_of"],
                top_strategies=r["top_strategies"],
            )
        )

    results.sort(key=lambda r: -r.concentration_score)
    return results, failed
