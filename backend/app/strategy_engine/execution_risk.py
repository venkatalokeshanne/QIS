"""
Execution realism of a strategy's own exit rules.

A backtest fills a stop exactly at its level. A real fill slips through it,
and the tighter the stop the more that matters: at 30m/65m bar resolution a
stop a few basis points from entry is essentially a coin flip that the
backtest always wins. Strategies like that can show a high profit factor
built from many tiny "losses" that would be larger in practice.

This does not disqualify a strategy -- it is reported as a warning so the
reason is visible, and cost stress (0-3x) still applies on top.
"""

from __future__ import annotations

from functools import lru_cache

# A stop closer than this to the entry cannot be trusted at intraday bar
# resolution: a typical 30m bar's range is many times wider.
MIN_TRUSTED_STOP = 0.0025


@lru_cache(maxsize=1)
def _stops() -> dict[str, float]:
    from app.strategies.trendspider.strategy import _risk_settings, load_models

    out = {}
    for slug, model in load_models().items():
        sl = _risk_settings(model).get("stop_loss_pct")
        if sl is not None:
            out[slug] = float(sl)
    return out


def stop_pct(slug: str) -> float | None:
    """The strategy's stop-loss distance as a fraction of entry price, if it
    declares a percentage stop."""
    stops = _stops()
    return stops.get(slug.replace("ts_", "", 1), stops.get(slug))


def fragility(slug: str) -> dict:
    """{'status': OK | FRAGILE_STOP | NO_STOP, 'stop_pct': float | None, 'note': str}"""
    sl = stop_pct(slug)
    if sl is None:
        return {"status": "NO_STOP", "stop_pct": None, "note": "no percentage stop; exits come from the strategy's rules"}
    if sl < MIN_TRUSTED_STOP:
        return {"status": "FRAGILE_STOP", "stop_pct": sl,
                "note": f"stop is {sl * 100:.2f}% from entry -- tighter than bar resolution can honour, so backtest "
                        f"fills at the stop level are optimistic and real losses would be larger"}
    return {"status": "OK", "stop_pct": sl, "note": f"stop {sl * 100:.2f}% from entry"}
