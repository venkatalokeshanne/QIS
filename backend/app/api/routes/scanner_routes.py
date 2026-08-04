"""Scanner routes -- run every selected strategy against every selected
symbol and report back only the recent long/short signal matches."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.schemas.scanner_schemas import (
    DayPrepRequest,
    DayPrepResponse,
    ScannerRunRequest,
    ScannerRunResponse,
)
from app.services import day_prep_service
from app.services.live_signal_engine import engine as live_signal_engine
from app.services.scanner_service import scan_for_signals
from app.strategies.execution import ExecutionConfig

router = APIRouter(prefix="/api/scanner", tags=["scanner"])


@router.post("/run", response_model=ScannerRunResponse)
def run_scan(payload: ScannerRunRequest):
    execution_config = ExecutionConfig(**payload.execution.model_dump())
    results, failed_symbols = scan_for_signals(
        symbols=payload.symbols,
        interval=payload.interval,
        strategy_names=payload.strategy_names,
        strategy_params_by_name=payload.strategy_params,
        execution_config=execution_config,
        lookback_bars=payload.lookback_bars,
        get_cached_bars=live_signal_engine.get_cached_bars,
    )
    return ScannerRunResponse(signals=[asdict(r) for r in results], failed_symbols=failed_symbols)


@router.post("/day-prep", response_model=DayPrepResponse)
def run_day_prep(payload: DayPrepRequest):
    execution_config = ExecutionConfig(**payload.execution.model_dump())
    results, failed_symbols = day_prep_service.prepare_day(
        symbols=payload.symbols,
        interval=payload.interval,
        strategy_names=payload.strategy_names,
        strategy_params_by_name=payload.strategy_params,
        execution_config=execution_config,
    )
    return DayPrepResponse(tickers=[asdict(r) for r in results], failed_symbols=failed_symbols)
