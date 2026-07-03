"""Drawdown from All-Time-High % — percentage decline of close from its running maximum so far in the dataset."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("drawdown_from_ath")
class DrawdownFromATH(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="drawdown_from_ath",
            display_name="Drawdown from All-Time High %",
            description="Percentage decline of close from its running (cumulative) maximum.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()

        running_ath = out["close"].cummax().replace(0, np.nan)
        out["drawdown_from_ath_pct"] = (out["close"] - running_ath) / running_ath * 100
        return out
