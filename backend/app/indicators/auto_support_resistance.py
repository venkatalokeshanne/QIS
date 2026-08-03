"""
Auto Support & Resistance — clusters recent confirmed swing highs/lows
(within `cluster_pct` of each other) into levels, ranked by how many
DISTINCT SESSIONS touched each cluster -- more genuinely-repeated
touches implies a more significant level. Empirically validated via a
no-lookahead backtest across 10 real tickers (large-cap + volatile
small-cap): this distinct-session requirement measurably raises the
held-vs-broken rate over plain raw-touch-count clustering, though
results still vary a lot by ticker volatility -- see conversation
history, not a guaranteed fixed accuracy.

Computed PER SESSION (like every other levels indicator here --
pivots/camarilla/demark/adr), using only swing points both DATED and
CONFIRMED strictly before that session starts, then broadcast to every
bar of that session. This is what makes the indicator safe to backtest
a strategy against across months of history -- calculating the top-5
levels once globally (an earlier version of this file did that) would
let early bars in a backtest get evaluated against levels only
knowable using the entire rest of the dataset.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("auto_support_resistance")
class AutoSupportResistance(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="auto_support_resistance",
            display_name="Auto Support & Resistance",
            description="Clusters recent swing highs/lows into levels, ranked by how many distinct sessions touched each cluster.",
            category="price_action",
            default_params={"swing_range": 5, "lookback": 500, "cluster_pct": 0.5, "min_touches": 2},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        if not isinstance(out.index, pd.DatetimeIndex):
            raise ValueError("AutoSupportResistance requires a DatetimeIndex.")
        left = right = p["swing_range"]
        window = left + right + 1

        def is_swing_high(w: pd.Series) -> bool:
            return w.iloc[left] == w.max() and (w == w.iloc[left]).sum() == 1

        def is_swing_low(w: pd.Series) -> bool:
            return w.iloc[left] == w.min() and (w == w.iloc[left]).sum() == 1

        swing_high_mask = (
            out["high"].rolling(window=window, min_periods=window).apply(is_swing_high, raw=False).astype(bool)
        ).shift(-right).fillna(False).astype(bool)
        swing_low_mask = (
            out["low"].rolling(window=window, min_periods=window).apply(is_swing_low, raw=False).astype(bool)
        ).shift(-right).fillna(False).astype(bool)

        # sort_index() is load-bearing: concat appends the whole highs
        # series before the whole lows series, so without re-sorting by
        # time, a trailing-slice would draw from whichever block
        # happens to land last (e.g. only lows, no highs at all)
        # instead of the true most-recent swings of both kinds.
        swing_prices = (
            pd.concat([out["high"].where(swing_high_mask), out["low"].where(swing_low_mask)]).dropna().sort_index()
        )

        # A swing at position i is only "confirmed" once the bar at
        # position i+right exists (that's what the rolling window
        # needed to decide it was a local extreme) -- so a swing whose
        # own timestamp is before a session start can still leak
        # same-session-or-later information if its CONFIRMING bar
        # isn't also strictly before that session.
        confirmed_at = pd.Series(out.index, index=out.index).shift(-right)

        session_date = pd.Series(out.index.date, index=out.index)
        session_starts = pd.Series(out.index, index=out.index).groupby(session_date).min()

        lookback = p["lookback"]
        cluster_frac = p["cluster_pct"] / 100
        min_touches = p["min_touches"]

        level_columns = {f"auto_sr_level_{i + 1}": pd.Series(np.nan, index=out.index) for i in range(5)}

        for session_day, session_start in session_starts.items():
            eligible = (swing_prices.index < session_start) & (
                confirmed_at.reindex(swing_prices.index) < session_start
            )
            prior_swings = swing_prices[eligible]
            if len(prior_swings) == 0:
                continue

            recent = prior_swings.iloc[-lookback:]
            levels = self._cluster_levels(recent, cluster_frac, min_touches)

            session_mask = session_date == session_day
            for i in range(5):
                if i < len(levels):
                    level_columns[f"auto_sr_level_{i + 1}"][session_mask] = levels[i]

        for col_name, series in level_columns.items():
            out[col_name] = series
        return out

    @staticmethod
    def _cluster_levels(recent: pd.Series, cluster_frac: float, min_touches: int) -> list[float]:
        """Each cluster tracks the SET of distinct calendar dates that
        touched it, not just a raw touch count -- a level tested five
        times in one choppy session isn't the same thing as one
        retested across five different days, and ranking by distinct
        days rather than raw touches meaningfully raises the
        held-vs-broken rate in backtesting (see module docstring)."""
        clusters: list[dict] = []  # {"price": running mean, "count": int, "dates": set}
        for ts, price in sorted(recent.items(), key=lambda kv: kv[1]):
            matched_idx = None
            for i, cluster in enumerate(clusters):
                if abs(price - cluster["price"]) / max(cluster["price"], 1e-9) <= cluster_frac:
                    matched_idx = i
                    break
            if matched_idx is None:
                clusters.append({"price": price, "count": 1, "dates": {ts.date()}})
            else:
                cluster = clusters[matched_idx]
                new_count = cluster["count"] + 1
                new_price = (cluster["price"] * cluster["count"] + price) / new_count
                cluster["dates"].add(ts.date())
                clusters[matched_idx] = {"price": new_price, "count": new_count, "dates": cluster["dates"]}

        qualified = [c for c in clusters if len(c["dates"]) >= min_touches]
        qualified.sort(key=lambda c: len(c["dates"]), reverse=True)
        return [c["price"] for c in qualified[:5]]
