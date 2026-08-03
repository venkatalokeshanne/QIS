"""Signal-alert Watches routes — thin wrapper around WatchRepository."""

from fastapi import APIRouter

from app.api.schemas.watch_schemas import WatchCreateRequest, WatchResponse
from app.core.exceptions import DataValidationError
from app.repositories.watch_repository import WatchRecord, WatchRepository
from app.services.live_signal_engine import engine as live_signal_engine

router = APIRouter(prefix="/api/watches", tags=["watches"])

_VALID_INTERVALS = {"1min", "5min", "15min", "1h", "1day"}


def _to_response(record: WatchRecord) -> WatchResponse:
    return WatchResponse(
        id=record.id,
        symbol=record.symbol,
        strategy_name=record.strategy_name,
        strategy_params=record.strategy_params,
        interval=record.interval,
        execution_settings=record.execution_settings,
        last_notified_bar_time=record.last_notified_bar_time,
        last_checked_at=record.last_checked_at,
        created_at=record.created_at,
    )


@router.post("", response_model=WatchResponse)
def create_watch(payload: WatchCreateRequest):
    if payload.interval not in _VALID_INTERVALS:
        raise DataValidationError(f"interval must be one of {sorted(_VALID_INTERVALS)} (got {payload.interval!r}).")
    repository = WatchRepository()
    record = repository.create(
        symbol=payload.symbol,
        strategy_name=payload.strategy_name,
        strategy_params=payload.strategy_params,
        interval=payload.interval,
        execution_settings=payload.execution.model_dump(),
    )
    # Subscribes the live signal engine to this symbol+interval's live
    # Candle feed (or, no-ops if already subscribed for another watch
    # on the same pair) -- fire-and-forget, doesn't block the response
    # on the historical warm-up fetch.
    live_signal_engine.on_watch_created(record)
    return _to_response(record)


@router.get("", response_model=list[WatchResponse])
def list_watches():
    repository = WatchRepository()
    return [_to_response(r) for r in repository.list_all()]


@router.delete("/{watch_id}", status_code=204)
def delete_watch(watch_id: str):
    repository = WatchRepository()
    record = repository.get(watch_id)
    repository.delete(watch_id)
    live_signal_engine.on_watch_deleted(record)
