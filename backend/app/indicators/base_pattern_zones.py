"""
Base Pattern Zones.

A different zone-detection methodology from
app.indicators.supply_demand_zones (which seeds a zone from a single
confirmed pivot bar): this looks for the classic "leg-in, base,
leg-out" candlestick pattern -- one to a few small-bodied consolidation
candles (the "base") sandwiched between two decisive, large-bodied
candles (the "legs"). The base itself becomes the zone, classified by
its leg directions into one of four textbook types:

- RBR (Rally-Base-Rally): both legs bullish -- a demand zone
- DBR (Drop-Base-Rally): leg-in bearish, leg-out bullish -- a demand zone
- RBD (Rally-Base-Drop): leg-in bullish, leg-out bearish -- a supply zone
- DBD (Drop-Base-Drop): both legs bearish -- a supply zone

A zone stays active until price closes back through its far (distal)
edge, at which point it's invalidated and removed -- same
non-repainting, stateful zone-lifecycle idea as supply_demand_zones,
just with this pattern's own seeding rule and up to `max_base_candles`
consolidation bars per base instead of a single pivot bar.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("base_pattern_zones")
class BasePatternZones(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="base_pattern_zones",
            display_name="Base Pattern Zones",
            description="Leg-in/base/leg-out candlestick zones (RBR/DBR/RBD/DBD), classified as demand or supply by their leg directions and invalidated when price closes back through the zone.",
            category="price_action",
            default_params={
                "leg_body_pct": 0.5,
                "base_body_pct": 0.5,
                "max_base_candles": 3,
                "max_zones_per_side": 5,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        candle_range = out["high"] - out["low"]
        body = (out["close"] - out["open"]).abs()
        body_pct = (body / candle_range.replace(0, np.nan)).fillna(0.0)

        is_base = body_pct <= p["base_body_pct"]
        is_bull_leg = (body_pct >= p["leg_body_pct"]) & (out["close"] > out["open"])
        is_bear_leg = (body_pct >= p["leg_body_pct"]) & (out["close"] < out["open"])

        is_base_arr = is_base.to_numpy()
        is_bull_leg_arr = is_bull_leg.to_numpy()
        is_bear_leg_arr = is_bear_leg.to_numpy()
        high, low = out["high"].to_numpy(), out["low"].to_numpy()
        open_, close = out["open"].to_numpy(), out["close"].to_numpy()
        n = len(out)
        max_base = p["max_base_candles"]
        max_zones = p["max_zones_per_side"]

        demand_top = np.full(n, np.nan)
        demand_bottom = np.full(n, np.nan)
        supply_top = np.full(n, np.nan)
        supply_bottom = np.full(n, np.nan)
        demand_zone_type = pd.Series([None] * n, index=out.index, dtype=object)
        supply_zone_type = pd.Series([None] * n, index=out.index, dtype=object)

        demand_zones: list[tuple[float, float, str]] = []  # (proximal, distal, type)
        supply_zones: list[tuple[float, float, str]] = []

        for i in range(n):
            # Look for leg-out at i, a run of 1..max_base base candles just
            # before it, then a leg-in just before the base.
            if is_bull_leg_arr[i] or is_bear_leg_arr[i]:
                base_len = 0
                j = i - 1
                while base_len < max_base and j >= 0 and is_base_arr[j]:
                    base_len += 1
                    j -= 1
                leg_in_bar = j
                if base_len > 0 and leg_in_bar >= 0 and (is_bull_leg_arr[leg_in_bar] or is_bear_leg_arr[leg_in_bar]):
                    leg_out_bull = is_bull_leg_arr[i]
                    leg_in_bull = is_bull_leg_arr[leg_in_bar]
                    zone_type = {
                        (True, True): "RBR",
                        (False, True): "DBR",
                        (True, False): "RBD",
                        (False, False): "DBD",
                    }[(leg_in_bull, leg_out_bull)]
                    is_demand = zone_type in ("RBR", "DBR")

                    base_start, base_end = leg_in_bar + 1, i - 1
                    base_open = open_[base_start:base_end + 1]
                    base_close = close[base_start:base_end + 1]
                    base_low = low[base_start:base_end + 1]
                    base_high = high[base_start:base_end + 1]
                    if is_demand:
                        # proximal (near price, above) is the top; distal
                        # (the base's own extreme low, farther from price)
                        # is the bottom -- invalidated by a close below it.
                        top = float(np.maximum(base_open, base_close).max())
                        bottom = float(base_low.min())
                        demand_zones.append((top, bottom, zone_type))
                        if len(demand_zones) > max_zones:
                            demand_zones.pop(0)
                    else:
                        # proximal (near price, below) is the bottom; distal
                        # (the base's own extreme high, farther from price)
                        # is the top -- invalidated by a close above it.
                        top = float(base_high.max())
                        bottom = float(np.minimum(base_open, base_close).min())
                        supply_zones.append((top, bottom, zone_type))
                        if len(supply_zones) > max_zones:
                            supply_zones.pop(0)

            demand_zones = [(top, bot, t) for top, bot, t in demand_zones if not (close[i] < bot)]
            supply_zones = [(top, bot, t) for top, bot, t in supply_zones if not (close[i] > top)]

            if demand_zones:
                demand_top[i], demand_bottom[i], dt = demand_zones[-1]
                demand_zone_type.iloc[i] = dt
            if supply_zones:
                supply_top[i], supply_bottom[i], st = supply_zones[-1]
                supply_zone_type.iloc[i] = st

        out["bpz_demand_top"] = demand_top
        out["bpz_demand_bottom"] = demand_bottom
        out["bpz_demand_type"] = demand_zone_type
        out["bpz_supply_top"] = supply_top
        out["bpz_supply_bottom"] = supply_bottom
        out["bpz_supply_type"] = supply_zone_type
        return out
