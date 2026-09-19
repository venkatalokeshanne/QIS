"""
Daily Selector Service.

The "live" and "backtest" halves of the Daily Strategy Selector:
  - select_for_today: for one symbol, read today's regime (ticker +
    market), look up which strategy/parameters that regime calls for
    in the symbol's calibrated TickerProfile (see
    app.services.calibration_service), and run that strategy on recent
    bars to see today's signal.
  - backtest_selection: replay that same day-by-day selection process
    over a historical TEST window that starts strictly AFTER the
    profile's own calibration cutoff -- genuine out-of-sample, not
    graded on data the playbook was built from -- and compares it
    against a static single-strategy baseline over the identical
    window.

Both read the SAME TickerProfile via app.services.calibration_store --
calibration is centralized in one place (POST
/api/daily-selection/calibrate writes it, both of these read it), so
"today's pick" and "does switching actually help" are always evaluated
against the identical playbook, never a silently different one built
on the fly. A symbol that hasn't been calibrated yet raises
NotFoundError, same as an unknown strategy name elsewhere in this app.
"""

from dataclasses import dataclass, field

import pandas as pd

from app.core.exceptions import NotFoundError
from app.integrations import twelvedata_client
from app.metrics.calculator import calculate_all_metrics
from app.services import calibration_store
from app.services.backtest_data import fetch_backtest_bars, historical_outputsize
from app.services.calibration_service import daily_regime_by_date, market_regime_by_date
from app.services.regime_classifier import classify_regime, combine_market_regime, regime_bucket_key
from app.services.signal_service import _trade_direction, fetch_symbol_bars
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import get_strategy

# Same "once-a-day read" generosity as day_prep_service's own
# SIGNAL_LOOKBACK_BARS -- a bit more forgiving than scanner_service's
# tight polling-loop default, since this is checked once, not repeatedly.
SIGNAL_LOOKBACK_BARS = 5

# How far back "today's regime" looks for daily bars -- matches
# calibration_service's own _DAILY_LOOKBACK_PAD_DAYS so a live read and
# a calibration read are classifying off the same warm-up depth.
DAILY_REGIME_LOOKBACK_DAYS = 200


@dataclass(frozen=True)
class DailySelection:
    symbol: str
    interval: str
    as_of: pd.Timestamp
    price: float | None
    ticker_regime: str | None  # RegimeLabel.key, or None if unclassifiable
    market_regime: str | None
    regime_bucket: str | None  # None when either side is unclassifiable
    selected_strategy: str
    used_fallback: bool  # True if the regime bucket had no calibrated pick of its own
    stop_loss_atr_multiple: float
    take_profit_atr_multiple: float
    entry_time_start: str | None
    entry_time_end: str | None
    has_live_signal: bool
    signal_direction: str | None
    signal_time: pd.Timestamp | None
    bars_ago: int | None


@dataclass(frozen=True)
class RegimeSegment:
    regime_bucket: str  # "unclassified" when neither ticker nor market regime was classifiable
    strategy_used: str
    start_date: str
    end_date: str
    trade_count: int
    # The params this segment actually ran with -- the bucket's own
    # tuned override if calibration found one, else the ticker-wide
    # defaults. Surfaced so two adjacent segments that share a strategy
    # but were NOT merged (because their resolved params differ) are
    # visibly distinguishable rather than looking like an unexplained split.
    stop_loss_atr_multiple: float = 0.0
    take_profit_atr_multiple: float = 0.0
    entry_time_start: str | None = None
    entry_time_end: str | None = None
    metrics: dict[str, float | None] = field(default_factory=dict)


@dataclass(frozen=True)
class SwitchingTrade:
    """One trade from the switching backtest, same shape as the plain
    Trade domain object plus WHICH strategy generated it -- the segment
    summary alone can't answer "what actually happened on this specific
    trade," only the aggregate per period."""

    strategy_name: str
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp | None
    direction: str
    entry_price: float
    exit_price: float | None
    quantity: float
    pnl: float | None
    exit_reason: str | None


@dataclass(frozen=True)
class SelectionBacktestResult:
    symbol: str
    interval: str
    calibrated_through: str
    test_start: str
    test_end: str
    switching_metrics: dict[str, float | None]
    switching_trade_count: int
    switching_trades: list[SwitchingTrade]
    baseline_strategy: str
    baseline_metrics: dict[str, float | None]
    baseline_trade_count: int
    segments: list[RegimeSegment]


_DEFAULT_PARAM_KEYS = ("stop_loss_atr_multiple", "take_profit_atr_multiple", "entry_time_start", "entry_time_end")


def _ticker_wide_params(profile) -> dict:
    return {
        "stop_loss_atr_multiple": profile.stop_loss_atr_multiple,
        "take_profit_atr_multiple": profile.take_profit_atr_multiple,
        "entry_time_start": profile.entry_time_start,
        "entry_time_end": profile.entry_time_end,
    }


def _resolve_pick(profile, bucket_key: str | None) -> tuple[str, dict]:
    """(strategy_name, params dict) for a given regime bucket (or None
    for unclassified days) -- applies that bucket's own regime_params
    override if calibration found one, else the ticker-wide defaults.
    Unclassified days and buckets with no strategy_by_regime entry both
    fall back to profile.default_strategy with the ticker-wide params."""
    if bucket_key and bucket_key in profile.strategy_by_regime:
        strategy_name = profile.strategy_by_regime[bucket_key]
        params = profile.regime_params.get(bucket_key) or _ticker_wide_params(profile)
    else:
        strategy_name = profile.default_strategy
        params = _ticker_wide_params(profile)
    return strategy_name, params


def _params_key(params: dict) -> tuple:
    return tuple(params[k] for k in _DEFAULT_PARAM_KEYS)


def _most_recent_entry(trades: list, df: pd.DataFrame, lookback_bars: int) -> tuple | None:
    """The latest trade (if any) whose entry landed within the last
    `lookback_bars` bars of `df`. Same shape as scanner_service's own
    private helper -- kept as its own small copy here (matching
    day_prep_service's own precedent) since a cross-module private
    import isn't warranted for something this small."""
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
            break
    return None


def select_for_today(
    symbol: str,
    interval: str,
    as_of: pd.Timestamp | None = None,
    fetch_bars=twelvedata_client.fetch_historical_bars,
) -> DailySelection:
    symbol = symbol.upper()
    profile = calibration_store.load_profile(symbol)
    if profile is None:
        raise NotFoundError(f"'{symbol}' has not been calibrated yet -- POST /api/daily-selection/calibrate first.")

    as_of = as_of or pd.Timestamp.now(tz="America/New_York").tz_localize(None)
    today = as_of.date().isoformat()
    daily_start = (as_of - pd.Timedelta(days=DAILY_REGIME_LOOKBACK_DAYS)).date().isoformat()

    # include_extended_hours/include_overnight=True makes
    # filter_by_session a no-op -- daily bars carry a midnight
    # timestamp, which the session-window filter would otherwise treat
    # as "overnight" and strip entirely (see calibration_service's
    # daily_regime_by_date, which needs the identical fix).
    ticker_daily_df = fetch_backtest_bars(
        symbol, "1day", daily_start, today, include_extended_hours=True, include_overnight=True, fetch_bars=fetch_bars
    )
    ticker_regime = classify_regime(ticker_daily_df)

    proxy_labels = []
    for proxy in profile.market_proxies:
        proxy_daily_df = fetch_backtest_bars(
            proxy, "1day", daily_start, today, include_extended_hours=True, include_overnight=True, fetch_bars=fetch_bars
        )
        proxy_labels.append(classify_regime(proxy_daily_df))
    market_regime = combine_market_regime(proxy_labels)

    regime_bucket = regime_bucket_key(ticker_regime, market_regime) if ticker_regime and market_regime else None
    used_fallback = regime_bucket is None or regime_bucket not in profile.strategy_by_regime
    selected_strategy, params = _resolve_pick(profile, regime_bucket)

    execution_config = ExecutionConfig(
        stop_loss_atr_multiple=params["stop_loss_atr_multiple"],
        take_profit_atr_multiple=params["take_profit_atr_multiple"],
        entry_time_start=params["entry_time_start"],
        entry_time_end=params["entry_time_end"],
        force_close_at_session_end=False,
    )

    intraday_df = fetch_symbol_bars(symbol, interval, fetch_bars=fetch_bars)
    strategy = get_strategy(selected_strategy)
    strategy_params = strategy.validate_params({})
    trades = strategy.run(intraday_df, strategy_params, execution_config) if not intraday_df.empty else []
    match = _most_recent_entry(trades, intraday_df, SIGNAL_LOOKBACK_BARS)

    return DailySelection(
        symbol=symbol,
        interval=interval,
        as_of=intraday_df.index[-1] if not intraday_df.empty else as_of,
        price=float(intraday_df["close"].iloc[-1]) if not intraday_df.empty else None,
        ticker_regime=ticker_regime.key if ticker_regime else None,
        market_regime=market_regime.key if market_regime else None,
        regime_bucket=regime_bucket,
        selected_strategy=selected_strategy,
        used_fallback=used_fallback,
        stop_loss_atr_multiple=params["stop_loss_atr_multiple"],
        take_profit_atr_multiple=params["take_profit_atr_multiple"],
        entry_time_start=params["entry_time_start"],
        entry_time_end=params["entry_time_end"],
        has_live_signal=match is not None,
        signal_direction=_trade_direction(match[0]) if match else None,
        signal_time=match[0].entry_time if match else None,
        bars_ago=match[1] if match else None,
    )


def _test_window_days(
    ticker_regime_lookup: dict, market_regime_lookup: dict, profile, cutoff_date: str, test_end_date: str
) -> list[tuple]:
    """[(date, bucket_label, strategy_name, params), ...] in
    chronological order for every classifiable day in [cutoff_date,
    test_end_date]. bucket_label is "unclassified" (falling back to
    profile.default_strategy, same as select_for_today) when the ticker
    or market regime wasn't classifiable that day. `params` is whatever
    _resolve_pick resolves for that bucket -- a per-bucket override if
    calibration found one, else the ticker-wide defaults."""
    start = pd.Timestamp(cutoff_date).date()
    end = pd.Timestamp(test_end_date).date()
    dates = sorted(d for d in set(ticker_regime_lookup) | set(market_regime_lookup) if start <= d <= end)

    days = []
    for d in dates:
        ticker_regime = ticker_regime_lookup.get(d)
        market_regime = market_regime_lookup.get(d)
        bucket = regime_bucket_key(ticker_regime, market_regime) if ticker_regime and market_regime else None
        strategy_name, params = _resolve_pick(profile, bucket)
        days.append((d, bucket or "unclassified", strategy_name, params))
    return days


def _group_into_segments(days: list[tuple]) -> list[tuple]:
    """Group consecutive (date, bucket, strategy, params) entries that
    share the same (STRATEGY, PARAMS) pair into contiguous [(bucket,
    strategy, params, start_date, end_date), ...] segments -- what
    actually changes operationally is which strategy+params combo runs,
    so two adjacent days landing in different regime buckets but still
    resolving to the identical pick stay one segment. Two buckets that
    happen to share a strategy but resolve to DIFFERENT params (one has
    a per-bucket override, the other doesn't) are NOT merged -- they'd
    need different ExecutionConfigs and can't be one continuous run."""
    if not days:
        return []
    segments = []
    seg_bucket, seg_strategy, seg_params, seg_start = days[0][1], days[0][2], days[0][3], days[0][0]
    seg_end = days[0][0]
    for d, bucket, strategy_name, params in days[1:]:
        if strategy_name == seg_strategy and _params_key(params) == _params_key(seg_params):
            seg_end = d
        else:
            segments.append((seg_bucket, seg_strategy, seg_params, seg_start, seg_end))
            seg_bucket, seg_strategy, seg_params, seg_start, seg_end = bucket, strategy_name, params, d, d
    segments.append((seg_bucket, seg_strategy, seg_params, seg_start, seg_end))
    return segments


def backtest_selection(
    symbol: str,
    interval: str,
    start_date: str,
    test_end_date: str,
    fetch_bars=twelvedata_client.fetch_historical_bars,
) -> SelectionBacktestResult:
    """
    Loads `symbol`'s ALREADY-CALIBRATED TickerProfile (POST
    /api/daily-selection/calibrate must have been run for it first --
    raises NotFoundError otherwise, same as select_for_today) and
    replays that exact playbook day-by-day over the requested
    [start_date, test_end_date] window. Also runs the playbook's own
    unconditional-best strategy continuously across the identical
    window as a static baseline, so switching-vs-static is a direct,
    honest comparison.

    `start_date` is CLAMPED UP to profile.calibrated_through if it
    predates it -- the out-of-sample guarantee (never testing on data
    the playbook was calibrated on) always wins over honoring the
    caller's exact requested date. The response's `test_start` reports
    whichever date actually got used, so a clamp is visible, not silent.

    Deliberately does NOT recalibrate internally: calibration lives in
    exactly one place (the stored TickerProfile), so this backtest is
    always testing the SAME playbook Today's Picks is currently reading
    from, not a fresh one built from whatever dates happened to be
    passed to this call.
    """
    symbol = symbol.upper()
    profile = calibration_store.load_profile(symbol)
    if profile is None:
        raise NotFoundError(f"'{symbol}' has not been calibrated yet -- POST /api/daily-selection/calibrate first.")
    market_proxies = profile.market_proxies

    cutoff = pd.Timestamp(profile.calibrated_through).date()
    requested_start = pd.Timestamp(start_date).date()
    test_start_date = max(requested_start, cutoff).isoformat()

    # Regime lookups span [test_start_date, test_end_date] --
    # daily_regime_by_date pads its own warm-up history before
    # test_start_date internally, so the early TEST-window days are
    # still classifiable. _test_window_days below only ever turns days
    # >= test_start_date into segments, so no pre-cutoff day is ever
    # part of the backtested result (see the clamp above).
    ticker_regime_lookup = daily_regime_by_date(symbol, test_start_date, test_end_date, fetch_bars)
    proxy_regime_lookup = market_regime_by_date(market_proxies, test_start_date, test_end_date, fetch_bars)
    days = _test_window_days(ticker_regime_lookup, proxy_regime_lookup, profile, test_start_date, test_end_date)
    segments_raw = _group_into_segments(days)

    lookback_days = max((pd.Timestamp(test_end_date) - pd.Timestamp(test_start_date)).days, 1)
    outputsize = historical_outputsize(interval, lookback_days, twelvedata_client.MAX_OUTPUTSIZE)
    full_test_df = fetch_backtest_bars(
        symbol, interval, test_start_date, test_end_date, outputsize=outputsize, fetch_bars=fetch_bars
    )

    # Baseline always runs the ticker-wide default -- never a per-bucket
    # override -- since it's meant to be the single static comparison
    # point "would switching have even helped."
    baseline_params = _ticker_wide_params(profile)

    # Run each DISTINCT (strategy, params) PICK that shows up across the
    # segments (or as the baseline) ONCE, continuously, on the full
    # test-window fetch -- same "run once, bucket after" pattern
    # calibrate_ticker itself uses, so picks never re-fetch/re-run
    # redundantly and every strategy sees identical, properly warmed-up
    # indicator history. Keyed on (strategy_name, params_key) rather than
    # strategy_name alone because two segments can run the SAME strategy
    # under DIFFERENT resolved params (one bucket has a per-bucket
    # override, another doesn't, or two buckets have different overrides).
    distinct_picks: dict[tuple, dict] = {(strategy_name, _params_key(params)): params for _, strategy_name, params, _, _ in segments_raw}
    distinct_picks[(profile.default_strategy, _params_key(baseline_params))] = baseline_params

    default_capital = ExecutionConfig().capital
    trades_by_pick: dict[tuple, list] = {}
    for (name, params_key), params in distinct_picks.items():
        strategy = get_strategy(name)
        strategy_params = strategy.validate_params({})
        pick_config = ExecutionConfig(
            stop_loss_atr_multiple=params["stop_loss_atr_multiple"],
            take_profit_atr_multiple=params["take_profit_atr_multiple"],
            entry_time_start=params["entry_time_start"],
            entry_time_end=params["entry_time_end"],
        )
        try:
            trades = strategy.run(full_test_df, strategy_params, pick_config)
        except Exception:
            trades = []
        trades_by_pick[(name, params_key)] = trades

    segments: list[RegimeSegment] = []
    switching_trades: list = []
    switching_trade_records: list[SwitchingTrade] = []
    for bucket, strategy_name, params, seg_start, seg_end in segments_raw:
        pick_key = (strategy_name, _params_key(params))
        seg_trades = [t for t in trades_by_pick[pick_key] if seg_start <= t.entry_time.date() <= seg_end]
        switching_trades.extend(seg_trades)
        switching_trade_records.extend(
            SwitchingTrade(
                strategy_name=strategy_name,
                entry_time=t.entry_time,
                exit_time=t.exit_time,
                direction=_trade_direction(t),
                entry_price=t.entry_price,
                exit_price=t.exit_price,
                quantity=t.quantity,
                pnl=t.pnl,
                exit_reason=t.exit_reason,
            )
            for t in seg_trades
        )
        segments.append(
            RegimeSegment(
                regime_bucket=bucket,
                strategy_used=strategy_name,
                start_date=seg_start.isoformat(),
                end_date=seg_end.isoformat(),
                trade_count=len(seg_trades),
                stop_loss_atr_multiple=params["stop_loss_atr_multiple"],
                take_profit_atr_multiple=params["take_profit_atr_multiple"],
                entry_time_start=params["entry_time_start"],
                entry_time_end=params["entry_time_end"],
                metrics=calculate_all_metrics(seg_trades, default_capital),
            )
        )
    switching_trades.sort(key=lambda t: t.entry_time)
    switching_trade_records.sort(key=lambda t: t.entry_time)

    test_start_bound = pd.Timestamp(test_start_date).date()
    test_end_bound = pd.Timestamp(test_end_date).date()
    baseline_pick_key = (profile.default_strategy, _params_key(baseline_params))
    baseline_trades = [
        t for t in trades_by_pick[baseline_pick_key] if test_start_bound <= t.entry_time.date() <= test_end_bound
    ]

    return SelectionBacktestResult(
        symbol=symbol,
        interval=interval,
        calibrated_through=profile.calibrated_through,
        test_start=test_start_date,
        test_end=test_end_date,
        switching_metrics=calculate_all_metrics(switching_trades, default_capital),
        switching_trade_count=len(switching_trades),
        switching_trades=switching_trade_records,
        baseline_strategy=profile.default_strategy,
        baseline_metrics=calculate_all_metrics(baseline_trades, default_capital),
        baseline_trade_count=len(baseline_trades),
        segments=segments,
    )
