"""
Raw CSV loading.

Deliberately does nothing except turn bytes/a file path into a
DataFrame. Column detection, normalization, and validation are each
separate modules so this one can be swapped for a Parquet/DB/broker
loader later without touching them.
"""

from io import BytesIO
from pathlib import Path

import pandas as pd

from app.core.exceptions import DataValidationError


def load_csv(source: bytes | str | Path) -> pd.DataFrame:
    """
    Load a CSV from raw bytes (an upload) or a file path into a
    DataFrame with no assumptions about column names yet.
    """
    try:
        if isinstance(source, (bytes, bytearray)):
            return pd.read_csv(BytesIO(source))
        return pd.read_csv(source)
    except pd.errors.EmptyDataError as exc:
        raise DataValidationError("The uploaded file is empty.") from exc
    except pd.errors.ParserError as exc:
        raise DataValidationError(f"Could not parse file as CSV: {exc}") from exc
