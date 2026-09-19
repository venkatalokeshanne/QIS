"""
Historical qualification (spec sections 28-35, 34 regime matching).

A strategy never qualifies on net return alone. It must pass every
configured check (QUALIFICATION_CONFIG) on its evaluated history:

  trade count, profit factor, out-of-sample profit factor, Sharpe,
  max drawdown, walk-forward pass rate, parameter stability, slippage
  robustness -- and, when there is enough history in regimes like TODAY's,
  the regime-matched profit factor too.

Regime matching looks up the performance rows for today's market + ticker
regime (falling back to market-only / ticker-only when the combined sample
is too small) and today's premarket regime. An insufficient sample is
reported as INSUFFICIENT_SAMPLE and falls back to all-time results -- it is
never silently treated as a pass or a fail.

Every check records value, threshold and outcome so a rejection can be
explained ("OOS PF 0.96, required >= 1.10").
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

import pandas as pd

from app.strategy_engine.evaluation import point_in_time_performance, utc
from app.strategy_engine.historical import ANY, EngineDB
from app.strategy_engine.models import StrategyMeta, Timeframe
from app.strategy_engine.thresholds import QUALIFICATION_CONFIG, config_version

QUALIFIED = "QUALIFIED"
NOT_QUALIFIED = "NOT_QUALIFIED"
NOT_EVALUATED = "NOT_EVALUATED"
INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"
PREMARKET_UNUSABLE = {"PREMARKET_UNRELIABLE", "PREMARKET_DATA_UNAVAILABLE", "NOT_EVALUATED", None}


@dataclass
class Check:
    name: str
    value: object
    threshold: str
    passed: bool | None          # None = not applicable (does not block)
    note: str = ""


@dataclass
class QualificationResult:
    ticker: str
    timeframe: str
    strategy_id: int
    strategy: str
    family: str
    qualification_status: str
    checks: list[Check] = field(default_factory=list)
    historical: dict = field(default_factory=dict)
    out_of_sample: dict = field(default_factory=dict)
    walk_forward: dict = field(default_factory=dict)
    parameter_stability: dict = field(default_factory=dict)
    slippage: dict = field(default_factory=dict)
    regime_matched: dict = field(default_factory=dict)
    premarket_matched: dict = field(default_factory=dict)
    evaluation: dict = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)

    @property
    def failed_checks(self) -> list[Check]:
        return [c for c in self.checks if c.passed is False]

    def to_dict(self) -> dict:
        return asdict(self)


def _row(perf: pd.DataFrame, scope: str, m=ANY, t=ANY, p=ANY) -> dict | None:
    sel = perf[(perf.scope == scope) & (perf.market_regime == m) & (perf.ticker_regime == t) & (perf.premarket_regime == p)]
    if sel.empty:
        return None
    r = sel.iloc[0].to_dict()
    r["details"] = json.loads(r.get("details") or "{}")
    return r


def _num(v):
    try:
        f = float(v)
        return None if f != f else f
    except (TypeError, ValueError):
        return None


class StrategyQualificationEngine:
    def __init__(self, db: EngineDB | None = None, config: dict | None = None):
        self.db = db or EngineDB()
        self.cfg = {**QUALIFICATION_CONFIG, **(config or {})}

    def qualify(self, ticker: str, strategy: StrategyMeta, timeframe: Timeframe, market_regime: str | None,
                ticker_regime: str | None, premarket_regime: str | None = None,
                as_of: pd.Timestamp | None = None) -> QualificationResult:
        """`as_of` = the decision time. When it precedes the end of the stored
        evaluation, every statistic is rebuilt from the trades that had CLOSED
        by then (point-in-time), so a replay never sees later trades."""
        cfg = self.cfg
        res = QualificationResult(ticker=ticker.upper(), timeframe=str(timeframe), strategy_id=strategy.id,
                                  strategy=strategy.name, family=str(strategy.family), qualification_status=NOT_EVALUATED)
        perf = self.db.load_performance(ticker, strategy.id, str(timeframe))
        base = _row(perf, "ALL_TIME") if not perf.empty else None
        if base is None:
            res.reasons = [f"no historical evaluation of {strategy.name} on {ticker.upper()} {timeframe} -- "
                           f"run the evaluation before it can qualify"]
            return res
        d = base["details"]
        run = self.db.latest_run(ticker, strategy.id, str(timeframe)) or {}
        pit = None
        if as_of is not None and d.get("bars_to") and utc(as_of) < utc(d["bars_to"]):
            perf, pit = point_in_time_performance(self.db, ticker, strategy, str(timeframe), pd.Timestamp(as_of), d, cfg)
            base = _row(perf, "ALL_TIME") if not perf.empty else None
            if base is None:
                res.reasons = [f"no history before {pd.Timestamp(as_of)} -- the evaluation window starts at {d.get('bars_from')}"]
                return res
            d = base["details"]
        res.evaluation = {"run_id": base.get("run_id"), "evaluated_at": base.get("last_updated"),
                          "bars_from": d.get("bars_from"), "bars_to": d.get("bars_to"), "span_years": d.get("span_years"),
                          "data_version": run.get("data_version"), "evaluation_config_version": run.get("config_version"),
                          "current_config_version": config_version(),
                          "point_in_time": pit is not None, **({"as_of": str(pd.Timestamp(as_of)), **pit} if pit else {})}
        res.historical = {k: base.get(k) for k in ("trade_count", "win_rate", "profit_factor", "expectancy", "sharpe", "max_drawdown")}
        res.out_of_sample = d.get("out_of_sample", {})
        res.walk_forward = {k: v for k, v in (d.get("walk_forward") or {}).items()}
        res.parameter_stability = d.get("parameter_stability", {})
        res.slippage = {"robustness": base.get("slippage_robustness"), **(d.get("slippage") or {})}

        checks = res.checks
        tc = int(base.get("trade_count") or 0)
        checks.append(Check("min_trades", tc, f">= {cfg['min_trades']}", tc >= cfg["min_trades"]))
        pf = _num(base.get("profit_factor"))
        checks.append(Check("profit_factor", pf, f">= {cfg['min_profit_factor']}", pf is not None and pf >= cfg["min_profit_factor"]))
        oos_pf = _num(base.get("oos_profit_factor"))
        checks.append(Check("out_of_sample_profit_factor", oos_pf, f">= {cfg['min_oos_profit_factor']}",
                            oos_pf is not None and oos_pf >= cfg["min_oos_profit_factor"],
                            "" if oos_pf is not None else "no out-of-sample trades"))
        sh = _num(base.get("sharpe"))
        checks.append(Check("sharpe", sh, f">= {cfg['min_sharpe']}", sh is not None and sh >= cfg["min_sharpe"]))
        dd = _num(base.get("max_drawdown"))
        checks.append(Check("max_drawdown", dd, f"<= {cfg['max_drawdown']}", dd is not None and dd <= cfg["max_drawdown"]))
        wf = _num(base.get("walk_forward_pass_rate"))
        wfd = res.walk_forward
        if cfg["require_walk_forward"]:
            checks.append(Check("walk_forward_pass_rate", wf, f">= {cfg['min_walk_forward_pass_rate']}",
                                wf is not None and wf >= cfg["min_walk_forward_pass_rate"],
                                f"{wfd.get('profitable_periods')}/{wfd.get('walk_forward_periods')} periods profitable"))
        ps = res.parameter_stability or {}
        if cfg["require_parameter_stability"]:
            if ps.get("status") == "NOT_APPLICABLE":
                checks.append(Check("parameter_stability", None, f">= {cfg['min_parameter_stability']}", None,
                                    ps.get("reason", "no tunable parameters")))
            else:
                score = _num(ps.get("score"))
                checks.append(Check("parameter_stability", score, f">= {cfg['min_parameter_stability']}",
                                    score is not None and score >= cfg["min_parameter_stability"],
                                    f"{ps.get('stable_neighbours')}/{ps.get('neighbours')} neighbouring parameter sets stay profitable"))
        rob = base.get("slippage_robustness")
        pf2 = (res.slippage.get("2x") or {}).get("profit_factor")
        checks.append(Check("slippage_robustness", rob, "not LOW", rob in ("HIGH", "MEDIUM"),
                            f"PF at 0x/1x/2x/3x slippage: " + "/".join(str((res.slippage.get(k) or {}).get("profit_factor"))
                                                                      for k in ("0x", "1x", "2x", "3x"))))

        # --- regime matching ---------------------------------------------------
        res.regime_matched = self._regime_match(perf, market_regime, ticker_regime)
        rm = res.regime_matched
        if rm["status"] == "MATCHED":
            checks.append(Check("regime_matched_profit_factor", rm["profit_factor"], f">= {cfg['min_profit_factor']}",
                                rm["profit_factor"] is not None and rm["profit_factor"] >= cfg["min_profit_factor"],
                                f"{rm['trade_count']} trades in {rm['level']} regime {rm['label']}"))
        else:
            checks.append(Check("regime_matched_profit_factor", None, f">= {cfg['min_profit_factor']}", None,
                                f"{INSUFFICIENT_SAMPLE}: fewer than {cfg['min_regime_matched_trades']} trades in today's regimes; "
                                f"all-time results used"))
        if strategy.uses_premarket:
            res.premarket_matched = self._premarket_match(perf, premarket_regime)
            pm = res.premarket_matched
            if pm["status"] == "MATCHED":
                checks.append(Check("premarket_matched_profit_factor", pm["profit_factor"], f">= {cfg['min_profit_factor']}",
                                    pm["profit_factor"] is not None and pm["profit_factor"] >= cfg["min_profit_factor"],
                                    f"{pm['trade_count']} trades in premarket regime {pm['premarket_regime']}"))
        else:
            res.premarket_matched = {"status": "NOT_APPLICABLE", "reason": "strategy does not use premarket context"}

        failed = res.failed_checks
        res.qualification_status = QUALIFIED if not failed else NOT_QUALIFIED
        res.reasons = ([f"{c.name}: {c.value} (required {c.threshold})" + (f" -- {c.note}" if c.note else "") for c in failed]
                       or ["all qualification checks passed"])
        if pit is not None and not pit["parameter_stability_point_in_time"]:
            res.reasons.append("note: parameter stability comes from the full evaluation window (neighbour trades were "
                               "not stored by that run); re-run the evaluation to make it point-in-time too")
        if res.evaluation.get("evaluation_config_version") not in (None, res.evaluation["current_config_version"]):
            res.reasons.append("note: evaluated under a different configuration version; re-run the evaluation to refresh")
        return res

    def _regime_match(self, perf: pd.DataFrame, market: str | None, ticker: str | None) -> dict:
        need = self.cfg["min_regime_matched_trades"]
        tried = []
        for level, scope, m, t in (("MARKET+TICKER", "MARKET_TICKER", market, ticker), ("MARKET", "MARKET", market, ANY),
                                   ("TICKER", "TICKER", ANY, ticker)):
            if m is None or t is None:
                continue
            r = _row(perf, scope, m, t)
            n = int(r["trade_count"]) if r else 0
            tried.append({"level": level, "trades": n})
            if r and n >= need:
                label = " + ".join(x for x in (m if m != ANY else None, t if t != ANY else None) if x)
                return {"status": "MATCHED", "level": level, "label": label, "trade_count": n,
                        "profit_factor": _num(r["profit_factor"]), "win_rate": _num(r["win_rate"]),
                        "max_drawdown": _num(r["max_drawdown"]), "oos_profit_factor": _num(r["oos_profit_factor"]),
                        "tried": tried}
        return {"status": INSUFFICIENT_SAMPLE, "market_regime": market, "ticker_regime": ticker,
                "required_trades": need, "tried": tried}

    def _premarket_match(self, perf: pd.DataFrame, premarket: str | None) -> dict:
        if premarket in PREMARKET_UNUSABLE:
            return {"status": "NOT_USED", "premarket_regime": premarket,
                    "reason": "premarket regime unavailable/unreliable -- market + ticker matching only"}
        r = _row(perf, "PREMARKET", ANY, ANY, premarket)
        n = int(r["trade_count"]) if r else 0
        if not r or n < self.cfg["min_regime_matched_trades"]:
            return {"status": INSUFFICIENT_SAMPLE, "premarket_regime": premarket, "trade_count": n,
                    "required_trades": self.cfg["min_regime_matched_trades"]}
        return {"status": "MATCHED", "premarket_regime": premarket, "trade_count": n,
                "profit_factor": _num(r["profit_factor"]), "win_rate": _num(r["win_rate"])}
