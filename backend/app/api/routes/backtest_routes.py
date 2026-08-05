"""Backtest routes — thin wrapper around app.services.strategy_runner."""

import asyncio
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import pandas as pd
from fastapi import APIRouter

from app.api.schemas.backtest_schemas import (
    HistoricalPerformanceRequest,
    HistoricalPerformanceResponse,
    RunBacktestRequest,
    RunBacktestResponse,
    StrategyResultResponse,
    TickerBacktestResult,
    TradeResponse,
)
from app.config.settings import settings
from app.ranking.models import RankingConfig
from app.services.backtest_data import fetch_backtest_bars, historical_outputsize
from app.services.strategy_runner import RunRequest, run_strategies
from app.strategies.execution import ExecutionConfig

_logger = logging.getLogger("quant_platform")

router = APIRouter(prefix="/api/backtests", tags=["backtests"])

# Strategy execution is CPU-bound pandas/numpy work, not I/O wait --
# threads don't give real parallelism for that (Python's GIL means
# only one thread runs Python bytecode at a time). Confirmed by
# measurement: letting every ticker's 35-strategy computation run
# unbounded (even capped) in THREADS ballooned each one from ~15s in
# isolation to 90-125s+ under load, and one run even 502'd outright --
# capping the thread count only stopped the crash, it never made the
# CPU-bound work itself faster, because threads fundamentally can't
# use more than one core for pure-Python/pandas work at a time.
#
# A process pool actually does: each worker is a separate OS process
# with its own GIL, so run_strategies calls genuinely run in parallel
# across cores. The cost is real memory per worker -- each one is a
# full fresh Python interpreter that has to import pandas/numpy/the
# whole strategy registry again. Sized conservatively via settings
# .strategy_worker_processes (default 2) rather than os.cpu_count():
# a container's reported core count often doesn't reflect its actual
# allocation (e.g. Render's free tier is ~0.1 vCPU on 512MB total), and
# spawning too many full-interpreter workers there risks an out-of-
# memory kill -- worse than running fewer workers slower. Bump the env
# var on a host that actually has the cores/RAM to spare.
#
# Created once at app startup (see main.py's lifespan calling
# start_strategy_pool/stop_strategy_pool) and reused across requests --
# spawning a fresh process pool per request would be far too slow,
# since process startup itself is the dominant cost for a short-lived
# pool.
_strategy_pool: ProcessPoolExecutor | None = None


def start_strategy_pool() -> None:
    global _strategy_pool
    _strategy_pool = ProcessPoolExecutor(max_workers=settings.strategy_worker_processes)


def stop_strategy_pool() -> None:
    global _strategy_pool
    if _strategy_pool is not None:
        _strategy_pool.shutdown(wait=False, cancel_futures=True)
        _strategy_pool = None

# "Historical performance" uses a fixed trailing three-month window,
# rather than the data source's drifting default lookback. This keeps
# the comparison consistent, and short enough that even the lazy
# single-strategy fetch below (see get_historical_performance) stays
# quick.
HISTORICAL_LOOKBACK_DAYS = 90

# fetch_backtest_bars' plain-backtest default (5000) is tuned for a
# short, explicit date range -- at a larger historical window it would
# silently truncate an intraday interval's historical fetch down to
# whatever tiny recent slice fits in 5000 bars (e.g. ~13 trading days
# for 1min), defeating the entire point of "historical." Request
# roughly enough bars to cover the full window instead, capped so a
# single request still completes in fetch_historical_bars' ~20s
# collection window -- dxfeed's own retention limits (or the cap
# below) may still return less than the full three months for the
# finest intervals, but historical_period_start/end on the response
# always report the ACTUAL span it covers, so that's honest either
# way, never silently misleading.
HISTORICAL_MAX_OUTPUTSIZE = 100_000

# Each ticker's bar fetch opens its own short-lived DXLink connection.
# The real bottleneck there is Tastytrade's own per-connection backfill
# pacing, not this app's CPU or network bandwidth -- an I/O wait, which
# concurrency genuinely helps with. This caps how many fetches run at
# once instead of unboundedly blasting every symbol at once (which
# risks tripping a per-account connection limit on Tastytrade's side --
# unconfirmed exact number, so this stays conservative).
_MAX_CONCURRENT_TICKER_FETCHES = 8

# Concurrent fetches mean more simultaneous DXLink connections than the
# old one-at-a-time code ever had -- confirmed in practice: symbols
# that fetch fine in isolation can intermittently come back with zero
# candles under concurrent load (a dropped/rate-limited connection, not
# a real "no data for this symbol"). One retry after a short pause
# recovers most of these; it does NOT change how a genuinely bad ticker
# behaves (still fails after the retry, same as before).
_FETCH_RETRY_ATTEMPTS = 2
_FETCH_RETRY_DELAY_SECONDS = 2.0


async def _fetch_bars_with_retry(symbol: str, payload: RunBacktestRequest) -> pd.DataFrame:
    last_error: Exception | None = None
    for attempt in range(1, _FETCH_RETRY_ATTEMPTS + 1):
        try:
            return await asyncio.to_thread(
                fetch_backtest_bars,
                symbol,
                payload.interval,
                payload.start_date,
                payload.end_date,
                include_extended_hours=payload.execution.include_extended_hours,
                include_overnight=payload.execution.include_overnight,
            )
        except Exception as exc:
            last_error = exc
            if attempt < _FETCH_RETRY_ATTEMPTS:
                _logger.warning("backtest %s: fetch attempt %d failed (%s), retrying", symbol, attempt, exc)
                await asyncio.sleep(_FETCH_RETRY_DELAY_SECONDS)
    raise last_error


async def _run_backtest_for_symbol(
    symbol: str,
    payload: RunBacktestRequest,
    request: RunRequest,
    fetch_semaphore: asyncio.Semaphore,
) -> TickerBacktestResult | None:
    """None means this ticker's BARS couldn't be fetched (bad symbol,
    fetch error surviving a retry, etc.) -- the caller reports it in
    failed_symbols rather than letting one bad ticker take down the
    whole batch response. Deliberately narrow: only the fetch is
    guarded here, NOT strategy execution -- an unknown strategy name is
    a request-validation problem uniform across every ticker (still
    NotFoundError -> 404 for the whole request, same as before), not a
    per-ticker data issue to silently swallow."""
    t_queued = time.monotonic()
    try:
        async with fetch_semaphore:
            t_fetch_start = time.monotonic()
            df = await _fetch_bars_with_retry(symbol, payload)
            t_fetch_done = time.monotonic()
    except Exception:
        _logger.exception("backtest %s: fetch failed, excluding from results", symbol)
        return None

    t_strategies_start = time.monotonic()
    loop = asyncio.get_running_loop()
    # Runs in _strategy_pool (a real process pool, see its own comment
    # above) -- genuine parallel CPU execution across workers, not just
    # concurrent scheduling. Falls back to the current thread if the
    # pool hasn't been started (e.g. a test that builds the app without
    # running its lifespan) so this never silently no-ops.
    if _strategy_pool is not None:
        results = await loop.run_in_executor(_strategy_pool, run_strategies, df, request)
    else:
        results = await asyncio.to_thread(run_strategies, df, request)
    t_strategies_done = time.monotonic()
    _logger.info(
        "backtest %s: fetch=%.1fs strategy_wait=%.1fs strategies=%.1fs total=%.1fs (%d bars)",
        symbol,
        t_fetch_done - t_fetch_start,
        t_strategies_start - t_fetch_done,
        t_strategies_done - t_strategies_start,
        t_strategies_done - t_queued,
        len(df),
    )

    return TickerBacktestResult(
        symbol=symbol.upper(),
        results=[
            StrategyResultResponse(
                strategy_name=r.strategy_name,
                strategy_display_name=r.strategy_display_name,
                metrics=r.metrics,
                trade_count=r.trade_count,
                overall_score=r.overall_score,
                trades=[
                    TradeResponse(
                        entry_time=t.entry_time,
                        exit_time=t.exit_time,
                        direction=t.direction.value,
                        entry_price=t.entry_price,
                        exit_price=t.exit_price,
                        quantity=t.quantity,
                        pnl=t.pnl,
                        exit_reason=t.exit_reason,
                    )
                    for t in r.trades
                ],
                rank=r.rank,
                monthly_metrics=r.monthly_metrics,
            )
            for r in results
        ],
    )


@router.post("/run", response_model=RunBacktestResponse)
async def run_backtest(payload: RunBacktestRequest):
    # ExecutionSettings' fields are named identically to ExecutionConfig's --
    # a plain spread is exact, no field-by-field mapping needed.
    execution_config = ExecutionConfig(**payload.execution.model_dump())
    ranking_config = (
        RankingConfig(weights=payload.ranking_weights) if payload.ranking_weights else RankingConfig()
    )

    request = RunRequest(
        strategy_names=payload.strategy_names,
        strategy_params=payload.strategy_params,
        execution_config=execution_config,
        ranking_config=ranking_config,
        breakdown_by_month=payload.breakdown_by_month,
        report_start_date=payload.start_date,
    )

    # Each ticker is scored/ranked independently -- "rank 1" means best
    # strategy for THAT ticker, not across the whole batch. Fetching is
    # concurrency-capped here (I/O wait, see _MAX_CONCURRENT_TICKER_FETCHES);
    # strategy computation is capped by _strategy_pool's own worker
    # count instead (CPU-bound, a different resource entirely -- see
    # its comment above). gather preserves payload.symbols' order
    # regardless of completion order.
    fetch_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_TICKER_FETCHES)
    raw_results = await asyncio.gather(
        *(
            _run_backtest_for_symbol(symbol, payload, request, fetch_semaphore)
            for symbol in payload.symbols
        )
    )

    # A None means that symbol failed (see _run_backtest_for_symbol) --
    # reported separately rather than failing the whole batch over one
    # bad/unlucky ticker.
    ticker_results = [r for r in raw_results if r is not None]
    failed_symbols = [symbol.upper() for symbol, r in zip(payload.symbols, raw_results) if r is None]

    return RunBacktestResponse(ticker_results=ticker_results, failed_symbols=failed_symbols)


@router.post("/historical-performance", response_model=HistoricalPerformanceResponse)
def get_historical_performance(payload: HistoricalPerformanceRequest):
    """
    How has this ONE symbol+strategy performed over the trailing
    HISTORICAL_LOOKBACK_DAYS -- fetched on demand (see Results.jsx's
    Historical Performance popup), not eagerly for every strategy on
    every /run call. Only ever costs one extra network fetch, for the
    one strategy actually being inspected.
    """
    execution_config = ExecutionConfig(**payload.execution.model_dump())
    historical_end = payload.end_date or date.today().isoformat()
    historical_start = (
        pd.Timestamp(historical_end) - pd.Timedelta(days=HISTORICAL_LOOKBACK_DAYS)
    ).date().isoformat()

    historical_df = fetch_backtest_bars(
        payload.symbol,
        payload.interval,
        historical_start,
        historical_end,
        include_extended_hours=payload.execution.include_extended_hours,
        include_overnight=payload.execution.include_overnight,
        outputsize=historical_outputsize(payload.interval, HISTORICAL_LOOKBACK_DAYS, HISTORICAL_MAX_OUTPUTSIZE),
    )

    request = RunRequest(
        strategy_names=[payload.strategy_name],
        strategy_params={payload.strategy_name: payload.strategy_params} if payload.strategy_params else None,
        execution_config=execution_config,
        breakdown_by_month=True,
        report_start_date=historical_start,
    )
    results = run_strategies(historical_df, request)
    result = results[0] if results else None

    return HistoricalPerformanceResponse(
        historical_metrics=result.metrics if result else None,
        historical_trade_count=result.trade_count if result else None,
        historical_period_start=historical_df.index.min() if not historical_df.empty else None,
        historical_period_end=historical_df.index.max() if not historical_df.empty else None,
        historical_monthly_metrics=result.monthly_metrics if result else None,
    )
