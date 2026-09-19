"""
Clustered Pivot S/R Levels.

Confirmed swing highs/lows within a trailing lookback window are
greedily merged into clusters (each new pivot joins the nearest
existing cluster if within `cluster_tolerance_pct` of its running
average price, else starts a new one); clusters are ranked by hit
count as a proxy for "how many times price reacted here." Rather than
the source script's on-chart "draw the 5 strongest lines" (only
meaningful as a snapshot on the last bar), this exposes the nearest
support and nearest resistance level from the top-ranked clusters as
two numeric series, updated non-repainting each time a new pivot
confirms and held constant between updates -- so it can be used in a
backtest without looking ahead at price structure that hadn't formed
yet.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("clustered_pivot_sr_levels")
class ClusteredPivotSRLevels(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="clustered_pivot_sr_levels",
            display_name="Clustered Pivot S/R Levels",
            description="Nearest support/resistance from swing pivots clustered by proximity and ranked by hit count, updated each time a new pivot confirms.",
            category="price_action",
            default_params={
                "pivot_range": 10,
                "lookback": 500,
                "cluster_tolerance_pct": 0.5,
                "top_n_levels": 5,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        left = right = p["pivot_range"]
        window = left + right + 1
        lookback, tol_pct, top_n = p["lookback"], p["cluster_tolerance_pct"], p["top_n_levels"]

        high = out["high"].to_numpy()
        low = out["low"].to_numpy()
        close = out["close"].to_numpy()

        high_mask = out["high"].rolling(window, min_periods=window).apply(
            lambda w: w[left] == w.max() and (w == w[left]).sum() == 1, raw=True
        ).astype(bool).shift(-right, fill_value=False).to_numpy()
        low_mask = out["low"].rolling(window, min_periods=window).apply(
            lambda w: w[left] == w.min() and (w == w[left]).sum() == 1, raw=True
        ).astype(bool).shift(-right, fill_value=False).to_numpy()

        n = len(out)
        nearest_resistance = np.full(n, np.nan)
        nearest_support = np.full(n, np.nan)

        pool: list[tuple[int, float]] = []  # (bar_index, price)
        cur_res, cur_sup = np.nan, np.nan

        for i in range(n):
            new_pivot = False
            if high_mask[i]:
                pool.append((i, high[i]))
                new_pivot = True
            if low_mask[i]:
                pool.append((i, low[i]))
                new_pivot = True

            if new_pivot:
                pool = [(b, px) for b, px in pool if i - b <= lookback]
                cluster_prices: list[float] = []
                cluster_hits: list[int] = []
                for _, price in pool:
                    tol = price * tol_pct / 100.0
                    merged = False
                    for j, cp in enumerate(cluster_prices):
                        if abs(cp - price) <= tol:
                            hits = cluster_hits[j]
                            cluster_prices[j] = (cp * hits + price) / (hits + 1)
                            cluster_hits[j] = hits + 1
                            merged = True
                            break
                    if not merged:
                        cluster_prices.append(price)
                        cluster_hits.append(1)

                ranked = sorted(zip(cluster_prices, cluster_hits), key=lambda x: -x[1])[:top_n]
                levels = [lvl for lvl, _ in ranked]

                above = [lvl for lvl in levels if lvl >= close[i]]
                below = [lvl for lvl in levels if lvl <= close[i]]
                cur_res = min(above) if above else np.nan
                cur_sup = max(below) if below else np.nan

            nearest_resistance[i] = cur_res
            nearest_support[i] = cur_sup

        out["clustered_sr_nearest_resistance"] = nearest_resistance
        out["clustered_sr_nearest_support"] = nearest_support
        return out
