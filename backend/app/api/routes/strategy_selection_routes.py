"""
Strategy Selection Engine API (spec section 51).

GET /api/strategy-selection/{ticker}?timeframe=5m&timestamp=<ISO, optional>&include_premarket=true

Deterministic and reproducible: the same ticker/timeframe/timestamp with the
same data, configuration and catalog versions returns the same answer, and
every call is logged (selection_log) with those versions. The engine never
returns trade signals -- only which strategies have historically qualified
for conditions like the requested moment, and why (or why not).
"""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.strategy_engine.registry import default_registry

router = APIRouter(prefix="/api/strategy-selection", tags=["strategy-selection"])


@router.get("/catalog")
def strategy_catalog():
    reg = default_registry()
    return {"version": reg.version, "strategies": [s.to_dict() for s in reg.all()]}


@router.get("/{ticker}")
def select_strategies(
    ticker: str,
    timeframe: str = Query("5m", description="1m 5m 15m 30m 65m 1h 2h 4h 1D 1W 1M"),
    timestamp: str | None = Query(None, description="decision time (ISO); naive values are America/New_York; default = now"),
    include_premarket: bool = Query(True),
):
    from app.strategy_engine.data.providers import TastytradeProvider
    from app.strategy_engine.models import Timeframe
    from app.strategy_engine.selector import StrategySelector

    try:
        tf = Timeframe.parse(timeframe)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    try:
        ts = pd.Timestamp(timestamp) if timestamp else None
    except ValueError:
        raise HTTPException(status_code=422, detail=f"invalid timestamp {timestamp!r}") from None

    result = StrategySelector(earnings_provider=TastytradeProvider()).select(ticker, tf, ts, include_premarket)
    m, t, p = result.market_regime, result.ticker_regime, result.premarket_regime
    return {
        "ticker": result.ticker,
        "timeframe": result.timeframe,
        "decision_ts": result.decision_ts,
        "status": result.status,
        "market_regime": {
            "status": m.get("status"), "as_of": m.get("as_of"), "direction": m.get("direction"),
            "trend_strength": m.get("trend_strength"), "volatility": m.get("volatility"), "breadth": m.get("breadth"),
            "market_premarket": m.get("market_premarket"), "regime": m.get("market_regime"), "confidence": m.get("confidence"),
            "reasons": m.get("reasons"), "symbols": m.get("symbols"), "volatility_inputs": m.get("volatility_inputs"),
        },
        "ticker_regime": {
            "status": t.get("status"), "as_of": t.get("as_of"), "trend": t.get("trend"), "momentum": t.get("momentum"),
            "relative_strength": t.get("relative_strength"), "volatility": t.get("volatility"), "volume": t.get("volume"),
            "gap": t.get("gap"), "gap_direction": t.get("gap_direction"), "liquidity": t.get("liquidity"),
            "event_status": t.get("event_status"), "regime": t.get("ticker_regime"), "confidence": t.get("confidence"),
            "reasons": t.get("reasons"), "warnings": t.get("warnings"), "features": t.get("features"),
        },
        "premarket_regime": {
            "status": p.get("status"), "data_through": p.get("premarket_data_through"), "direction": p.get("direction"),
            "change_pct": p.get("change_pct"), "structure": p.get("structure"), "volume": p.get("volume"),
            "premarket_rvol": p.get("premarket_rvol"), "liquidity": p.get("liquidity"), "reliability": p.get("reliability"),
            "catalyst": p.get("catalyst"), "regime": p.get("premarket_regime"), "confidence": p.get("confidence"),
            "reasons": p.get("reasons"), "features": p.get("features"),
        },
        "eligible_families": result.eligible_families,
        "lower_priority_families": result.lower_priority_families,
        "family_rules": result.family_rules,
        "family_notes": result.family_notes,
        "qualified_strategies": result.qualified_strategies,
        "rejected_strategies": result.rejected_strategies,
        "notes": result.notes,
        "versions": result.versions,
        "log_id": result.log_id,
    }


@router.get("/replay/{ticker}")
def replay_day(
    ticker: str,
    date: str = Query(..., description="trading day to replay (YYYY-MM-DD)"),
    timeframes: str = Query("15m,30m,65m,1D", description="comma-separated"),
    refresh: str = Query("weekly", pattern="^(weekly|daily)$",
                         description="how often qualification statistics were rebuilt, as in live use"),
):
    """Replay one morning end to end: the regimes known at 09:25, the strategies
    that qualified then, and what their trades that day actually did -- next to
    what every other strategy did. Uses only information available at 09:25."""
    import datetime as dt

    from app.strategy_engine.engine_backtest import EngineBacktester
    from app.strategy_engine.models import Timeframe

    try:
        day = dt.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"invalid date {date!r}; expected YYYY-MM-DD") from None
    try:
        tfs = [Timeframe.parse(t.strip()) for t in timeframes.split(",") if t.strip()]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    if not tfs:
        raise HTTPException(status_code=422, detail="no timeframes given")
    return EngineBacktester(refresh=refresh).replay_day(ticker, day, tfs)
