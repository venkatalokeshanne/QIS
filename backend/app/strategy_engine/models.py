"""
Shared vocabulary of the Strategy Selection Engine.

Every layer (registry, regimes, family mapping, qualification, selector)
speaks in these enums so a decision can be logged and replayed exactly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:  # "BREAKOUT_MOMENTUM", not "Family.BREAKOUT_MOMENTUM"
        return self.value


class Family(StrEnum):
    TREND_FOLLOWING = "TREND_FOLLOWING"
    BREAKOUT_MOMENTUM = "BREAKOUT_MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    REVERSAL = "REVERSAL"
    VWAP_INTRADAY = "VWAP_INTRADAY"
    OSCILLATOR_MOMENTUM = "OSCILLATOR_MOMENTUM"
    LONG_TERM_BREAKOUT = "LONG_TERM_BREAKOUT"
    SPECIAL_ASSET_SPECIFIC = "SPECIAL_ASSET_SPECIFIC"


class Direction(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"
    BOTH = "BOTH"


class Session(StrEnum):
    PREMARKET = "PREMARKET"
    RTH = "RTH"
    AFTER_HOURS = "AFTER_HOURS"
    DAILY = "DAILY"


class AssetScope(StrEnum):
    EQUITY = "EQUITY"
    SPECIFIC_TICKER = "SPECIFIC_TICKER"


class MinimumData(StrEnum):
    INTRADAY = "INTRADAY"
    DAILY = "DAILY"


class Timeframe(StrEnum):
    """Supported timeframes. 65m and 2h are included because several of
    the ported TrendSpider strategies were authored on them."""

    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    M65 = "65m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    D1 = "1D"
    W1 = "1W"
    MN1 = "1M"

    @property
    def minutes(self) -> int:
        return TIMEFRAME_MINUTES[self]

    @property
    def is_intraday(self) -> bool:
        return self.minutes < TIMEFRAME_MINUTES[Timeframe.D1]

    @classmethod
    def parse(cls, value: str) -> "Timeframe":
        """Accepts the engine's own strings plus common aliases
        ("5min", "60min", "1day", "D", "daily", ...)."""
        key = str(value).strip()
        if key in _TIMEFRAME_ALIASES:
            return _TIMEFRAME_ALIASES[key]
        low = key.lower()
        if low in _TIMEFRAME_ALIASES_LOWER:
            return _TIMEFRAME_ALIASES_LOWER[low]
        raise ValueError(f"unknown timeframe {value!r}; supported: {[t.value for t in cls]}")


TIMEFRAME_MINUTES = {
    Timeframe.M1: 1, Timeframe.M5: 5, Timeframe.M15: 15, Timeframe.M30: 30, Timeframe.M65: 65,
    Timeframe.H1: 60, Timeframe.H2: 120, Timeframe.H4: 240,
    Timeframe.D1: 1440, Timeframe.W1: 10080, Timeframe.MN1: 43200,
}

_TIMEFRAME_ALIASES = {t.value: t for t in Timeframe}
_TIMEFRAME_ALIASES_LOWER = {
    "1min": Timeframe.M1, "5min": Timeframe.M5, "15min": Timeframe.M15, "30min": Timeframe.M30,
    "65min": Timeframe.M65, "60min": Timeframe.H1, "1h": Timeframe.H1, "1hour": Timeframe.H1,
    "120min": Timeframe.H2, "2h": Timeframe.H2, "240min": Timeframe.H4, "4h": Timeframe.H4,
    "1d": Timeframe.D1, "1day": Timeframe.D1, "d": Timeframe.D1, "daily": Timeframe.D1,
    "1w": Timeframe.W1, "1week": Timeframe.W1, "w": Timeframe.W1, "weekly": Timeframe.W1,
    "1month": Timeframe.MN1, "monthly": Timeframe.MN1,
}


@dataclass(frozen=True)
class StrategyMeta:
    """One entry of the strategy registry (spec section 24)."""

    id: int
    slug: str                      # QIS strategy name, e.g. "ts_orb_long_15_min"
    name: str                      # human name, e.g. "ORB Long 15-Min"
    family: Family                 # primary family
    secondary_families: tuple[Family, ...]
    direction: Direction
    timeframes: tuple[Timeframe, ...]
    asset_scope: AssetScope
    allowed_tickers: tuple[str, ...]
    session: Session
    minimum_data: MinimumData
    uses_premarket: bool           # edge is evaluated per premarket regime
    requires_premarket_data: bool  # cannot be evaluated without premarket bars
    requires_event_data: bool      # e.g. earnings strategies
    runnable: bool                 # can QIS execute it (all indicators mapped)?
    not_runnable_reason: str = ""
    source: str = ""               # where the strategy came from
    classification: dict = field(default_factory=dict)  # original user family/setup, for traceability

    @property
    def all_families(self) -> tuple[Family, ...]:
        return (self.family, *self.secondary_families)

    def to_dict(self) -> dict:
        d = asdict(self)
        for key in ("family", "direction", "asset_scope", "session", "minimum_data"):
            d[key] = str(d[key])
        d["secondary_families"] = [str(f) for f in self.secondary_families]
        d["timeframes"] = [str(t) for t in self.timeframes]
        d["allowed_tickers"] = list(self.allowed_tickers)
        return d
