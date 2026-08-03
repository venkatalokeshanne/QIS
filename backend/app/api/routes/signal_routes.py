"""Live Signal Check routes — thin wrapper around app.services.signal_service."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.schemas.signal_schemas import SignalCheckRequest, SignalCheckResponse
from app.services.signal_service import check_signal

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.post("/check", response_model=SignalCheckResponse)
def check(payload: SignalCheckRequest):
    result = check_signal(payload.symbol, payload.interval, payload.strategy_name, payload.strategy_params)
    return SignalCheckResponse(**asdict(result))
