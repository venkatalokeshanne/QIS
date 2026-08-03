"""Live Signal Check routes — thin wrapper around app.services.signal_service."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.schemas.signal_schemas import SignalCheckRequest, SignalCheckResponse
from app.services.signal_service import check_signal
from app.strategies.execution import ExecutionConfig

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.post("/check", response_model=SignalCheckResponse)
def check(payload: SignalCheckRequest):
    execution_config = ExecutionConfig(**payload.execution.model_dump())
    result = check_signal(
        payload.symbol,
        payload.interval,
        payload.strategy_name,
        payload.strategy_params,
        execution_config=execution_config,
    )
    return SignalCheckResponse(**asdict(result))
