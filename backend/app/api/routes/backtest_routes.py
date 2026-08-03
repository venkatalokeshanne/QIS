"""Backtest routes — thin wrapper around app.services.strategy_runner."""

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
        df = fetch_backtest_bars(symbol, payload.interval, payload.start_date, payload.end_date)
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
