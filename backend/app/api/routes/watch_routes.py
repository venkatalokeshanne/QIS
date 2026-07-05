"""Signal-alert Watches routes — thin wrapper around WatchRepository."""

from fastapi import APIRouter

from app.api.schemas.watch_schemas import TestNotificationRequest, WatchCreateRequest, WatchResponse
from app.core.exceptions import DataValidationError
from app.repositories.watch_repository import WatchRecord, WatchRepository
from app.services import notification_service

router = APIRouter(prefix="/api/watches", tags=["watches"])

_VALID_INTERVALS = {"1min", "5min", "15min"}


def _to_response(record: WatchRecord) -> WatchResponse:
    return WatchResponse(
        id=record.id,
        symbol=record.symbol,
        strategy_name=record.strategy_name,
        strategy_params=record.strategy_params,
        interval=record.interval,
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
        expo_push_token=payload.expo_push_token,
        symbol=payload.symbol,
        strategy_name=payload.strategy_name,
        strategy_params=payload.strategy_params,
        interval=payload.interval,
    )
    return _to_response(record)


@router.post("/test-notification", status_code=204)
def send_test_notification(payload: TestNotificationRequest):
    """
    Sends a push immediately, bypassing the poller/strategy-signal logic
    entirely -- lets someone confirm the delivery pipeline itself
    (backend -> Expo -> APNs -> device) works without waiting on market
    hours or a real entry/exit signal to happen to fire.
    """
    notification_service.send_push_notification(
        payload.expo_push_token,
        "Test Notification",
        "If you can see this, push notifications are working.",
        data={"test": True},
    )


@router.get("", response_model=list[WatchResponse])
def list_watches(expo_push_token: str):
    repository = WatchRepository()
    return [_to_response(r) for r in repository.list_for_token(expo_push_token)]


@router.delete("/{watch_id}", status_code=204)
def delete_watch(watch_id: str):
    repository = WatchRepository()
    repository.delete(watch_id)
