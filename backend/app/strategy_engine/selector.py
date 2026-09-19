"""
Final strategy selector (spec sections 36-41, 49).

    market regime -> ticker regime -> premarket regime -> timeframe
        -> strategy families -> historical qualification -> qualified strategies

Deterministic, no look-ahead (every layer only sees data available at the
decision timestamp), and it NEVER generates trade signals. It answers:
which strategies have historically shown an edge in conditions like now?

Every strategy in the registry ends with exactly one status, checked in
this order so the reason is always the first gate it failed:
    NOT_RUNNABLE          QIS cannot execute it (unmapped indicator / data)
    NOT_APPLICABLE        restricted to other tickers
    TIMEFRAME_MISMATCH    requested timeframe is not one it declares
    DATA_UNAVAILABLE      needs premarket / event data that isn't available
    FAMILY_NOT_APPLICABLE its family doesn't fit the current regimes
    NOT_EVALUATED         no historical evaluation for this ticker/timeframe
    NOT_QUALIFIED         failed a historical check (with the failing numbers)
    QUALIFIED             passed every check

"NO QUALIFIED STRATEGY" is a valid, expected outcome -- nothing is forced.
Every decision is written to selection_log with the data, configuration and
catalog versions needed to reproduce it.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field

import pandas as pd

from app.strategy_engine.data.calendar import NY, previous_trading_day, session_bounds
from app.strategy_engine.data.normalize import daily_upto, upto
from app.strategy_engine.data.store import BarStore, data_version
from app.strategy_engine.historical import EngineDB
from app.strategy_engine.market_regime import MarketRegimeDetector
from app.strategy_engine.models import AssetScope, StrategyMeta, Timeframe
from app.strategy_engine.premarket_regime import PremarketRegimeDetector
from app.strategy_engine.qualification import NOT_EVALUATED, QUALIFIED, StrategyQualificationEngine
from app.strategy_engine.registry import StrategyRegistry, default_registry
from app.strategy_engine.strategy_family import NOT_APPLICABLE as FAMILY_NA
from app.strategy_engine.strategy_family import StrategyFamilyEngine
from app.strategy_engine.thresholds import config_version
from app.strategy_engine.ticker_regime import TickerRegimeDetector
from app.strategy_engine.timeframe import TimeframeSelector

QUALIFIED_AVAILABLE = "QUALIFIED_STRATEGIES_AVAILABLE"
NO_QUALIFIED = "NO_QUALIFIED_STRATEGY"
DATA_INSUFFICIENT = "DATA_INSUFFICIENT"


@dataclass
class StrategyVerdict:
    strategy_id: int
    strategy: str
    slug: str
    family: str
    status: str
    reason: str
    family_status: str | None = None
    qualification: dict | None = None
    why: list[str] = field(default_factory=list)


@dataclass
class SelectionResult:
    ticker: str
    timeframe: str
    decision_ts: str
    status: str
    market_regime: dict = field(default_factory=dict)
    ticker_regime: dict = field(default_factory=dict)
    premarket_regime: dict = field(default_factory=dict)
    eligible_families: list[str] = field(default_factory=list)
    lower_priority_families: list[str] = field(default_factory=list)
    family_rules: list[dict] = field(default_factory=list)
    family_notes: list[str] = field(default_factory=list)
    qualified_strategies: list[dict] = field(default_factory=list)
    rejected_strategies: list[dict] = field(default_factory=list)
    versions: dict = field(default_factory=dict)
    log_id: int | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _as_ny(ts) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_localize(NY) if t.tzinfo is None else t.tz_convert(NY)


class StrategySelector:
    def __init__(self, store: BarStore | None = None, db: EngineDB | None = None,
                 registry: StrategyRegistry | None = None, earnings_provider=None, log: bool = True):
        self.store = store or BarStore()
        self.db = db or EngineDB()
        self.registry = registry or default_registry()
        self.earnings_provider = earnings_provider
        self.log = log
        self.tf = TimeframeSelector()
        self.families = StrategyFamilyEngine()
        self.qualifier = StrategyQualificationEngine(self.db)

    # -- inputs ------------------------------------------------------------------
    def _inputs(self, ticker: str, ts: pd.Timestamp) -> dict:
        s = self.store
        daily = {sym: s.load(sym, Timeframe.D1, source="twelvedata") for sym in ("SPY", "QQQ", "IWM")}
        vix = s.load("VIX", Timeframe.D1, source="tastytrade")
        t_daily = s.load(ticker, Timeframe.D1, source="twelvedata")
        t_5m = s.load(ticker, Timeframe.M5)                      # RTH: Twelve Data, extended: Tastytrade
        m_5m = {sym: s.load(sym, Timeframe.M5, source="tastytrade") for sym in ("SPY", "QQQ", "IWM")}
        return {"daily": daily, "vix": vix, "t_daily": t_daily, "t_5m": t_5m, "m_5m": m_5m}

    def _earnings(self, ticker: str, ts: pd.Timestamp):
        """Tastytrade only knows the CURRENT expected date, so it is used only
        for decisions about today; historical decisions get UNKNOWN."""
        if self.earnings_provider is None or ts.date() != dt.datetime.now(NY).date():
            return None
        try:
            return self.earnings_provider.earnings([ticker]).get(ticker.upper())
        except Exception:
            return None

    # -- main ----------------------------------------------------------------------
    def select(self, ticker: str, timeframe: str | Timeframe, decision_ts=None, include_premarket: bool = True) -> SelectionResult:
        ticker = ticker.upper()
        tf = timeframe if isinstance(timeframe, Timeframe) else self.tf.parse(timeframe)
        ts = _as_ny(decision_ts) if decision_ts is not None else pd.Timestamp.now(tz=NY).floor("min")
        res = SelectionResult(ticker=ticker, timeframe=str(tf), decision_ts=ts.isoformat(), status=DATA_INSUFFICIENT)
        inp = self._inputs(ticker, ts)

        market = MarketRegimeDetector().detect(inp["daily"], ts, vix=inp["vix"] if len(inp["vix"]) else None)
        res.market_regime = market.to_dict()
        ticker_r = TickerRegimeDetector().detect(ticker, inp["t_daily"], {k: inp["daily"][k] for k in ("SPY", "QQQ")}, ts,
                                                 intraday=inp["t_5m"], intraday_timeframe=Timeframe.M5,
                                                 earnings=self._earnings(ticker, ts))
        res.ticker_regime = ticker_r.to_dict()

        premarket = None
        if include_premarket:
            premarket = self._premarket(ticker, ts, inp)
            res.premarket_regime = premarket.to_dict()
            res.market_regime["market_premarket"] = premarket.market_premarket
            res.ticker_regime["premarket_regime"] = premarket.premarket_regime
        else:
            res.premarket_regime = {"status": "NOT_EVALUATED", "premarket_regime": "NOT_EVALUATED",
                                    "reasons": ["premarket evaluation disabled for this request"]}

        res.versions = {
            "configuration_version": config_version(), "catalog_version": self.registry.version,
            "data_version": data_version(*[daily_upto(inp["daily"][k], ts) for k in ("SPY", "QQQ", "IWM")],
                                         daily_upto(inp["t_daily"], ts), upto(inp["t_5m"], ts, 5)),
        }
        if market.status != "OK" or ticker_r.status != "OK":
            res.status = DATA_INSUFFICIENT
            res.notes = [f"market regime: {market.status} {market.reasons}" if market.status != "OK" else "",
                         f"ticker regime: {ticker_r.status} {ticker_r.reasons}" if ticker_r.status != "OK" else ""]
            res.notes = [n for n in res.notes if n]
            self._log(res)
            return res

        fam = self.families.decide(market, ticker_r, premarket)
        res.eligible_families, res.lower_priority_families = fam.eligible, fam.lower_priority
        res.family_rules, res.family_notes = fam.fired_rules, fam.notes

        pm_label = premarket.premarket_regime if premarket else "NOT_EVALUATED"
        self._as_of = ts
        verdicts = [self._judge(s, ticker, tf, fam, market, ticker_r, premarket, pm_label) for s in self.registry.all()]
        qualified = [v for v in verdicts if v.status == QUALIFIED]
        qualified.sort(key=self._strength, reverse=True)
        # Replays: statistics are rebuilt from trades closed before the decision
        # time; parameter stability can only be too if the run stored neighbour trades.
        evals = [(v.qualification or {}).get("evaluation") or {} for v in verdicts]
        pit = [e for e in evals if e.get("point_in_time")]
        if pit:
            res.notes.append(f"POINT_IN_TIME_REPLAY: qualification statistics for {len(pit)} strategies were rebuilt "
                             f"from trades closed before {ts}")
            stale = [e for e in pit if not e.get("parameter_stability_point_in_time")]
            if stale:
                res.notes.append(f"PARAMETER_STABILITY_NOT_POINT_IN_TIME: {len(stale)} evaluations predate stored "
                                 f"neighbour trades; their parameter stability uses the full window -- re-run them")
        res.qualified_strategies = [self._summary(v) for v in qualified]
        res.rejected_strategies = [asdict(v) for v in verdicts if v.status != QUALIFIED]
        res.status = QUALIFIED_AVAILABLE if qualified else NO_QUALIFIED
        self._log(res)
        return res

    def _premarket(self, ticker, ts, inp):
        prev = previous_trading_day(ts.date()) if session_bounds(ts.date()) else None

        def prev_close(df):
            if prev is None or df is None or df.empty:
                return None
            sub = df[df.index.tz_convert(NY).date == prev]
            return float(sub["close"].iloc[-1]) if len(sub) else None

        d = inp["t_daily"]
        prev_row = d[d.index.tz_convert(NY).date == prev] if prev else d.iloc[0:0]
        prev_day = {"high": float(prev_row["high"].iloc[-1]), "low": float(prev_row["low"].iloc[-1])} if len(prev_row) else None
        return PremarketRegimeDetector().detect(
            ticker, inp["t_5m"], Timeframe.M5, ts, previous_close=prev_close(d), previous_day=prev_day,
            earnings=self._earnings(ticker, ts), market=inp["m_5m"],
            market_previous_close={k: prev_close(inp["daily"][k]) for k in ("SPY", "QQQ", "IWM")})

    def _judge(self, s: StrategyMeta, ticker, tf, fam, market, ticker_r, premarket, pm_label) -> StrategyVerdict:
        v = StrategyVerdict(strategy_id=s.id, strategy=s.name, slug=s.slug, family=str(s.family), status="", reason="")
        if not s.runnable:
            v.status, v.reason = "NOT_RUNNABLE", f"QIS cannot run this strategy: {s.not_runnable_reason}"
            return v
        if s.asset_scope is AssetScope.SPECIFIC_TICKER and ticker not in s.allowed_tickers:
            v.status, v.reason = "NOT_APPLICABLE", f"Strategy restricted to {', '.join(s.allowed_tickers)}; current ticker: {ticker}"
            return v
        tfc = self.tf.check(s, tf)
        if not tfc.ok:
            v.status, v.reason = tfc.status, tfc.reason
            return v
        if s.requires_premarket_data and pm_label in ("PREMARKET_DATA_UNAVAILABLE", "NOT_EVALUATED"):
            v.status, v.reason = "DATA_UNAVAILABLE", f"Strategy requires premarket data; premarket status: {pm_label}"
            return v
        if s.requires_event_data and ticker_r.event_status == "UNKNOWN":
            v.status, v.reason = "DATA_UNAVAILABLE", "Strategy requires event (earnings) data; event status: UNKNOWN"
            return v
        fstat, freason = self.families.strategy_status(s, fam)
        v.family_status = fstat
        if fstat == FAMILY_NA:
            v.status, v.reason = "FAMILY_NOT_APPLICABLE", freason
            return v
        q = self.qualifier.qualify(ticker, s, tf, market.market_regime, ticker_r.ticker_regime,
                                   pm_label if s.uses_premarket else None, as_of=self._as_of)
        v.qualification = q.to_dict()
        v.status = q.qualification_status
        v.reason = "; ".join(q.reasons)
        if v.status == QUALIFIED:
            v.why = self._why(s, tf, market, ticker_r, premarket, freason, q)
        return v

    @staticmethod
    def _strength(v: StrategyVerdict) -> tuple:
        q = v.qualification or {}
        rm = q.get("regime_matched") or {}
        regime_pf = rm.get("profit_factor") if rm.get("status") == "MATCHED" else None
        oos = (q.get("out_of_sample") or {}).get("profit_factor") or 0
        return (regime_pf if regime_pf is not None else oos, oos)

    @staticmethod
    def _summary(v: StrategyVerdict) -> dict:
        q = v.qualification or {}
        rm = q.get("regime_matched") or {}
        pm = q.get("premarket_matched") or {}
        return {"strategy_id": v.strategy_id, "strategy": v.strategy, "family": v.family,
                "family_status": v.family_status,
                "trade_count": (q.get("historical") or {}).get("trade_count"),
                "profit_factor": (q.get("historical") or {}).get("profit_factor"),
                "oos_pf": (q.get("out_of_sample") or {}).get("profit_factor"),
                "regime_pf": rm.get("profit_factor") if rm.get("status") == "MATCHED" else None,
                "regime_match": rm.get("status"), "regime_level": rm.get("level"),
                "premarket_regime_pf": pm.get("profit_factor") if pm.get("status") == "MATCHED" else None,
                "walk_forward_pass_rate": (q.get("walk_forward") or {}).get("pass_rate"),
                "max_drawdown": (q.get("historical") or {}).get("max_drawdown"),
                "qualification": v.status, "why": v.why, "checks": q.get("checks")}

    @staticmethod
    def _why(s, tf, market, ticker_r, premarket, family_reason, q) -> list[str]:
        h, wf, rm = q.historical, q.walk_forward, q.regime_matched
        out = [f"Market: {market.direction} + {market.volatility} volatility ({market.market_regime})",
               f"Ticker: trend {ticker_r.trend}, momentum {ticker_r.momentum}, relative strength {ticker_r.relative_strength}, "
               f"volume {ticker_r.volume}, volatility {ticker_r.volatility}"]
        if premarket is not None and s.uses_premarket:
            out.append(f"Premarket: {premarket.premarket_regime} (reliability {premarket.reliability})")
        out += [f"Timeframe: {tf} supported", f"Family: {family_reason}",
                f"Historical: {h.get('trade_count')} trades, PF {h.get('profit_factor')}, OOS PF {q.out_of_sample.get('profit_factor')}, "
                f"walk-forward {wf.get('profitable_periods')}/{wf.get('walk_forward_periods')} periods profitable, "
                f"parameter stability {q.parameter_stability.get('score', 'n/a')}, slippage robustness {q.slippage.get('robustness')}"]
        if rm.get("status") == "MATCHED":
            out.append(f"Regime-matched ({rm['level']}): {rm['trade_count']} trades, PF {rm['profit_factor']}")
        else:
            out.append("Regime-matched: insufficient sample in today's regimes; all-time results used")
        out.append("Result: QUALIFIED")
        return out

    def _log(self, res: SelectionResult) -> None:
        if not self.log:
            return
        res.log_id = self.db.log_selection({
            "logged_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "decision_ts": res.decision_ts,
            "ticker": res.ticker, "timeframe": res.timeframe,
            "market_regime": res.market_regime.get("market_regime"), "ticker_regime": res.ticker_regime.get("ticker_regime"),
            "premarket_regime": res.premarket_regime.get("premarket_regime"),
            "premarket_data_through": res.premarket_regime.get("premarket_data_through"),
            "candidate_families": {"eligible": res.eligible_families, "lower_priority": res.lower_priority_families},
            "candidate_strategies": [r["strategy"] for r in res.rejected_strategies
                                     if r["status"] in ("NOT_QUALIFIED", "NOT_EVALUATED")] + [q["strategy"] for q in res.qualified_strategies],
            "qualification_results": {r["strategy"]: {"status": r["status"], "reason": r["reason"]} for r in res.rejected_strategies},
            "final_qualified_strategies": [q["strategy"] for q in res.qualified_strategies],
            "status": res.status, **res.versions,
        })
