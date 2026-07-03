"""Dataset routes — thin wrappers around DatasetService. No business logic here."""

from fastapi import APIRouter, File, Form, UploadFile

from app.api.schemas.dataset_schemas import DatasetSummary, PreviewResponse, TwelveDataFetchRequest, UploadResponse
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


def _to_summary(record) -> DatasetSummary:
    return DatasetSummary(
        id=record.id,
        name=record.name,
        original_filename=record.original_filename,
        row_count=record.row_count,
        start_date=record.start_date,
        end_date=record.end_date,
        created_at=record.created_at,
    )


@router.post("", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...), name: str | None = Form(None)):
    service = DatasetService()
    content = await file.read()
    result = service.upload_dataset(
        content, name=name or file.filename, original_filename=file.filename
    )
    return UploadResponse(dataset=_to_summary(result.record), warnings=result.validation.warnings)


@router.post("/twelvedata", response_model=UploadResponse)
def fetch_from_twelvedata(payload: TwelveDataFetchRequest):
    service = DatasetService()
    result = service.import_from_twelvedata(
        symbol=payload.symbol,
        name=payload.name,
        interval=payload.interval,
        duration=payload.duration,
        outputsize=payload.outputsize,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    return UploadResponse(dataset=_to_summary(result.record), warnings=result.validation.warnings)


@router.get("", response_model=list[DatasetSummary])
def list_datasets():
    service = DatasetService()
    return [_to_summary(r) for r in service.list_datasets()]


@router.get("/{dataset_id}", response_model=DatasetSummary)
def get_dataset(dataset_id: str):
    service = DatasetService()
    return _to_summary(service.get_metadata(dataset_id))


@router.get("/{dataset_id}/preview", response_model=PreviewResponse)
def preview_dataset(dataset_id: str, rows: int = 20):
    service = DatasetService()
    return PreviewResponse(dataset_id=dataset_id, rows=service.preview(dataset_id, rows=rows))


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str):
    service = DatasetService()
    service.delete_dataset(dataset_id)
