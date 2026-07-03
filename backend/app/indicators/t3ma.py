"""T3 Moving Average (Tim Tillson) — a six-pass EMA cascade blended by a volume factor, smoother than DEMA/TEMA with less overshoot."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _gd(series: pd.Series, n: int, volume_factor: float) -> pd.Series:
    """Generalized DEMA: a single blended EMA pass used to build up T3."""
    ema = series.ewm(span=n, adjust=False, min_periods=n).mean()
    ema_of_ema = ema.ewm(span=n, adjust=False, min_periods=n).mean()
    return ema * (1 + volume_factor) - ema_of_ema * volume_factor


@indicator_registry.register("t3ma")
class T3MA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="t3ma",
            display_name="T3 Moving Average",
            description="Six-pass EMA cascade (Tillson's T3) -- smoother than DEMA/TEMA with less overshoot.",
            category="overlap",
            default_params={"period": 5, "volume_factor": 0.7, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, vf = p["period"], p["volume_factor"]

        stage1 = _gd(out[p["source"]], n, vf)
        stage2 = _gd(stage1, n, vf)
        out[f"t3ma_{n}"] = _gd(stage2, n, vf)
        return out
