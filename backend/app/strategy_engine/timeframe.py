"""
Timeframe compatibility (spec section 23).

A strategy runs only on the timeframes it DECLARES in the registry -- the
engine never assumes that a strategy authored on daily bars works on 5m.
Every rejection carries a reason for the "Why not?" view.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.strategy_engine.models import MinimumData, StrategyMeta, Timeframe

SUPPORTED_TIMEFRAMES = list(Timeframe)

COMPATIBLE = "COMPATIBLE"
TIMEFRAME_MISMATCH = "TIMEFRAME_MISMATCH"
DATA_MISMATCH = "DATA_MISMATCH"


@dataclass(frozen=True)
class TimeframeCheck:
    status: str
    reason: str

    @property
    def ok(self) -> bool:
        return self.status == COMPATIBLE


class TimeframeSelector:
    def parse(self, value: str) -> Timeframe:
        return Timeframe.parse(value)

    def check(self, strategy: StrategyMeta, timeframe: Timeframe) -> TimeframeCheck:
        if strategy.minimum_data is MinimumData.INTRADAY and not timeframe.is_intraday:
            return TimeframeCheck(DATA_MISMATCH, f"strategy needs intraday bars; requested {timeframe}")
        if timeframe not in strategy.timeframes:
            declared = ", ".join(str(t) for t in strategy.timeframes)
            return TimeframeCheck(TIMEFRAME_MISMATCH,
                                  f"strategy timeframe: {declared}; requested timeframe: {timeframe}")
        return TimeframeCheck(COMPATIBLE, f"{timeframe} is a declared timeframe of this strategy")
