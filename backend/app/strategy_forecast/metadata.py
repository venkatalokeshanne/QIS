"""
Strategy metadata -- the catalog as data, not anonymous names.

Families come from two places and are reconciled here: the platform's own
strategies declare a category (trend_following, mean_reversion, breakout,
momentum, price_action, volatility), while the ported TrendSpider ones all
declare the placeholder "trendspider" and carry their real family in the
strategy-engine catalog. Family matters because individual strategies often
have too few observations to judge alone, so evidence is pooled up a level.
"""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from app.strategies.registry import discover_strategies, get_strategy, strategy_registry

PLACEHOLDER = "trendspider"


@lru_cache(maxsize=1)
def strategy_metadata() -> pd.DataFrame:
    discover_strategies()
    try:                                                    # real families for the ported strategies
        from app.strategy_engine.registry import default_registry
        catalog = {s.slug: s for s in default_registry().all()}
    except Exception:
        catalog = {}
    rows = []
    for name in sorted(strategy_registry.names()):
        meta = get_strategy(name).metadata
        family = getattr(meta, "category", None)
        entry = catalog.get(name)
        if (family in (None, PLACEHOLDER)) and entry is not None:
            family = str(entry.family).lower()
        indicators = list(getattr(meta, "indicators_used", []) or [])
        rows.append({
            "strategy": name,
            "display_name": getattr(meta, "display_name", name),
            "family": (family or "unknown").lower(),
            "source": "trendspider" if name.startswith("ts_") else "platform",
            "direction": "long" if entry is None else str(getattr(entry, "direction", "long")).lower(),
            "authored_timeframes": "" if entry is None else ",".join(str(t) for t in entry.timeframes),
            "indicator_count": len(indicators),
            "indicators": ",".join(indicators[:8]),
        })
    return pd.DataFrame(rows)


def family_map() -> dict[str, str]:
    m = strategy_metadata()
    return dict(zip(m["strategy"], m["family"]))
