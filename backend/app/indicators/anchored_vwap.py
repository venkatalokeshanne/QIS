"""Anchored VWAP — the same cumulative (typical price * volume) / volume calculation as session VWAP, but anchored to a specific bar index instead of resetting every session."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("anchored_vwap")
class AnchoredVWAP(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="anchored_vwap",
            display_name="Anchored VWAP",
            description="Cumulative volume-weighted average price starting from a chosen anchor bar, rather than resetting every session.",
            category="overlap",
            default_params={"anchor_index": 0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        anchor = p["anchor_index"]
        if not (0 <= anchor < len(out)):
            raise ValueError(f"anchor_index {anchor} is out of range for a dataframe of length {len(out)}.")

        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        pv = typical_price * out["volume"]

        anchored_pv = pv.iloc[anchor:].cumsum()
        anchored_volume = out["volume"].iloc[anchor:].cumsum().replace(0, float("nan"))

        avwap = pd.Series(index=out.index, dtype=float)
        avwap.iloc[anchor:] = anchored_pv / anchored_volume
        out["anchored_vwap"] = avwap
        return out
