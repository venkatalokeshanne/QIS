"""
Dataset service.

Orchestrates the upload pipeline. Each step (load, detect, normalize,
validate, persist) lives in its own module; this is just the glue —
no business logic of its own, per the "never put business logic
inside routes" / thin-orchestration principle applied one layer down.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.loader import load_csv
from app.data.normalizer import normalize_ohlcv
from app.data.validator import ValidationReport, validate_ohlcv
from app.integrations import twelvedata_client
from app.repositories.dataset_repository import DatasetRecord, DatasetRepository

# Approximate day-widths for user-facing duration presets ("1M" = "about a
# month back") -- Twelve Data's API only understands actual calendar dates,
# not relative durations, so this is the one place that translates between
# the two. Precision to the day doesn't matter for a "how far back" picker.
_DURATION_UNIT_DAYS = {"D": 1, "M": 30, "Y": 365}


def _start_date_for_duration(duration: str) -> str:
    amount = int(duration[:-1])
    unit = duration[-1].upper()
    days = amount * _DURATION_UNIT_DAYS[unit]
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")


@dataclass(frozen=True)
class UploadResult:
    record: DatasetRecord
    validation: ValidationReport


class DatasetService:
    def __init__(self, repository: DatasetRepository | None = None):
        self._repository = repository or DatasetRepository()

    def upload_dataset(self, file_bytes: bytes, name: str, original_filename: str) -> UploadResult:
        raw = load_csv(file_bytes)
        detection = detect_columns(raw)
        normalized = normalize_ohlcv(raw, detection)
        report = validate_ohlcv(normalized)

        if not report.is_valid:
            raise DataValidationError("Dataset failed validation.", issues=report.errors)

        record = self._repository.save(normalized, name=name, original_filename=original_filename)
        return UploadResult(record=record, validation=report)

    def import_from_twelvedata(
        self,
        symbol: str,
        name: str | None = None,
        interval: str = "1min",
        duration: str | None = "1M",
        outputsize: int = 5000,
        start_date: str | None = None,
        end_date: str | None = None,
        fetch_bars=twelvedata_client.fetch_historical_bars,
    ) -> UploadResult:
        """
        Pull historical bars from Twelve Data and run them through the
        SAME detect -> normalize -> validate -> persist pipeline as an
        uploaded CSV, so a Twelve-Data-fetched dataset is indistinguishable
        from one uploaded by hand everywhere else in the app.

        `duration` is a user-facing "how far back" preset (e.g. "1D",
        "5D", "1M", "3M", "6M", "1Y") translated to a start_date here --
        pass an explicit `start_date` to bypass it entirely.
        `outputsize` stays a safety cap (Twelve Data's per-call max),
        not something the UI exposes directly.

        `fetch_bars` is injectable purely for testing (avoids a real
        network call in unit tests).
        """
        if duration and not start_date:
            start_date = _start_date_for_duration(duration)

        raw = fetch_bars(
            symbol,
            interval=interval,
            outputsize=outputsize,
            start_date=start_date,
            end_date=end_date,
        )
        detection = detect_columns(raw)
        normalized = normalize_ohlcv(raw, detection)
        report = validate_ohlcv(normalized)

        if not report.is_valid:
            raise DataValidationError("Dataset failed validation.", issues=report.errors)

        record = self._repository.save(normalized, name=name or symbol, original_filename=f"TwelveData:{symbol}")
        return UploadResult(record=record, validation=report)

    def get_dataframe(self, dataset_id: str) -> pd.DataFrame:
        return self._repository.get_dataframe(dataset_id)

    def get_metadata(self, dataset_id: str) -> DatasetRecord:
        return self._repository.get_metadata(dataset_id)

    def list_datasets(self) -> list[DatasetRecord]:
        return self._repository.list_all()

    def delete_dataset(self, dataset_id: str) -> None:
        self._repository.delete(dataset_id)

    def preview(self, dataset_id: str, rows: int = 20) -> list[dict]:
        df = self.get_dataframe(dataset_id)
        preview_df = df.head(rows).reset_index()
        preview_df["timestamp"] = preview_df["timestamp"].astype(str)
        return preview_df.to_dict(orient="records")
