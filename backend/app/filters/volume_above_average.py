"""Volume > Average Volume."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("volume_above_average")
class VolumeAboveAverage(Filter):
    """Requires a volume_avg_{period} column already computed (app.indicators.volume_average)."""

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="volume_above_average",
            display_name="Volume > Average Volume",
            description="True where current volume exceeds its rolling average.",
            category="volume",
            default_params={"period": 20},
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        p = self.validate_params(params)
        col = f"volume_avg_{p['period']}"
        if col not in df.columns:
            raise KeyError(f"volume_above_average filter requires a '{col}' column.")
        return df["volume"] > df[col]
