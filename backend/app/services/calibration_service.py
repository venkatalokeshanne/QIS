"""
Calibration Service.

Builds a TickerProfile: for a given ticker, which strategy has
historically performed best under each market regime, and what static
risk/timing parameters (stop loss, take profit, entry time window)
work best for this specific ticker. This is the "playbook" the Daily
Strategy Selector (app.services.daily_selector_service) reads from --
built once (or periodically) offline, not recomputed on every request.

See app.services.regime_classifier for how a day's regime is
determined, and app.services.calibration_store for how the resulting
profile gets persisted.
"""

import itertools
from dataclasses import dataclass

import pandas as pd

from app.integrations import twelvedata_client
from app.metrics.calculator import calculate_all_metrics
from app.ranking.models import RankingConfig
from app.ranking.scorer import score_results
from app.services.backtest_data import fetch_backtest_bars, historical_outputsize
from app.services.regime_classifier import classify_regime_series, combine_market_regime, regime_bucket_key
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import discover_strategies, get_strategy, strategy_registry

# Below this many trades IN A SINGLE REGIME BUCKET, that bucket's "best
# strategy" pick isn't trusted -- the bucket falls back to the ticker's
# unconditional best strategy instead. Same spirit as
# day_prep_service.MIN_EDGE_TRADES / the old LOW_SAMPLE_THRESHOLD,
# scoped locally to this feature (not reviving either). Raised from an
# original 8 after live testing showed 8-trade picks were close to a
# coin flip and didn't generalize to new data.
MIN_REGIME_TRADES = 15

# Grid swept once per ticker (against its unconditional-best strategy)
# to pick static stop-loss/take-profit/entry-time-window parameters.
# Deliberately small -- every extra grid point is another way to
# accidentally curve-fit a "few tickers" calibration to its own history.
_SL_ATR_GRID = (1.0, 1.5, 2.0, 2.5)
_TP_ATR_GRID = (2.0, 3.0, 4.0)
_TIME_WINDOW_GRID: tuple[tuple[str | None, str | None], ...] = (
    (None, None),  # full session
    ("09:30", "11:30"),
    ("09:30", "12:00"),
    ("13:00", "16:00"),
)

# Historical lookback for the DAILY-bar regime read -- generous since
# ADX/ATR need real warm-up (default vol_lookback=100 bars) before a
# day is even classifiable; short of this and the earliest part of the
# calibration window would have no usable regime label at all.
_DAILY_LOOKBACK_PAD_DAYS = 200


@dataclass(frozen=True)
class TickerProfile:
    symbol: str
    interval: str
    calibrated_through: str  # the cutoff date used, "YYYY-MM-DD"
    market_proxies: list[str]
    # The ticker's single best-performing strategy, unconditioned on
    # regime -- the fallback for any regime bucket without enough
    # trades to trust its own pick, and the strategy the parameter
    # sweep (step 6) is calibrated against.
    default_strategy: str
    # regime_classifier.regime_bucket_key(...) -> strategy_name. Only
    # contains buckets that cleared MIN_REGIME_TRADES on their own;
    # buckets without an entry here fall back to default_strategy.
    strategy_by_regime: dict[str, str]
    # regime_bucket_key(...) -> how many trades backed that bucket's
    # pick -- transparency, same spirit as the old market-regime
    # analysis reporting a trade count next to every bucket's metrics.
    regime_trade_counts: dict[str, int]
    # Ticker-wide fallback params -- used for default_strategy, and for
    # any regime_by_strategy pick that doesn't have its own entry below.
    stop_loss_atr_multiple: float
    take_profit_atr_multiple: float
    entry_time_start: str | None
    entry_time_end: str | None
    # regime_bucket_key(...) -> {stop_loss_atr_multiple, take_profit_atr_multiple,
    # entry_time_start, entry_time_end}. A bucket only gets an entry here
    # if that bucket's OWN winning strategy has params swept specifically
    # for IT that (a) still clear MIN_REGIME_TRADES and (b) score better
    # than just reusing the ticker-wide params above -- the ticker-wide
    # params were only ever tuned against ONE strategy (default_strategy's
    # sweep candidate), so forcing them onto every OTHER regime's pick was
    # confirmed in practice to mismatch strategies whose real edge falls
    # outside that window or needs a different stop distance. Buckets
    # without an entry here still get a strategy pick, just via the
    # ticker-wide params (same as before this field existed).
    regime_params: dict[str, dict]


def daily_regime_by_date(symbol: str, start_date: str, end_date: str, fetch_bars) -> dict:
    """date -> RegimeLabel | None, from `symbol`'s daily bars over a
    padded range so early dates in [start_date, end_date] still have
    enough trailing history to be classifiable (see _DAILY_LOOKBACK_PAD_DAYS).
    Public -- shared with app.services.daily_selector_service, which
    needs the identical lookup for both "today's regime" and the
    backtest replay's day-by-day walk, not a case where the two
    callers' semantics should ever diverge."""
    padded_start = (pd.Timestamp(start_date) - pd.Timedelta(days=_DAILY_LOOKBACK_PAD_DAYS)).date().isoformat()
    lookback_days = max((pd.Timestamp(end_date) - pd.Timestamp(padded_start)).days, 1)
    outputsize = historical_outputsize("1day", lookback_days, twelvedata_client.MAX_OUTPUTSIZE)
    # include_extended_hours/include_overnight=True is what makes
    # filter_by_session a no-op (see twelvedata_client) -- daily bars
    # come back with a midnight timestamp, which the session-window
    # filter would otherwise treat as "overnight" and strip entirely.
    # The regular/extended/overnight distinction only means anything
    # for intraday bars.
    daily_df = fetch_backtest_bars(
        symbol,
        "1day",
        padded_start,
        end_date,
        include_extended_hours=True,
        include_overnight=True,
        outputsize=outputsize,
        fetch_bars=fetch_bars,
    )
    series = classify_regime_series(daily_df)
    return {ts.date(): label for ts, label in series.items()}


def market_regime_by_date(market_proxies: list[str], start_date: str, end_date: str, fetch_bars) -> dict:
    """date -> combined RegimeLabel | None across every market proxy
    (see combine_market_regime). Public for the same reason as
    daily_regime_by_date above."""
    per_proxy = {p: daily_regime_by_date(p, start_date, end_date, fetch_bars) for p in market_proxies}
    all_dates: set = set()
    for lookup in per_proxy.values():
        all_dates.update(lookup.keys())
    return {d: combine_market_regime([per_proxy[p].get(d) for p in market_proxies]) for d in all_dates}


def _pick_best_strategy(trades_by_strategy: dict[str, list], capital: float) -> str | None:
    """Rank candidates by calculate_all_metrics + score_results (the
    same scoring machinery /run uses) and return the winner's name, or
    None if nothing scored (e.g. every candidate had zero trades)."""
    raw_results = [
        (name, name, calculate_all_metrics(trades, capital), len(trades), trades, None)
        for name, trades in trades_by_strategy.items()
    ]
    if not raw_results:
        return None
    ranked = score_results(raw_results, RankingConfig())
    if not ranked or ranked[0].overall_score is None:
        return None
    return ranked[0].strategy_name


def _sweep_parameters(
    df: pd.DataFrame, strategy_name: str, report_start
) -> tuple[float, float, tuple[str | None, str | None]]:
    """Sweep _SL_ATR_GRID x _TP_ATR_GRID x _TIME_WINDOW_GRID against
    `strategy_name` over the whole calibration window and return the
    best-scoring (stop_loss_atr_multiple, take_profit_atr_multiple,
    (entry_time_start, entry_time_end)) combo."""
    strategy = get_strategy(strategy_name)
    params = strategy.validate_params({})

    combos = list(itertools.product(_SL_ATR_GRID, _TP_ATR_GRID, _TIME_WINDOW_GRID))
    raw_results = []
    for sl, tp, (t_start, t_end) in combos:
        config = ExecutionConfig(
            stop_loss_atr_multiple=sl, take_profit_atr_multiple=tp, entry_time_start=t_start, entry_time_end=t_end
        )
        try:
            trades = strategy.run(df, params, config)
        except Exception:
            trades = []
        trades = [t for t in trades if t.entry_time.date() >= report_start]
        label = f"sl={sl}|tp={tp}|window={t_start}-{t_end}"
        raw_results.append((label, label, calculate_all_metrics(trades, config.capital), len(trades), trades, None))

    ranked = score_results(raw_results, RankingConfig())
    scored = [r for r in ranked if r.overall_score is not None]
    if not scored:
        # No combo produced enough trades to score -- fall back to the
        # grid's own middle values rather than an arbitrary point.
        return _SL_ATR_GRID[1], _TP_ATR_GRID[1], (None, None)

    winner_label = scored[0].strategy_name
    for (sl, tp, window), (label, *_rest) in zip(combos, raw_results):
        if label == winner_label:
            return sl, tp, window
    return _SL_ATR_GRID[1], _TP_ATR_GRID[1], (None, None)  # unreachable, defensive


def calibrate_ticker(
    symbol: str,
    interval: str,
    market_proxies: list[str],
    start_date: str,
    cutoff_date: str,
    strategy_names: list[str] | None = None,
    fetch_bars=twelvedata_client.fetch_historical_bars,
) -> TickerProfile:
    """
    Build `symbol`'s TickerProfile using ONLY historical data in
    [start_date, cutoff_date] -- see the module docstring for the full
    pipeline. Raises ValueError if no candidate strategy produced
    enough trades in the window to calibrate anything.
    """
    symbol = symbol.upper()
    discover_strategies()
    names = strategy_names or strategy_registry.names()
    report_start = pd.Timestamp(start_date).date()

    ticker_regime_lookup = daily_regime_by_date(symbol, start_date, cutoff_date, fetch_bars)
    market_regime_lookup = market_regime_by_date(market_proxies, start_date, cutoff_date, fetch_bars)

    lookback_days = max((pd.Timestamp(cutoff_date) - pd.Timestamp(start_date)).days, 1)
    outputsize = historical_outputsize(interval, lookback_days, twelvedata_client.MAX_OUTPUTSIZE)
    df = fetch_backtest_bars(
        symbol, interval, start_date, cutoff_date, outputsize=outputsize, fetch_bars=fetch_bars
    )

    def run_all(config: ExecutionConfig) -> dict[str, list]:
        trades_by_strategy: dict[str, list] = {}
        for name in names:
            strategy = get_strategy(name)
            params = strategy.validate_params({})
            try:
                trades = strategy.run(df, params, config)
            except Exception:
                trades = []
            trades_by_strategy[name] = [t for t in trades if t.entry_time.date() >= report_start]
        return trades_by_strategy

    # Pass 1: raw signal only (no risk management, full session) --
    # used ONLY to seed a reasonable candidate for the parameter sweep
    # below. Deliberately NOT used for the regime-bucket picks or the
    # final default_strategy: a strategy's raw signal can look great
    # unconstrained and then produce far fewer (or worse) trades once
    # the ticker's actual stop-loss/take-profit/entry-window apply to
    # it -- confirmed in practice, some candidates lose enough trades
    # under the real params to drop below MIN_REGIME_TRADES entirely,
    # which base_config's looser count would never have revealed.
    raw_trades_by_strategy = run_all(ExecutionConfig())
    sweep_candidate = _pick_best_strategy(raw_trades_by_strategy, ExecutionConfig().capital)
    if sweep_candidate is None:
        raise ValueError(
            f"No strategy produced enough trades to calibrate {symbol} over [{start_date}, {cutoff_date}]."
        )

    stop_loss_atr_multiple, take_profit_atr_multiple, (entry_time_start, entry_time_end) = _sweep_parameters(
        df, sweep_candidate, report_start
    )
    final_config = ExecutionConfig(
        stop_loss_atr_multiple=stop_loss_atr_multiple,
        take_profit_atr_multiple=take_profit_atr_multiple,
        entry_time_start=entry_time_start,
        entry_time_end=entry_time_end,
    )

    # Pass 2: re-run every candidate under the SAME static params the
    # ticker will actually trade with -- this is the trade set BOTH the
    # unconditional default pick AND every regime bucket's pick get
    # ranked from, so "best strategy" always means "best under the
    # conditions this ticker actually runs under," not under a
    # hypothetical unconstrained backtest nobody will ever trade.
    trades_by_strategy = run_all(final_config)
    default_strategy = _pick_best_strategy(trades_by_strategy, final_config.capital)
    if default_strategy is None:
        # sweep_candidate had enough raw-signal trades, but nothing
        # survives once the real params are applied -- fall back to it
        # rather than leaving the ticker uncalibratable over a
        # parameter choice, not a genuine lack of data.
        default_strategy = sweep_candidate

    # Bucket every strategy's own trades by the regime active on their
    # entry day, then rank within each bucket independently.
    bucket_trades: dict[str, dict[str, list]] = {}
    for name, trades in trades_by_strategy.items():
        for trade in trades:
            entry_date = trade.entry_time.date()
            ticker_regime = ticker_regime_lookup.get(entry_date)
            market_regime = market_regime_lookup.get(entry_date)
            if ticker_regime is None or market_regime is None:
                continue  # unclassifiable day -- doesn't count toward any bucket
            key = regime_bucket_key(ticker_regime, market_regime)
            bucket_trades.setdefault(key, {}).setdefault(name, []).append(trade)

    strategy_by_regime: dict[str, str] = {}
    regime_trade_counts: dict[str, int] = {}
    for bucket_key, by_strategy in bucket_trades.items():
        qualifying = {name: t for name, t in by_strategy.items() if len(t) >= MIN_REGIME_TRADES}
        if not qualifying:
            continue  # falls back to default_strategy at lookup time
        best_name = _pick_best_strategy(qualifying, final_config.capital)
        if best_name is None:
            continue
        strategy_by_regime[bucket_key] = best_name
        regime_trade_counts[bucket_key] = len(qualifying[best_name])

    # For each bucket's winning strategy, try sweeping params tuned to
    # THAT strategy specifically, instead of forcing on it the params
    # that were only ever tuned for sweep_candidate. Only keep the
    # override if it (a) still clears MIN_REGIME_TRADES for this bucket
    # and (b) scores better than the ticker-wide params already do --
    # otherwise the ticker-wide params (known to qualify, since that's
    # how this strategy became the bucket's winner) are kept as-is.
    # Sweeps are cached per strategy name since the same strategy often
    # wins more than one bucket.
    swept_params_cache: dict[str, tuple[float, float, tuple[str | None, str | None]]] = {}
    regime_params: dict[str, dict] = {}
    for bucket_key, winner_name in strategy_by_regime.items():
        if winner_name not in swept_params_cache:
            swept_params_cache[winner_name] = _sweep_parameters(df, winner_name, report_start)
        own_sl, own_tp, (own_start, own_end) = swept_params_cache[winner_name]

        own_config = ExecutionConfig(
            stop_loss_atr_multiple=own_sl, take_profit_atr_multiple=own_tp, entry_time_start=own_start, entry_time_end=own_end
        )
        strategy = get_strategy(winner_name)
        params = strategy.validate_params({})
        try:
            own_trades = strategy.run(df, params, own_config)
        except Exception:
            own_trades = []
        own_trades = [t for t in own_trades if t.entry_time.date() >= report_start]
        own_bucket_trades = [
            t
            for t in own_trades
            if (tr := ticker_regime_lookup.get(t.entry_time.date())) is not None
            and (mr := market_regime_lookup.get(t.entry_time.date())) is not None
            and regime_bucket_key(tr, mr) == bucket_key
        ]

        if len(own_bucket_trades) < MIN_REGIME_TRADES:
            continue  # own-tuned params don't hold up for this bucket -- keep the ticker-wide params

        ticker_wide_bucket_trades = bucket_trades[bucket_key][winner_name]
        ranked = score_results(
            [
                ("ticker_wide", "ticker_wide", calculate_all_metrics(ticker_wide_bucket_trades, final_config.capital), len(ticker_wide_bucket_trades), ticker_wide_bucket_trades, None),
                ("own_tuned", "own_tuned", calculate_all_metrics(own_bucket_trades, own_config.capital), len(own_bucket_trades), own_bucket_trades, None),
            ],
            RankingConfig(),
        )
        if ranked and ranked[0].strategy_name == "own_tuned":
            regime_params[bucket_key] = {
                "stop_loss_atr_multiple": own_sl,
                "take_profit_atr_multiple": own_tp,
                "entry_time_start": own_start,
                "entry_time_end": own_end,
            }
            regime_trade_counts[bucket_key] = len(own_bucket_trades)

    return TickerProfile(
        symbol=symbol,
        interval=interval,
        calibrated_through=cutoff_date,
        market_proxies=list(market_proxies),
        default_strategy=default_strategy,
        strategy_by_regime=strategy_by_regime,
        regime_trade_counts=regime_trade_counts,
        stop_loss_atr_multiple=stop_loss_atr_multiple,
        take_profit_atr_multiple=take_profit_atr_multiple,
        entry_time_start=entry_time_start,
        entry_time_end=entry_time_end,
        regime_params=regime_params,
    )
