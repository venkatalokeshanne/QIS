"""
Batch jobs that populate the historical database:

  ensure_bars          download/refresh bars into the local store
  build_market_history market_regime_history from SPY/QQQ/IWM (+ VIX)
  build_ticker_history ticker_regime_history for one ticker
  build_premarket_history  premarket_regime_history at a fixed decision time
  evaluate_ticker      strategy evaluations for every applicable strategy

Order matters: regime histories must exist before evaluations, because
evaluations tag every trade with the regimes known before its entry.
"""

from __future__ import annotations

import datetime as dt
import logging

import pandas as pd

from app.strategy_engine.data.calendar import NY, previous_trading_day, session_bounds
from app.strategy_engine.data.providers import ProviderError, TastytradeProvider, TwelveDataProvider
from app.strategy_engine.data.store import BarStore
from app.strategy_engine.evaluation import RESAMPLED_FROM_5M, StrategyEvaluator
from app.strategy_engine.historical import EngineDB
from app.strategy_engine.market_regime import MarketRegimeDetector
from app.strategy_engine.models import AssetScope, Timeframe
from app.strategy_engine.premarket_regime import PremarketRegimeDetector
from app.strategy_engine.registry import default_registry
from app.strategy_engine.thresholds import config_version
from app.strategy_engine.ticker_regime import TickerRegimeDetector

log = logging.getLogger(__name__)


def ensure_bars(tickers: list[str], timeframes: list[Timeframe], start: dt.date, end: dt.date,
                store: BarStore | None = None, extended_days: int = 95) -> dict:
    """Regular-session history from Twelve Data; extended-hours 5m bars
    (premarket) from Tastytrade for the recent window it serves."""
    store = store or BarStore()
    td, tt = TwelveDataProvider(max_requests=40), TastytradeProvider()
    report = {}
    for t in tickers:
        for tf in sorted(set(timeframes) | {Timeframe.D1}, key=lambda x: x.minutes):
            fetch_tf = Timeframe.M5 if tf in RESAMPLED_FROM_5M else tf
            s = start if fetch_tf.is_intraday else dt.date(2016, 1, 1)
            try:
                df = td.fetch(t, fetch_tf, s, end)
                report[(t, str(fetch_tf), "twelvedata")] = store.upsert(t, fetch_tf, "twelvedata", df, note="ensure_bars")
            except Exception as exc:
                report[(t, str(fetch_tf), "twelvedata")] = f"ERROR {type(exc).__name__}: {exc}"
        try:
            ext = tt.fetch(t, Timeframe.M5, end - dt.timedelta(days=extended_days), end, extended_hours=True)
            report[(t, "5m", "tastytrade")] = store.upsert(t, Timeframe.M5, "tastytrade", ext, note="ensure_bars")
        except (ProviderError, Exception) as exc:
            report[(t, "5m", "tastytrade")] = f"ERROR {type(exc).__name__}: {exc}"
    return report


def build_market_history(store: BarStore | None = None, db: EngineDB | None = None) -> int:
    store, db = store or BarStore(), db or EngineDB()
    daily = {s: store.load(s, Timeframe.D1, source="twelvedata") for s in ("SPY", "QQQ", "IWM")}
    vix = store.load("VIX", Timeframe.D1, source="tastytrade")
    hist = MarketRegimeDetector().classify_history(daily, vix=vix if len(vix) else None)
    return db.write_market_history(hist, config_version())


def build_ticker_history(ticker: str, store: BarStore | None = None, db: EngineDB | None = None) -> int:
    store, db = store or BarStore(), db or EngineDB()
    daily = store.load(ticker, Timeframe.D1, source="twelvedata")
    bench = {b: store.load(b, Timeframe.D1, source="twelvedata") for b in ("SPY", "QQQ")}
    hist = TickerRegimeDetector().classify_history(ticker, daily, bench)
    return db.write_ticker_history(hist, config_version())


def build_premarket_history(ticker: str, decision_time: str = "09:25", store: BarStore | None = None,
                            db: EngineDB | None = None) -> int:
    """One premarket regime per day that has premarket bars, as known at
    `decision_time` (so it can tag trades entering at/after 09:30)."""
    store, db = store or BarStore(), db or EngineDB()
    bars = store.load(ticker, Timeframe.M5, source="tastytrade")
    daily = store.load(ticker, Timeframe.D1, source="twelvedata")
    if bars.empty or daily.empty:
        return 0
    closes = {ts.tz_convert(NY).date(): (float(c), float(h), float(l))
              for ts, c, h, l in zip(daily.index, daily["close"], daily["high"], daily["low"])}
    det = PremarketRegimeDetector()
    days = sorted({d for d in bars[bars["session"] == "PREMARKET"].index.tz_convert(NY).date})
    rows = []
    for d in days:
        prev = previous_trading_day(d)
        if prev not in closes or session_bounds(d) is None:
            continue
        c, h, l = closes[prev]
        ts = pd.Timestamp(f"{d} {decision_time}", tz=NY)
        r = det.detect(ticker, bars, Timeframe.M5, ts, previous_close=c, previous_day={"high": h, "low": l})
        f = r.features
        rows.append({"ticker": ticker.upper(), "date": str(d), "decision_time": decision_time,
                     "known_at": int(ts.timestamp()), "premarket_data_through": r.premarket_data_through,
                     "premarket_status": r.status, "premarket_change_pct": f.get("premarket_change_pct"),
                     "premarket_range_pct": f.get("premarket_range_pct"), "premarket_structure": r.structure,
                     "premarket_volume": f.get("premarket_volume"), "premarket_rvol": r.premarket_rvol,
                     "premarket_liquidity": r.liquidity, "premarket_reliability": r.reliability,
                     "premarket_catalyst": r.catalyst, "premarket_regime": r.premarket_regime})
    return db.write_premarket_rows(rows, config_version())


def applicable_strategies(ticker: str, timeframes: list[Timeframe] | None = None):
    for s in default_registry().all():
        if not s.runnable:
            continue
        if s.asset_scope is AssetScope.SPECIFIC_TICKER and ticker.upper() not in s.allowed_tickers:
            continue
        for tf in s.timeframes:
            if timeframes is None or tf in timeframes:
                yield s, tf


def evaluate_ticker(ticker: str, timeframes: list[Timeframe] | None = None, evaluator: StrategyEvaluator | None = None,
                    only: list[str] | None = None, progress=print) -> list[dict]:
    ev = evaluator or StrategyEvaluator()
    out = []
    for s, tf in applicable_strategies(ticker, timeframes):
        if only and s.slug not in only:
            continue
        try:
            r = ev.evaluate(ticker, s, tf)
            out.append({"strategy": s.name, "timeframe": str(tf), "status": "OK", **r["all_time"], "robustness": r["robustness"]})
            progress(f"  {ticker} {tf:>4} {s.name[:45]:45} trades={r['all_time']['trade_count']:4} "
                     f"PF={r['all_time']['profit_factor']} robust={r['robustness']}")
        except Exception as exc:
            out.append({"strategy": s.name, "timeframe": str(tf), "status": f"ERROR {type(exc).__name__}: {exc}"[:200]})
            progress(f"  {ticker} {tf:>4} {s.name[:45]:45} ERROR {type(exc).__name__}: {str(exc)[:80]}")
    return out
