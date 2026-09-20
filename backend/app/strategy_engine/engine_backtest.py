"""
Backtest of the selection engine itself (not of individual strategies).

Every trading day D, at the decision time (09:25 New York, before the open):
  1. the regimes known at that moment are read from the persisted histories
     (market / ticker regime as of the previous close, premarket as of 09:25);
  2. every strategy goes through the selector's own gates (runnable, ticker,
     timeframe, data, family) and the point-in-time qualifier -- statistics
     rebuilt from trades that had CLOSED before D 09:25;
  3. the strategies that qualified are "traded" on D: their trades entered on
     D (at or after the decision time) are taken from the stored backtest.

The trades come from each strategy's continuous backtest, so a trade taken on
D is exactly the one the strategy would have entered that day. Positions are
sized equally per trade and costed at 1x slippage; overlap between
concurrently open trades is not modelled (each trade is one unit of risk).

Policies compared on the same days:
  ENGINE            all strategies the full engine qualifies that morning
  ENGINE_TOP1       only the top-ranked qualified strategy
  NO_REGIME         point-in-time qualification only (no family gate, no
                    regime-matched check) -- isolates what regimes add
  ALL_STRATEGIES    every runnable strategy on the timeframe, no selection
  BUY_AND_HOLD      the ticker itself over the period (reference)
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from types import SimpleNamespace

import numpy as np
import pandas as pd

from app.strategy_engine.data.calendar import NY, trading_days
from app.strategy_engine.evaluation import costed_returns, metrics
from app.strategy_engine.historical import EngineDB
from app.strategy_engine.models import Timeframe
from app.strategy_engine.qualification import QUALIFIED, StrategyQualificationEngine
from app.strategy_engine.registry import default_registry
from app.strategy_engine.selector import StrategySelector
from app.strategy_engine.strategy_family import StrategyFamilyEngine
from app.strategy_engine.thresholds import EXECUTION_COST_CONFIG

POLICIES = ("ENGINE", "ENGINE_TOP1", "NO_REGIME", "ALL_STRATEGIES")
NO_PREMARKET = "PREMARKET_DATA_UNAVAILABLE"


class CachedDB:
    """Read-through, in-memory view of EngineDB for the few read calls the
    qualifier makes -- the same rows, loaded once instead of once per day."""

    def __init__(self, db: EngineDB):
        self.db, self._c = db, {}

    def _get(self, key, fn):
        if key not in self._c:
            self._c[key] = fn()
        return self._c[key]

    def load_performance(self, ticker, sid, tf):
        return self._get(("perf", ticker.upper(), sid, tf), lambda: self.db.load_performance(ticker, sid, tf))

    def latest_run(self, ticker, sid, tf):
        return self._get(("run", ticker.upper(), sid, tf), lambda: self.db.latest_run(ticker, sid, tf))

    def load_trades(self, ticker, sid, tf, variant="base"):
        full = self._get(("trades", ticker.upper(), sid, tf), lambda: self.db.load_trades(ticker, sid, tf, variant=None))
        return full if variant is None else full[full["variant"] == variant]


def _last_known(hist: pd.DataFrame, ts_s: int) -> dict | None:
    if hist is None or hist.empty:
        return None
    pos = int(np.searchsorted(hist["known_at"].to_numpy(), ts_s, side="right")) - 1
    return hist.iloc[pos].to_dict() if pos >= 0 else None


@dataclass
class DayDecision:
    date: str
    timeframe: str
    market_regime: str | None
    ticker_regime: str | None
    premarket_regime: str
    engine: list[int] = field(default_factory=list)          # qualified strategy ids, ranked
    no_regime: list[int] = field(default_factory=list)


class EngineBacktester:
    def __init__(self, db: EngineDB | None = None, decision_time: str = "09:25", refresh: str = "weekly"):
        """refresh: how often qualification statistics are rebuilt -- "weekly"
        (as of each week's first trading morning, matching a weekly
        re-evaluation in live use) or "daily". Regimes are always daily."""
        if refresh not in ("weekly", "daily"):
            raise ValueError("refresh must be 'weekly' or 'daily'")
        self.refresh = refresh
        self.raw_db = db or EngineDB()
        self.db = CachedDB(self.raw_db)
        self.registry = default_registry()
        self.decision_time = decision_time
        self.cost = EXECUTION_COST_CONFIG["rth_slippage"]
        # the selector's own gate logic, with a qualifier reading the cached DB
        self.selector = StrategySelector(db=self.raw_db, log=False)
        self.selector.qualifier = StrategyQualificationEngine(self.db, pit_cache={})
        self.families = StrategyFamilyEngine()

    # -- regimes as known at the decision time ----------------------------------------
    def _regimes(self, day: dt.date, market_h, ticker_h, pm_h):
        ts = pd.Timestamp(f"{day} {self.decision_time}", tz=NY)
        s = int(ts.timestamp())
        m, t = _last_known(market_h, s), _last_known(ticker_h, s)
        pm_row = pm_h[(pm_h["date"] == str(day)) & (pm_h["known_at"] <= s)] if pm_h is not None and len(pm_h) else None
        pm = pm_row.iloc[0].to_dict() if pm_row is not None and len(pm_row) else None
        market = SimpleNamespace(direction=m and m["market_direction"], volatility=m and m["market_volatility"],
                                 market_regime=m and m["market_regime"])
        ticker = SimpleNamespace(trend=t and t["trend"], momentum=t and t["momentum"],
                                 relative_strength=t and t["relative_strength"], volatility=t and t["volatility"],
                                 volume=t and t["volume"], ticker_regime=t and t["ticker_regime"], event_status="UNKNOWN")
        premarket = SimpleNamespace(premarket_regime=pm["premarket_regime"] if pm else NO_PREMARKET,
                                    structure=pm["premarket_structure"] if pm else None,
                                    reliability=pm["premarket_reliability"] if pm else None)
        return ts, market, ticker, premarket

    # -- one ticker ---------------------------------------------------------------------
    def decisions(self, ticker: str, timeframes: list[Timeframe], start: dt.date, end: dt.date,
                  progress=None) -> list[DayDecision]:
        ticker = ticker.upper()
        market_h = self.raw_db.load_market_history()
        ticker_h = self.raw_db.load_ticker_history(ticker)
        pm_h = self.raw_db.load_premarket_history(ticker)
        out = []
        days = trading_days(start, end)
        week_start: dict[tuple, dt.date] = {}
        for day in days:
            week_start.setdefault(day.isocalendar()[:2], day)
        for i, day in enumerate(days):
            ts, market, tick, pm = self._regimes(day, market_h, ticker_h, pm_h)
            if market.market_regime is None or tick.ticker_regime is None:
                continue                                     # the live selector would say DATA_INSUFFICIENT
            fam = self.families.decide(market, tick, pm)
            stats_day = day if self.refresh == "daily" else week_start[day.isocalendar()[:2]]
            stats_ts = pd.Timestamp(f"{stats_day} {self.decision_time}", tz=NY)
            self.selector._as_of = stats_ts
            for tf in timeframes:
                d = DayDecision(str(day), str(tf), market.market_regime, tick.ticker_regime, pm.premarket_regime)
                engine, plain = [], []
                for s in self.registry.all():
                    v = self.selector._judge(s, ticker, tf, fam, market, tick, pm, pm.premarket_regime)
                    if v.status == QUALIFIED:
                        engine.append(v)
                    # NO_REGIME: same gates and point-in-time stats, no family gate, no regime matching
                    if v.status in (QUALIFIED, "NOT_QUALIFIED", "FAMILY_NOT_APPLICABLE"):
                        q = self.selector.qualifier.qualify(ticker, s, tf, None, None, None, as_of=stats_ts)
                        if q.qualification_status == QUALIFIED:
                            plain.append(s.id)
                engine.sort(key=StrategySelector._strength, reverse=True)
                engine, _ = self.selector._drop_duplicates(engine, ticker, tf)
                d.engine = [v.strategy_id for v in engine]
                d.no_regime = plain
                out.append(d)
            if progress and (i % 50 == 0 or i == len(days) - 1):
                progress(f"{ticker}: {i + 1}/{len(days)} days")
        return out

    def trades_on(self, ticker: str, sid: int, tf: str) -> pd.DataFrame:
        t = self.db.load_trades(ticker, sid, tf).copy()
        if len(t):
            t["entry_day"] = pd.to_datetime(t["entry_time"], unit="s", utc=True).dt.tz_convert(NY).dt.date.astype(str)
            t["ret"] = costed_returns(t, self.cost)
        return t

    def simulate(self, ticker: str, decisions: list[DayDecision], start: dt.date, end: dt.date) -> dict:
        """Collect each policy's trades from the day-by-day decisions."""
        ticker = ticker.upper()
        by_tf: dict[str, list[DayDecision]] = {}
        for d in decisions:
            by_tf.setdefault(d.timeframe, []).append(d)
        result = {}
        for tf, days in by_tf.items():
            decided = {d.date: d for d in days}
            runnable = [s for s in self.registry.all() if s.runnable and any(str(x) == tf for x in s.timeframes)
                        and (not s.allowed_tickers or ticker in s.allowed_tickers)]
            cache = {s.id: self.trades_on(ticker, s.id, tf) for s in runnable}
            picks = {p: [] for p in POLICIES}
            for sid, t in cache.items():
                if not len(t):
                    continue
                t = t[(t["entry_day"] >= str(start)) & (t["entry_day"] <= str(end))]
                for row in t.itertuples():
                    d = decided.get(row.entry_day)
                    if d is None:
                        continue
                    ts = pd.Timestamp(f"{row.entry_day} {self.decision_time}", tz=NY).timestamp()
                    if row.entry_time < ts:
                        continue                                  # entered before the decision was made
                    rec = (row.exit_time, row.entry_time, sid, row.ret)
                    picks["ALL_STRATEGIES"].append(rec)
                    if sid in d.engine:
                        picks["ENGINE"].append(rec)
                    if d.engine and sid == d.engine[0]:
                        picks["ENGINE_TOP1"].append(rec)
                    if sid in d.no_regime:
                        picks["NO_REGIME"].append(rec)
            summary = {}
            for p, recs in picks.items():
                recs.sort()
                r = np.array([x[3] for x in recs])
                m = metrics(r, span_years=max((end - start).days / 365.25, 1 / 12))
                cum = np.cumsum(r) if len(r) else np.array([0.0])
                dd = float((np.maximum.accumulate(np.concatenate([[0.0], cum]))[1:] - cum).max()) if len(r) else 0.0
                summary[p] = {**{k: m[k] for k in ("trade_count", "win_rate", "profit_factor", "expectancy", "sharpe")},
                              "sum_return": round(float(r.sum()), 4) if len(r) else 0.0,
                              "max_drawdown_sum": round(dd, 4),
                              "strategies_used": len({x[2] for x in recs})}
            days_selected = sum(1 for d in days if d.engine)
            summary["days"] = {"decisions": len(days), "with_engine_pick": days_selected,
                               "distinct_engine_sets": len({tuple(d.engine) for d in days if d.engine})}
            result[tf] = summary
        return result


def buy_and_hold(store, ticker: str, start: dt.date, end: dt.date) -> float | None:
    d = store.load(ticker, Timeframe.D1, source="twelvedata")
    if d.empty:
        return None
    days = d.index.tz_convert(NY).date
    sel = d[(days >= start) & (days <= end)]
    return round(float(sel["close"].iloc[-1] / sel["open"].iloc[0] - 1), 4) if len(sel) else None
