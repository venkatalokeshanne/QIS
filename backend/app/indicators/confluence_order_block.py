"""
Confluence Order Block.

Detects order-block zones using a 4-component confluence score (ATR
displacement, percent displacement, volume pivot, structure alignment)
and tracks each zone's lifecycle -- activation, mitigation, expiry, and
consumption on first touch -- causally, bar by bar.

Trade rules (entry fill, stop/target, position sizing) are NOT here --
see app.strategies.confluence_order_block.strategy, which overrides
Strategy.run() because this algorithm's execution model (limit fills at
the zone edge, a stop anchored to the zone's *formation-bar* ATR) can't
be expressed through the shared entries/exits + simulate_trades contract
every other strategy uses.

Two off-by-one gotchas are load-bearing for causality and are the reason
this is a sequential loop rather than a vectorized computation:
    - volPivot[i] describes candle i - volLen; only knowable at bar i.
    - the structure-state window at bar i includes bar i itself; the
      *tested* bar is i - osLen.
    - zone detection's confirmation must break on the FIRST bar the
      score threshold is met, using only data available at that bar --
      accumulating flags across the whole impulse window and recording
      an earlier confirmation bar leaks future data.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@dataclass
class _Zone:
    direction: int  # +1 demand/bullish, -1 supply/bearish
    ob_index: int
    confirm_index: int
    top: float
    bottom: float
    atr_at_formation: float


def _compute_os_state(high: np.ndarray, low: np.ndarray, os_len: int) -> np.ndarray:
    """Latching structure state: 1 = last confirmed swing was a low, 0 = a high.

    The window at bar i is high/low[i-osLen+1 .. i] (includes i); the bar
    being TESTED against that window is i-osLen, one bar older still.
    """
    n = len(high)
    os = np.zeros(n, dtype=int)
    state = 0
    for i in range(n):
        if i >= os_len:
            window_high = high[i - os_len + 1 : i + 1].max()
            window_low = low[i - os_len + 1 : i + 1].min()
            if high[i - os_len] > window_high:
                state = 0
            elif low[i - os_len] < window_low:
                state = 1
        os[i] = state
    return os


def _compute_vol_pivot(volume: np.ndarray, vol_len: int) -> np.ndarray:
    """True at bar i when candle i-volLen's volume is a strict local max
    over volLen bars each side -- only knowable once those later bars exist.
    """
    n = len(volume)
    vol_pivot = np.zeros(n, dtype=bool)
    for i in range(2 * vol_len, n):
        p = i - vol_len
        left = volume[p - vol_len : p]
        right = volume[p + 1 : p + 1 + vol_len]
        if len(left) < vol_len or len(right) < vol_len:
            continue
        vol_pivot[i] = bool(volume[p] > left.max() and volume[p] > right.max())
    return vol_pivot


def _detect_zones(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    atr: np.ndarray,
    os: np.ndarray,
    vol_pivot: np.ndarray,
    *,
    impulse_bars: int,
    disp_atr: float,
    disp_pct: float,
    vol_len: int,
    min_score: int,
    zone_width: str,
) -> list[_Zone]:
    n = len(close)
    zones: list[_Zone] = []
    horizon = max(impulse_bars, vol_len)

    start = 2 * vol_len + 1
    end = n - 2
    for i in range(start, end + 1):
        a = atr[i]
        if not np.isfinite(a) or a <= 0:
            continue
        thr_atr = disp_atr * a
        thr_pct = (disp_pct / 100.0) * close[i]
        vol_bar = i + vol_len
        vol_flag = vol_bar < n and bool(vol_pivot[vol_bar])
        last = min(i + horizon, n - 2)

        for direction in (1, -1):
            if direction == 1 and not (close[i] < open_[i]):
                continue
            if direction == -1 and not (close[i] > open_[i]):
                continue

            run = -np.inf if direction == 1 else np.inf
            f_disp = 0
            f_pct = 0
            confirm = None

            for k in range(i + 1, last + 1):
                # Displacement is only measured inside the impulse window.
                if k <= i + impulse_bars:
                    if direction == 1:
                        run = max(run, high[k])
                        move = run - high[i]
                    else:
                        run = min(run, low[k])
                        move = low[i] - run
                    if move >= thr_atr:
                        f_disp = 1
                    if move >= thr_pct:
                        f_pct = 1

                f_vol = 1 if (k >= vol_bar and vol_flag) else 0
                f_os = 1 if ((os[k] == 1) == (direction == 1)) else 0
                score = f_disp + f_pct + f_vol + f_os

                if score >= min_score:
                    # First bar the threshold is genuinely met -- do not
                    # keep scanning for a "better" confirmation, that
                    # would leak future data into an earlier bar.
                    confirm = k
                    break

            if confirm is None:
                continue

            mid = (high[i] + low[i]) / 2.0
            if direction == 1:
                top = mid if zone_width == "half" else high[i]
                bottom = low[i]
            else:
                top = high[i]
                bottom = mid if zone_width == "half" else low[i]

            zones.append(
                _Zone(
                    direction=direction,
                    ob_index=i,
                    confirm_index=confirm,
                    top=top,
                    bottom=bottom,
                    atr_at_formation=float(a),
                )
            )

    return zones


def _run_lifecycle(
    n: int,
    close: np.ndarray,
    low: np.ndarray,
    high: np.ndarray,
    zones: list[_Zone],
    *,
    mitigation: str,
    max_age: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    signal = np.full(n, None, dtype=object)
    zone_top = np.full(n, np.nan)
    zone_bottom = np.full(n, np.nan)
    atr_at_formation = np.full(n, np.nan)

    zones_by_confirm: dict[int, list[_Zone]] = {}
    for z in zones:
        zones_by_confirm.setdefault(z.confirm_index, []).append(z)

    active: list[_Zone] = []

    for i in range(n):
        # Step B -- age, then mitigation, then touch, oldest zone first.
        still_active: list[_Zone] = []
        consumed_this_bar = False
        for z in active:
            if i <= z.confirm_index:
                still_active.append(z)
                continue
            if (i - z.confirm_index) > max_age:
                continue  # expired

            if z.direction == 1:
                dead = (close[i] < z.bottom) if mitigation == "close" else (low[i] < z.bottom)
            else:
                dead = (close[i] > z.top) if mitigation == "close" else (high[i] > z.top)
            if dead:
                continue  # mitigated

            touched = (low[i] <= z.top) if z.direction == 1 else (high[i] >= z.bottom)
            if not touched:
                still_active.append(z)
                continue

            # First touch consumes the zone whether or not a trade
            # results -- if two zones are touched on the same bar, only
            # the first (oldest) one is reported as the signal.
            if not consumed_this_bar:
                signal[i] = "long" if z.direction == 1 else "short"
                zone_top[i] = z.top
                zone_bottom[i] = z.bottom
                atr_at_formation[i] = z.atr_at_formation
                consumed_this_bar = True
            # Either way the zone is dropped -- not re-added to still_active.

        active = still_active

        # Step C -- activate zones confirmed on this bar, AFTER Step B,
        # so a zone can never be entered on its own confirmation bar.
        for z in zones_by_confirm.get(i, []):
            active.append(z)

    return signal, zone_top, zone_bottom, atr_at_formation


@indicator_registry.register("confluence_order_block")
class ConfluenceOrderBlock(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="confluence_order_block",
            display_name="Confluence Order Block",
            description=(
                "Order-block zones confirmed by a 4-component confluence score (ATR "
                "displacement, percent displacement, volume pivot, structure alignment); "
                "each zone is tracked causally through activation, mitigation, expiry, "
                "and first-touch consumption."
            ),
            category="price_action",
            default_params={
                "atr_len": 14,
                "impulse_bars": 5,
                "disp_atr": 2.0,
                "disp_pct": 1.0,
                "vol_len": 5,
                "os_len": 5,
                "min_score": 3,
                "zone_width": "half",
                "mitigation": "close",
                "max_age": 60,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = len(out)

        atr = wilders_smooth(true_range(out), p["atr_len"]).to_numpy()
        open_ = out["open"].to_numpy(dtype=float)
        high = out["high"].to_numpy(dtype=float)
        low = out["low"].to_numpy(dtype=float)
        close = out["close"].to_numpy(dtype=float)
        volume = out["volume"].to_numpy(dtype=float)

        os_state = _compute_os_state(high, low, p["os_len"])
        vol_pivot = _compute_vol_pivot(volume, p["vol_len"])

        zones = _detect_zones(
            open_,
            high,
            low,
            close,
            atr,
            os_state,
            vol_pivot,
            impulse_bars=p["impulse_bars"],
            disp_atr=p["disp_atr"],
            disp_pct=p["disp_pct"],
            vol_len=p["vol_len"],
            min_score=p["min_score"],
            zone_width=p["zone_width"],
        )

        signal, zone_top, zone_bottom, atr_at_formation = _run_lifecycle(
            n,
            close,
            low,
            high,
            zones,
            mitigation=p["mitigation"],
            max_age=p["max_age"],
        )

        out["cob_signal"] = signal
        out["cob_zone_top"] = zone_top
        out["cob_zone_bottom"] = zone_bottom
        out["cob_atr_at_formation"] = atr_at_formation
        return out
