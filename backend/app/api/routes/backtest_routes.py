"""Backtest routes — thin wrapper around app.services.strategy_runner."""

from dataclasses import replace
from datetime import date

import pandas as pd
from fastapi import APIRouter

from app.api.schemas.backtest_schemas import (
    RunBacktestRequest,
    RunBacktestResponse,
    StrategyResultResponse,
    TickerBacktestResult,
    TradeResponse,
)
from app.ranking.models import RankingConfig
from app.services.backtest_data import fetch_backtest_bars
from app.services.strategy_runner import RunRequest, run_strategies
from app.strategies.execution import ExecutionConfig

router = APIRouter(prefix="/api/backtests", tags=["backtests"])

# "Historical performance" means a full trailing year, not whatever
# unbounded default fetch_backtest_bars happens to return -- fixing the
# window keeps the comparison meaningful (same ~year of data every
# time) instead of drifting with each data source's own default lookback.
HISTORICAL_LOOKBACK_DAYS = 365


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
    has_explicit_range = bool(payload.start_date or payload.end_date)

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

        # "How has this strategy actually done on this ticker
        # historically" -- the SAME run over a fixed trailing year
        # ending today (or the requested end_date, if given) rather
        # than just the requested date range. Skipped as a redundant
        # duplicate fetch/run when the request already had no date
        # bounds (that request already covers this full window).
        if has_explicit_range:
            historical_end = payload.end_date or date.today().isoformat()
            historical_start = (
                pd.Timestamp(historical_end) - pd.Timedelta(days=HISTORICAL_LOOKBACK_DAYS)
            ).date().isoformat()
            historical_df = fetch_backtest_bars(
                symbol,
                payload.interval,
                historical_start,
                historical_end,
                include_extended_hours=payload.execution.include_extended_hours,
                include_overnight=payload.execution.include_overnight,
            )
            historical_request = replace(request, report_start_date=historical_start)
            historical_results = run_strategies(historical_df, historical_request)
            historical_by_name = {r.strategy_name: r for r in historical_results}
            historical_period_start = historical_df.index.min()
            historical_period_end = historical_df.index.max()
        else:
            historical_by_name = {}
            historical_period_start = None
            historical_period_end = None

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
                        historical_metrics=historical_by_name[r.strategy_name].metrics
                        if r.strategy_name in historical_by_name
                        else None,
                        historical_trade_count=historical_by_name[r.strategy_name].trade_count
                        if r.strategy_name in historical_by_name
                        else None,
                        historical_period_start=historical_period_start,
                        historical_period_end=historical_period_end,
                    )
                    for r in results
                ],
            )
        )

    return RunBacktestResponse(ticker_results=ticker_results)
