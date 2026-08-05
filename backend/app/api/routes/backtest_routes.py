"""Backtest routes — thin wrapper around app.services.strategy_runner."""

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
from app.ranking.models import RankingConfig
from app.services.backtest_data import fetch_backtest_bars, historical_outputsize
from app.services.strategy_runner import RunRequest, run_strategies
from app.strategies.execution import ExecutionConfig

router = APIRouter(prefix="/api/backtests", tags=["backtests"])

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


@router.post("/run", response_model=RunBacktestResponse)
def run_backtest(payload: RunBacktestRequest):
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

    ticker_results = []
    for symbol in payload.symbols:
        # Each ticker is scored/ranked independently -- "rank 1" means
        # best strategy for THAT ticker, not across the whole batch.
        df = fetch_backtest_bars(
            symbol,
            payload.interval,
            payload.start_date,
            payload.end_date,
            include_extended_hours=payload.execution.include_extended_hours,
            include_overnight=payload.execution.include_overnight,
        )
        results = run_strategies(df, request)

        ticker_results.append(
            TickerBacktestResult(
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
        )

    return RunBacktestResponse(ticker_results=ticker_results)


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
