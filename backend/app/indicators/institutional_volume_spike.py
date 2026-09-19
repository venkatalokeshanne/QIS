"""
Institutional Volume Spike.

Flags bars where volume spikes well above its recent average AND the
bar closed decisively in one direction -- read as a proxy for large
("institutional") participation rather than routine retail noise.
Bullish: huge volume + close > open. Bearish: huge volume + close < open.

The source script paired this with its own 3-bar Fair Value Gap check,
but that's identical logic to the already-shipped
app.indicators.fair_value_gap -- not duplicated here.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("institutional_volume_spike")
class InstitutionalVolumeSpike(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="institutional_volume_spike",
            display_name="Institutional Volume Spike",
            description="Flags bars with volume well above its recent average that also closed decisively in one direction, as a proxy for large-participant activity.",
            category="volume",
            default_params={"volume_ma_period": 20, "volume_multiplier": 2.5},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        avg_volume = out["volume"].rolling(window=p["volume_ma_period"], min_periods=p["volume_ma_period"]).mean()
        is_huge_volume = out["volume"] > avg_volume * p["volume_multiplier"]

        out["institutional_buy_volume"] = is_huge_volume & (out["close"] > out["open"])
        out["institutional_sell_volume"] = is_huge_volume & (out["close"] < out["open"])
        return out
