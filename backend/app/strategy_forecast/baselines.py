"""
Phase 1 baselines -- no machine learning, on purpose.

Each predictor sees only days strictly before the one it is scoring: state is
updated after a day is evaluated, never before, so the walk-forward is a
property of the code rather than a convention to remember. Rates are shrunk
toward the day's base rate (5 / candidates), so a strategy that was top-5 once
out of one appearance does not outrank one that was top-5 forty times out of
a hundred -- the small-sample trap this dataset is full of.

    RANDOM        control: the base rate, nothing learned
    PERSISTENCE   yesterday's top 5 (the naive rule the spec rejects; kept as
                  a control, because a model that cannot beat it is worthless)
    GLOBAL        P(top5 | strategy)
    TICKER        P(top5 | strategy, ticker)
    REGIME        P(top5 | strategy, market regime)
    TICKER_REGIME P(top5 | strategy, ticker, ticker regime)
    FAMILY        P(top5 | family) spread over that family's members
    RECENT        P(top5 | strategy) over the last N days only
    TRIGGER       P(trigger) x P(top5 | triggered), the spec's decomposition
"""

from __future__ import annotations

from collections import defaultdict, deque

import numpy as np
import pandas as pd

ALPHA = 20.0          # shrinkage strength, in "pseudo-observations"
RECENT_DAYS = 20


class _Rate:
    """Shrunk success rate per key, updated observation by observation."""

    def __init__(self, alpha: float = ALPHA):
        self.hit: dict = defaultdict(float)
        self.n: dict = defaultdict(float)
        self.alpha = alpha

    def add(self, key, hit: float) -> None:
        self.hit[key] += hit
        self.n[key] += 1

    def rate(self, key, prior: float) -> float:
        n = self.n.get(key, 0.0)
        return (self.hit.get(key, 0.0) + self.alpha * prior) / (n + self.alpha)

    def count(self, key) -> int:
        return int(self.n.get(key, 0))


class Predictor:
    name = "base"
    needs_state = True

    def score(self, day: pd.DataFrame, prior: float) -> np.ndarray:
        raise NotImplementedError

    def update(self, day: pd.DataFrame) -> None:
        pass

    # evidence shown alongside a pick (sample size etc.)
    def evidence(self, day: pd.DataFrame) -> list[dict]:
        return [{} for _ in range(len(day))]


class Random(Predictor):
    name = "RANDOM"

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)

    def score(self, day, prior):
        return self.rng.random(len(day))


class Persistence(Predictor):
    """Yesterday's top 5 for this ticker -- the rule the spec says not to build."""

    name = "PERSISTENCE"

    def __init__(self):
        self.last: dict[str, dict[str, float]] = {}

    def score(self, day, prior):
        ticker = day["ticker"].iloc[0]
        last = self.last.get(ticker, {})
        return day["strategy"].map(lambda s: last.get(s, 0.0)).to_numpy()

    def update(self, day):
        ticker = day["ticker"].iloc[0]
        self.last[ticker] = {r.strategy: 1.0 / r.rank for r in day.itertuples() if r.rank <= 5}


class KeyedRate(Predictor):
    """P(top5 | key(row)) with shrinkage, optionally falling back to a coarser key."""

    def __init__(self, name: str, keys, target: str = "top5", fallback: "KeyedRate | None" = None,
                 alpha: float = ALPHA, min_obs: int = 0):
        self.name = name
        self.keys = keys                       # callable(row) -> hashable
        self.target = target
        self.rate = _Rate(alpha)
        self.fallback = fallback
        self.min_obs = min_obs

    def score(self, day, prior):
        out = np.empty(len(day))
        fb = self.fallback.score(day, prior) if self.fallback is not None else None
        for i, row in enumerate(day.itertuples()):
            key = self.keys(row)
            if self.min_obs and self.rate.count(key) < self.min_obs and fb is not None:
                out[i] = fb[i]
            else:
                out[i] = self.rate.rate(key, prior)
        return out

    def update(self, day):
        for row in day.itertuples():
            self.rate.add(self.keys(row), float(getattr(row, self.target)))
        if self.fallback is not None:
            self.fallback.update(day)

    def evidence(self, day):
        return [{"observations": self.rate.count(self.keys(r)),
                 "hits": int(self.rate.hit.get(self.keys(r), 0))} for r in day.itertuples()]


class FamilyRate(KeyedRate):
    """Evidence pooled to the family, for strategies with too few days of their own."""

    def __init__(self, family_map: dict[str, str], target: str = "top5", alpha: float = ALPHA):
        super().__init__("FAMILY", lambda r: family_map.get(r.strategy, "unknown"), target, alpha=alpha)
        self.family_map = family_map


class Recent(Predictor):
    """Same as GLOBAL but only over the last `days` trading days."""

    name = "RECENT"

    def __init__(self, days: int = RECENT_DAYS, target: str = "top5", alpha: float = ALPHA):
        self.window: deque = deque(maxlen=days)
        self.target, self.alpha = target, alpha

    def _rates(self) -> tuple[dict, dict]:
        hit, n = defaultdict(float), defaultdict(float)
        for day in self.window:
            for strategy, value in day:
                hit[strategy] += value
                n[strategy] += 1
        return hit, n

    def score(self, day, prior):
        hit, n = self._rates()
        return np.array([(hit.get(s, 0.0) + self.alpha * prior) / (n.get(s, 0.0) + self.alpha)
                         for s in day["strategy"]])

    def update(self, day):
        self.window.append([(r.strategy, float(getattr(r, self.target))) for r in day.itertuples()])


class TriggerDecomposition(Predictor):
    """P(top5) = P(trigger) x P(top5 | triggered) -- keeps "did not fire" and
    "fired and lost" as the different things they are."""

    name = "TRIGGER"

    def __init__(self, alpha: float = ALPHA):
        self.trigger = _Rate(alpha)
        self.top5_given = _Rate(alpha)

    def score(self, day, prior):
        out = np.empty(len(day))
        for i, row in enumerate(day.itertuples()):
            key = (row.ticker, row.strategy)
            p_trigger = self.trigger.rate(key, 0.3)
            p_top5 = self.top5_given.rate(key, prior)
            out[i] = p_trigger * p_top5
        return out

    def update(self, day):
        for row in day.itertuples():
            key = (row.ticker, row.strategy)
            self.trigger.add(key, float(row.triggered))
            if row.triggered:
                self.top5_given.add(key, float(row.top5))

    def evidence(self, day):
        return [{"p_trigger": round(self.trigger.rate((r.ticker, r.strategy), 0.3), 3),
                 "triggered_days": self.trigger.count((r.ticker, r.strategy))} for r in day.itertuples()]


def default_predictors(family_map: dict[str, str], target: str = "top5") -> list[Predictor]:
    """The five baselines the spec asks for, plus two controls and the
    trigger decomposition. GLOBAL is the fallback for the sparser keys."""
    global_rate = KeyedRate("GLOBAL", lambda r: r.strategy, target)
    return [
        Random(),
        Persistence(),
        global_rate,
        KeyedRate("TICKER", lambda r: (r.ticker, r.strategy), target,
                  fallback=KeyedRate("GLOBAL_fb", lambda r: r.strategy, target), min_obs=20),
        KeyedRate("REGIME", lambda r: (r.market_regime, r.strategy), target,
                  fallback=KeyedRate("GLOBAL_fb", lambda r: r.strategy, target), min_obs=20),
        KeyedRate("TICKER_REGIME", lambda r: (r.ticker, r.ticker_regime, r.strategy), target,
                  fallback=KeyedRate("GLOBAL_fb", lambda r: r.strategy, target), min_obs=20),
        FamilyRate(family_map, target),
        Recent(RECENT_DAYS, target),
        TriggerDecomposition(),
    ]
