"""Balance of Power (Igor Livshin) — where the close settled within the bar's own range, signed by open-to-close direction."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("bop")
class BalanceOfPower(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="bop",
            display_name="Balance of Power",
            description="(Close - Open) / (High - Low) -- buying vs. selling pressure within a single bar.",
            category="momentum",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        rng = (out["high"] - out["low"]).replace(0, np.nan)
        out["bop"] = (out["close"] - out["open"]) / rng
        return out
