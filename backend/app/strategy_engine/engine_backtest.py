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
    eligible_families: list[str] = field(default_factory=list)
    lower_priority_families: list[str] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)       # only filled by replay_day


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
                  progress=None, keep_rejected: int = 0) -> list[DayDecision]:
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
                d = DayDecision(str(day), str(tf), market.market_regime, tick.ticker_regime, pm.premarket_regime,
                                eligible_families=list(fam.eligible), lower_priority_families=list(fam.lower_priority))
                engine, plain, rejected_verdicts = [], [], []
                for s in self.registry.all():
                    v = self.selector._judge(s, ticker, tf, fam, market, tick, pm, pm.premarket_regime)
                    if v.status == QUALIFIED:
                        engine.append(v)
                    elif keep_rejected and v.status not in ("NOT_RUNNABLE", "NOT_APPLICABLE", "TIMEFRAME_MISMATCH"):
                        rejected_verdicts.append(v)
                    # NO_REGIME: same gates and point-in-time stats, no family gate, no regime matching
                    if v.status in (QUALIFIED, "NOT_QUALIFIED", "FAMILY_NOT_APPLICABLE"):
                        q = self.selector.qualifier.qualify(ticker, s, tf, None, None, None, as_of=stats_ts)
                        if q.qualification_status == QUALIFIED:
                            plain.append(s.id)
                engine.sort(key=StrategySelector._strength, reverse=True)
                engine, dropped = self.selector._drop_duplicates(engine, ticker, tf)
                d.engine = [v.strategy_id for v in engine]
                if keep_rejected:
                    rej = [{"strategy": v.strategy, "status": v.status, "reason": v.reason} for v in rejected_verdicts]
                    rej += [{"strategy": v.strategy, "status": "DUPLICATE",
                             "reason": f"trades almost the same signals as {of}"} for v, of in dropped]
                    order = {"NOT_QUALIFIED": 0, "DUPLICATE": 1, "FAMILY_NOT_APPLICABLE": 2, "NOT_EVALUATED": 3}
                    d.rejected = sorted(rej, key=lambda r: order.get(r["status"], 9))[:keep_rejected]
                d.no_regime = plain
                out.append(d)
            if progress and (i % 50 == 0 or i == len(days) - 1):
                progress(f"{ticker}: {i + 1}/{len(days)} days")
        return out

    def replay_day(self, ticker: str, day: dt.date, timeframes: list[Timeframe], keep_rejected: int = 40) -> dict:
        """One morning, start to finish: the regimes known at 09:25, the
        strategies that qualified then, and what their trades that day did --
        plus what every other strategy did, as the comparison."""
        ticker = ticker.upper()
        decisions = self.decisions(ticker, timeframes, day, day, keep_rejected=keep_rejected)
        names = {s.id: s for s in self.registry.all()}
        cutoff = pd.Timestamp(f"{day} {self.decision_time}", tz=NY).timestamp()
        out = {"ticker": ticker, "date": str(day), "decision_time": self.decision_time, "refresh": self.refresh,
               "timeframes": []}
        if not decisions:
            out["status"] = "DATA_INSUFFICIENT"
            out["note"] = (f"no market/ticker regime was known at {day} {self.decision_time} -- "
                           f"the engine would have stood aside")
            return out
        d0 = decisions[0]
        out.update({"status": "OK", "market_regime": d0.market_regime, "ticker_regime": d0.ticker_regime,
                    "premarket_regime": d0.premarket_regime, "eligible_families": d0.eligible_families,
                    "lower_priority_families": d0.lower_priority_families})
        picked_rows, all_rows = [], []
        for d in decisions:
            runnable = [s for s in self.registry.all()
                        if s.runnable and any(str(x) == d.timeframe for x in s.timeframes)
                        and (not s.allowed_tickers or ticker in s.allowed_tickers)]
            tf_trades = []
            for s in runnable:
                t = self.trades_on(ticker, s.id, d.timeframe)
                if not len(t):
                    continue
                t = t[(t["entry_day"] == str(day)) & (t["entry_time"] >= cutoff)]
                for r in t.itertuples():
                    tf_trades.append({
                        "strategy_id": s.id, "strategy": s.name, "family": str(s.family), "timeframe": d.timeframe,
                        "picked": s.id in d.engine, "rank": d.engine.index(s.id) + 1 if s.id in d.engine else None,
                        "direction": r.direction, "entry": _ny(r.entry_time), "exit": _ny(r.exit_time),
                        "entry_price": round(float(r.entry_price), 4), "exit_price": round(float(r.exit_price), 4),
                        "return_pct": round(float(r.ret) * 100, 3),
                        "hold_hours": round((r.exit_time - r.entry_time) / 3600, 2),
                        "closed_same_day": _ny(r.exit_time)[:10] == str(day)})
            picked_rows += [r for r in tf_trades if r["picked"]]
            all_rows += tf_trades
            out["timeframes"].append({
                "timeframe": d.timeframe,
                "picked": [{"strategy_id": i, "strategy": names[i].name, "family": str(names[i].family), "rank": n + 1,
                            "traded": any(r["picked"] and r["strategy_id"] == i for r in tf_trades)}
                           for n, i in enumerate(d.engine)],
                "rejected": d.rejected,
                "trades": sorted(tf_trades, key=lambda r: (not r["picked"], r["entry"]))})
        out["summary"] = {"engine": _pnl(picked_rows), "all_strategies": _pnl(all_rows),
                          "strategies_on_watchlist": sum(len(t["picked"]) for t in out["timeframes"])}
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


def _ny(ts) -> str:
    return pd.Timestamp(int(ts), unit="s", tz="UTC").tz_convert(NY).strftime("%Y-%m-%d %H:%M")


def _pnl(rows: list[dict]) -> dict:
    if not rows:
        return {"trades": 0, "total_return_pct": 0.0, "mean_return_pct": None, "winners": 0, "losers": 0,
                "best": None, "worst": None, "capital_days": 0.0, "return_per_capital_day_pct": None}
    rets = [r["return_pct"] for r in rows]
    hold = sum(max(r["hold_hours"], 1) / 24 for r in rows)
    best, worst = max(rows, key=lambda r: r["return_pct"]), min(rows, key=lambda r: r["return_pct"])
    return {"trades": len(rows), "total_return_pct": round(sum(rets), 3),
            "mean_return_pct": round(sum(rets) / len(rets), 3),
            "winners": sum(1 for r in rets if r > 0), "losers": sum(1 for r in rets if r <= 0),
            "best": {"strategy": best["strategy"], "return_pct": best["return_pct"]},
            "worst": {"strategy": worst["strategy"], "return_pct": worst["return_pct"]},
            "capital_days": round(hold, 2),
            "return_per_capital_day_pct": round(sum(rets) / hold, 3) if hold else None}


def buy_and_hold(store, ticker: str, start: dt.date, end: dt.date) -> float | None:
    d = store.load(ticker, Timeframe.D1, source="twelvedata")
    if d.empty:
        return None
    days = d.index.tz_convert(NY).date
    sel = d[(days >= start) & (days <= end)]
    return round(float(sel["close"].iloc[-1] / sel["open"].iloc[0] - 1), 4) if len(sel) else None
