"""Live Signal Check routes — thin wrapper around app.services.signal_service."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.schemas.signal_schemas import SignalCheckRequest, SignalCheckResponse
from app.services.live_signal_engine import engine as live_signal_engine
from app.services.signal_service import check_signal
from app.strategies.execution import ExecutionConfig

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.post("/check", response_model=SignalCheckResponse)
def check(payload: SignalCheckRequest):
    execution_config = ExecutionConfig(**payload.execution.model_dump())
    # Reuse the live engine's already-subscribed, continuously-updated
    # bars when this symbol+interval is being tracked live (e.g. an
    # active watch) instead of opening a brand-new DXLink connection
    # for every single poll -- see check_signal's cached_df docstring.
    cached_df = live_signal_engine.get_cached_bars(payload.symbol, payload.interval)
    result = check_signal(
        payload.symbol,
        payload.interval,
        payload.strategy_name,
        payload.strategy_params,
        execution_config=execution_config,
        cached_df=cached_df,
    )
    return SignalCheckResponse(**asdict(result))
