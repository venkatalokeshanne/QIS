"""
Price Volume Rank (Anthony Trongone).

Classifies each bar into one of four regimes based on whether price
AND volume each rose or fell versus the prior bar, giving a simple 1-4
rank used by scanners to flag "price up on rising volume" (strongest,
rank 1) down through "price down on falling volume" (weakest, rank 4).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("price_volume_rank")
class PriceVolumeRank(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="price_volume_rank",
            display_name="Price Volume Rank",
            description="1-4 rank of price-vs-volume agreement: price up/volume up (1) through price down/volume down (4).",
            category="volume",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()

        price_up = out["close"] > out["close"].shift(1)
        volume_up = out["volume"] > out["volume"].shift(1)

        rank = pd.Series(np.nan, index=out.index)
        rank[price_up & volume_up] = 1
        rank[price_up & ~volume_up] = 2
        rank[~price_up & volume_up] = 3
        rank[~price_up & ~volume_up] = 4

        out["price_volume_rank"] = rank
        return out
