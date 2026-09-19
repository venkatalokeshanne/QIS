"""Volume Dry-Up — current volume as a fraction of its own rolling average, with a categorical dry-up zone (a "true" volume dry-up at <=50% of average, tapering bands up to >100%). Low readings flag quiet, low-participation stretches often watched for ahead of a breakout."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("volume_dryup")
class VolumeDryUp(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volume_dryup",
            display_name="Volume Dry-Up",
            description="Volume as a fraction of its own rolling average, with a categorical dry-up zone (true dry-up at <=50% of average).",
            category="volume",
            default_params={"period": 50, "true_dryup_pct": 0.50, "zone2_pct": 0.60, "zone3_pct": 0.70},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, t1, t2, t3 = p["period"], p["true_dryup_pct"], p["zone2_pct"], p["zone3_pct"]

        vol_ma = out["volume"].rolling(window=n, min_periods=n).mean()
        pct = out["volume"] / vol_ma.replace(0, np.nan)

        zone = pd.cut(pct, bins=[-np.inf, t1, t2, t3, 1.0, np.inf], labels=["true_dryup", "zone2", "zone3", "normal", "above_average"])

        out[f"volume_dryup_pct_{n}"] = pct
        out[f"volume_dryup_zone_{n}"] = zone.astype(object)
        out[f"volume_dryup_true_{n}"] = pct <= t1
        return out
