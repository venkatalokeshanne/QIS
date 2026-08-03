"""Level Watches routes — thin wrapper around LevelWatchRepository."""

from fastapi import APIRouter

from app.api.schemas.level_watch_schemas import LevelWatchCreateRequest, LevelWatchResponse
from app.repositories.level_watch_repository import LevelWatchRecord, LevelWatchRepository

router = APIRouter(prefix="/api/level-watches", tags=["level-watches"])


def _to_response(record: LevelWatchRecord) -> LevelWatchResponse:
    return LevelWatchResponse(
        id=record.id,
        symbol=record.symbol,
        last_levels=record.last_levels,
        last_checked_at=record.last_checked_at,
        created_at=record.created_at,
    )


@router.post("", response_model=LevelWatchResponse)
def create_level_watch(payload: LevelWatchCreateRequest):
    repository = LevelWatchRepository()
    record = repository.create(symbol=payload.symbol)
    return _to_response(record)


@router.get("", response_model=list[LevelWatchResponse])
def list_level_watches():
    repository = LevelWatchRepository()
    return [_to_response(r) for r in repository.list_all()]


@router.delete("/{watch_id}", status_code=204)
def delete_level_watch(watch_id: str):
    repository = LevelWatchRepository()
    repository.delete(watch_id)
