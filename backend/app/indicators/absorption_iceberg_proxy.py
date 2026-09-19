"""
Absorption / Iceberg Proxy.

Flags bars with unusually HIGH volume packed into an unusually TIGHT
range -- a lot of size traded without price actually moving, read as
a proxy for a large resting order "absorbing" flow (an iceberg)
rather than genuine directional participation. Distinct from
app.indicators.institutional_volume_spike (a volume spike paired with
a DIRECTIONAL close, the opposite signature -- size moving price)
and from app.indicators.atr_strong_bar (a big range, not a tight one).

`near_prior_day_extreme_pct` (off by default, i.e. 0) optionally gates
the flag to bars trading within that %-of-price tolerance of the
prior session's high or low -- the source script's default behavior
of only caring about absorption AT a known level, adapted from a
fixed-point tolerance (instrument-price-scale dependent) to a
percentage one so it works across instruments.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("absorption_iceberg_proxy")
class AbsorptionIcebergProxy(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="absorption_iceberg_proxy",
            display_name="Absorption / Iceberg Proxy",
            description="Flags bars with high volume packed into a tight range -- a proxy for a large resting order absorbing flow rather than moving price.",
            category="volume",
            default_params={
                "volume_lookback": 20,
                "range_lookback": 20,
                "volume_multiplier": 1.8,
                "range_multiplier": 0.6,
                "near_prior_day_extreme_pct": 0.0,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("AbsorptionIcebergProxy requires a DatetimeIndex.")
        out = df.copy()

        avg_vol = out["volume"].rolling(p["volume_lookback"], min_periods=p["volume_lookback"]).mean()
        bar_range = out["high"] - out["low"]
        avg_range = bar_range.rolling(p["range_lookback"], min_periods=p["range_lookback"]).mean()

        high_vol = out["volume"] > avg_vol * p["volume_multiplier"]
        tight_range = bar_range < avg_range * p["range_multiplier"]
        absorption = high_vol & tight_range

        if p["near_prior_day_extreme_pct"] > 0:
            session_date = pd.Series(out.index.date, index=out.index)
            daily_high = out["high"].groupby(session_date).transform("max")
            daily_low = out["low"].groupby(session_date).transform("min")
            prior_high = daily_high.groupby(session_date).first().shift(1)
            prior_low = daily_low.groupby(session_date).first().shift(1)
            prior_day_high = session_date.map(prior_high)
            prior_day_low = session_date.map(prior_low)

            tol = out["close"] * p["near_prior_day_extreme_pct"] / 100
            near_high = (out["close"] - prior_day_high).abs() <= tol
            near_low = (out["close"] - prior_day_low).abs() <= tol
            absorption = absorption & (near_high | near_low)

        out["absorption_iceberg_proxy"] = absorption
        return out
