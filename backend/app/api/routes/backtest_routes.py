"""Backtest routes — thin wrapper around app.services.strategy_runner."""

from fastapi import APIRouter

from app.api.schemas.backtest_schemas import (
    DatasetBacktestResult,
    RunBacktestRequest,
    RunBacktestResponse,
    StrategyResultResponse,
    TradeResponse,
)
from app.ranking.models import RankingConfig
from app.services.dataset_service import DatasetService
from app.services.strategy_runner import RunRequest, run_strategies
from app.strategies.execution import ExecutionConfig

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


@router.post("/run", response_model=RunBacktestResponse)
def run_backtest(payload: RunBacktestRequest):
    dataset_service = DatasetService()

    execution_config = ExecutionConfig(
        capital=payload.execution.capital,
        quantity=payload.execution.quantity,
        commission_per_trade=payload.execution.commission_per_trade,
        slippage_pct=payload.execution.slippage_pct,
        force_close_at_session_end=payload.execution.force_close_at_session_end,
        direction_filter=payload.execution.direction_filter,
        atr_period=payload.execution.atr_period,
        stop_loss_atr_multiple=payload.execution.stop_loss_atr_multiple,
        stop_loss_pct=payload.execution.stop_loss_pct,
        take_profit_atr_multiple=payload.execution.take_profit_atr_multiple,
        trailing_stop_atr_multiple=payload.execution.trailing_stop_atr_multiple,
        risk_per_trade_pct=payload.execution.risk_per_trade_pct,
    )
    ranking_config = (
        RankingConfig(weights=payload.ranking_weights) if payload.ranking_weights else RankingConfig()
    )

    request = RunRequest(
        strategy_names=payload.strategy_names,
        strategy_params=payload.strategy_params,
        execution_config=execution_config,
        ranking_config=ranking_config,
        breakdown_by_month=payload.breakdown_by_month,
    )

    dataset_results = []
    for dataset_id in payload.dataset_ids:
        # Each dataset is scored/ranked independently -- "rank 1" means
        # best strategy for THAT ticker, not across the whole batch.
        metadata = dataset_service.get_metadata(dataset_id)
        df = dataset_service.get_dataframe(dataset_id)
        results = run_strategies(df, request)

        dataset_results.append(
            DatasetBacktestResult(
                dataset_id=dataset_id,
                dataset_name=metadata.name,
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

    return RunBacktestResponse(dataset_results=dataset_results)
