"""
Supply & Demand Zones.

Each confirmed swing high seeds a "supply" zone (the pivot bar's
high-to-body range); each confirmed swing low seeds a "demand" zone.
A zone stays active, extending forward, until price trades back INTO
its range -- that retest consumes it (removed, non-repainting: once
retested it's gone for good, matching the source's remove-on-retest
behavior). Up to `max_zones_per_side` most recent zones are tracked
per side.

Exposed as the nearest still-active supply/demand zone boundaries as
of each bar (for use as dynamic S/R levels) plus retest-event flags,
computed with an explicit bar-by-bar loop since zone lifecycle
(creation, extension, removal-on-retest) is inherently stateful.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("supply_demand_zones")
class SupplyDemandZones(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="supply_demand_zones",
            display_name="Supply & Demand Zones",
            description="Pivot-seeded supply/demand zones that stay active until price retests them; exposes the nearest active zone on each side plus retest events.",
            category="price_action",
            default_params={"pivot_range": 8, "max_zones_per_side": 6, "use_wick": True},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        left = right = p["pivot_range"]
        window = left + right + 1
        max_zones = p["max_zones_per_side"]

        def is_pivot_high(w: np.ndarray) -> bool:
            return w[left] == w.max() and (w == w[left]).sum() == 1

        def is_pivot_low(w: np.ndarray) -> bool:
            return w[left] == w.min() and (w == w[left]).sum() == 1

        high_mask = out["high"].rolling(window, min_periods=window).apply(is_pivot_high, raw=True).astype(bool).shift(
            -right, fill_value=False
        ).to_numpy()
        low_mask = out["low"].rolling(window, min_periods=window).apply(is_pivot_low, raw=True).astype(bool).shift(
            -right, fill_value=False
        ).to_numpy()

        high, low = out["high"].to_numpy(), out["low"].to_numpy()
        open_, close = out["open"].to_numpy(), out["close"].to_numpy()
        n = len(out)

        supply_top = np.full(n, np.nan)
        supply_bottom = np.full(n, np.nan)
        demand_top = np.full(n, np.nan)
        demand_bottom = np.full(n, np.nan)
        supply_retest = np.zeros(n, dtype=bool)
        demand_retest = np.zeros(n, dtype=bool)

        supply_zones: list[tuple[float, float]] = []  # (top, bottom), most recent last
        demand_zones: list[tuple[float, float]] = []

        for i in range(n):
            if high_mask[i]:
                pivot = i - right
                top = high[pivot] if p["use_wick"] else max(open_[pivot], close[pivot])
                bottom = low[pivot] if p["use_wick"] else min(open_[pivot], close[pivot])
                supply_zones.append((top, bottom))
                if len(supply_zones) > max_zones:
                    supply_zones.pop(0)
            if low_mask[i]:
                pivot = i - right
                top = high[pivot] if p["use_wick"] else max(open_[pivot], close[pivot])
                bottom = low[pivot] if p["use_wick"] else min(open_[pivot], close[pivot])
                demand_zones.append((top, bottom))
                if len(demand_zones) > max_zones:
                    demand_zones.pop(0)

            surviving_supply = []
            hit_supply = False
            for top, bottom in supply_zones:
                if bottom <= high[i] <= top:
                    hit_supply = True
                else:
                    surviving_supply.append((top, bottom))
            supply_zones = surviving_supply
            supply_retest[i] = hit_supply

            surviving_demand = []
            hit_demand = False
            for top, bottom in demand_zones:
                if bottom <= low[i] <= top:
                    hit_demand = True
                else:
                    surviving_demand.append((top, bottom))
            demand_zones = surviving_demand
            demand_retest[i] = hit_demand

            if supply_zones:
                supply_top[i], supply_bottom[i] = supply_zones[-1]
            if demand_zones:
                demand_top[i], demand_bottom[i] = demand_zones[-1]

        out["supply_zone_top"] = supply_top
        out["supply_zone_bottom"] = supply_bottom
        out["demand_zone_top"] = demand_top
        out["demand_zone_bottom"] = demand_bottom
        out["supply_zone_retest"] = supply_retest
        out["demand_zone_retest"] = demand_retest
        return out
