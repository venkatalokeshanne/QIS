"""Pydantic schemas for the Datasets API."""

from pydantic import BaseModel


class DatasetSummary(BaseModel):
    id: str
    name: str
    original_filename: str
    row_count: int
    start_date: str | None
    end_date: str | None
    created_at: str


class UploadResponse(BaseModel):
    dataset: DatasetSummary
    warnings: list[str]


class TwelveDataFetchRequest(BaseModel):
    symbol: str
    name: str | None = None
    interval: str = "1min"  # Twelve Data interval, e.g. "1min", "5min", "1h", "1day"
    duration: str | None = "1M"  # "how far back", e.g. "1D", "5D", "1M", "3M", "6M", "1Y"
    outputsize: int = 5000  # per-call safety cap, max 5000
    start_date: str | None = None  # overrides `duration` when given
    end_date: str | None = None


class PreviewRow(BaseModel):
    model_config = {"extra": "allow"}


class PreviewResponse(BaseModel):
    dataset_id: str
    rows: list[dict]
