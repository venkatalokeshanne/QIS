"""
Historical evaluation of one (ticker, strategy, timeframe): the evidence the
qualification engine reads (spec sections 28-34, 46).

For each evaluation:
  * the strategy runs through QIS's backtester with TrendSpider-parity
    execution (next-bar-open fills, the model's own stops/targets), at ZERO
    slippage; costs are then applied to every recorded fill at 0x/1x/2x/3x
    the estimated slippage (standard robustness practice; stop/target levels
    are not re-derived from the costed fills);
  * headline metrics use 1x costs (realistic), never 0x;
  * out-of-sample = the last `oos_fraction` of the period (chronological);
  * walk-forward = `walk_forward_periods` consecutive windows, each judged
    profitable or not -- the actual per-window results are stored;
  * parameter stability = the same strategy with its indicator periods
    scaled by nearby factors; share of neighbours that stay profitable;
  * every trade is tagged with the market/ticker/premarket regime known
    BEFORE its entry, and results are aggregated per regime.

Metric definitions (per-trade returns r after costs, full capital per trade):
  profit_factor  sum(r > 0) / |sum(r < 0)|
  expectancy     mean(r)
  sharpe         mean(r) / std(r) * sqrt(trades per year)   (trade-based)
  max_drawdown   largest peak-to-trough fall of prod(1 + r)
"""

from __future__ import annotations

import copy
import datetime as dt
import json
import math
import time
import uuid

import numpy as np
import pandas as pd

from app.strategy_engine.data.calendar import NY
from app.strategy_engine.data.normalize import select_session
from app.strategy_engine.data.resample import resample_rth
from app.strategy_engine.data.store import BarStore, data_version
from app.strategy_engine.historical import ANY, EngineDB, tag_trades
from app.strategy_engine.models import Session, StrategyMeta, Timeframe
from app.strategy_engine.registry import default_registry
from app.strategy_engine.thresholds import EXECUTION_COST_CONFIG, QUALIFICATION_CONFIG, config_version

RESAMPLED_FROM_5M = {Timeframe.M65, Timeframe.H2, Timeframe.H4}
PARAM_KEYS = ("period", "length", "window")
PF_CAP = 99.0


# ----------------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------------


def metrics(returns: np.ndarray, times: np.ndarray | None = None, span_years: float | None = None) -> dict:
    r = np.asarray(returns, dtype=float)
    n = len(r)
    if n == 0:
        return {"trade_count": 0, "win_rate": None, "profit_factor": None, "expectancy": None, "sharpe": None,
                "max_drawdown": None, "total_return": None}
    wins, losses = r[r > 0].sum(), -r[r < 0].sum()
    pf = PF_CAP if losses == 0 else min(PF_CAP, wins / losses)
    equity = np.cumprod(1 + r)
    peak = np.maximum.accumulate(np.concatenate([[1.0], equity]))[1:]
    dd = float((1 - equity / peak).max()) if n else 0.0
    if span_years is None and times is not None and n > 1:
        span_years = max((float(times[-1]) - float(times[0])) / (365.25 * 86400), 1 / 12)
    per_year = n / span_years if span_years else None
    sd = r.std(ddof=1) if n > 1 else 0.0
    sharpe = float(r.mean() / sd * math.sqrt(per_year)) if (sd > 0 and per_year) else None
    return {"trade_count": n, "win_rate": round(float((r > 0).mean()), 4), "profit_factor": round(float(pf), 4),
            "expectancy": round(float(r.mean()), 6), "sharpe": None if sharpe is None else round(sharpe, 4),
            "max_drawdown": round(dd, 4), "total_return": round(float(equity[-1] - 1), 4)}


def costed_returns(trades: pd.DataFrame, cost: float) -> np.ndarray:
    """Per-trade return after `cost` (fraction) applied against you on both fills."""
    e, x = trades["entry_price"].to_numpy(float), trades["exit_price"].to_numpy(float)
    long = (trades["direction"] == "LONG").to_numpy()
    r_long = (x * (1 - cost)) / (e * (1 + cost)) - 1
    r_short = (e * (1 - cost)) / (x * (1 + cost)) - 1
    return np.where(long, r_long, r_short)


# ----------------------------------------------------------------------------
# bars and strategy runs
# ----------------------------------------------------------------------------


def load_bars(store: BarStore, ticker: str, timeframe: Timeframe) -> pd.DataFrame:
    """Regular-session bars for the timeframe (RTH only; strategies trade the session)."""
    if timeframe in RESAMPLED_FROM_5M:
        five = store.load(ticker, Timeframe.M5, source="twelvedata")
        return resample_rth(five, timeframe)
    src = store.load(ticker, timeframe, source="twelvedata")
    return select_session(src, Session.RTH) if timeframe.is_intraday else src


def to_qis_frame(bars: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """QIS strategies expect naive America/New_York timestamps."""
    df = bars[["open", "high", "low", "close", "volume"]].copy()
    df.index = df.index.tz_convert(NY).tz_localize(None)
    df.index.name = "timestamp"
    df.attrs["symbol"] = ticker.upper()
    return df


def _strategy_class(slug: str):
    from app.strategies.registry import discover_strategies, strategy_registry

    discover_strategies()
    return strategy_registry.get(slug)


def _scaled_model(model: dict, factor: float) -> tuple[dict, list[dict]]:
    """Copy of a TrendSpider model with every indicator period/length/window
    input scaled by `factor` (rounded, >= 2). Returns (model, changes)."""
    m = copy.deepcopy(model)
    changes: list[dict] = []

    def walk(node):
        if isinstance(node, dict):
            d = node.get("definition")
            if isinstance(d, dict) and isinstance(d.get("inputs"), dict):
                for k, v in list(d["inputs"].items()):
                    if isinstance(v, bool) or not isinstance(v, (int, float)):
                        continue
                    if any(p in k.lower() for p in PARAM_KEYS) or k.lower().startswith(("fast_", "slow_")):
                        nv = max(2, int(round(v * factor)))
                        if nv != v:
                            changes.append({"indicator": d.get("indicatorType"), "input": k, "from": v, "to": nv})
                            d["inputs"][k] = nv
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(m.get("enterCondition"))
    walk(m.get("exitCondition"))
    return m, changes


def session_open_times(times: pd.Series) -> pd.Series:
    """Daily/weekly/monthly bars are stamped at midnight of their date, but a
    fill on them happens at that session's 09:30 open (or later, for a stop
    inside the bar) -- never before. Restamp to the open so nothing treats a
    trade as entered or closed before it could have been."""
    ny = times.dt.tz_convert(NY)
    return (ny.dt.normalize() + pd.Timedelta(hours=9, minutes=30)).dt.tz_convert("UTC")


def run_trades(slug: str, df: pd.DataFrame, model_override: dict | None = None,
               timeframe: Timeframe | None = None) -> pd.DataFrame:
    cls = _strategy_class(slug)
    if model_override is not None:
        cls = type(cls.__name__ + "Variant", (cls,), {"MODEL": model_override})
    strat = cls()
    execution = strat.recommended_execution(slippage_pct=0.0, commission_per_trade=0.0)
    trades = strat.run(df, {}, execution)
    rows = [{"entry_time": t.entry_time, "exit_time": t.exit_time, "direction": str(getattr(t.direction, "value", t.direction)).upper(),
             "entry_price": float(t.entry_price), "exit_price": float(t.exit_price)}
            for t in trades if t.exit_price is not None and t.entry_price]
    out = pd.DataFrame(rows, columns=["entry_time", "exit_time", "direction", "entry_price", "exit_price"])
    for col in ("entry_time", "exit_time"):
        out[col] = pd.to_datetime(out[col]).dt.tz_localize(NY, ambiguous="infer", nonexistent="shift_forward").dt.tz_convert("UTC")
        if timeframe is not None and not timeframe.is_intraday and len(out):
            out[col] = session_open_times(out[col])
    return out


def _unix(s: pd.Series) -> np.ndarray:
    """Unix seconds. Unit-safe: pandas may store datetimes in s/ms/us/ns."""
    return s.dt.tz_convert("UTC").dt.as_unit("s").astype("int64").to_numpy()


# ----------------------------------------------------------------------------
# evaluator
# ----------------------------------------------------------------------------


class StrategyEvaluator:
    def __init__(self, store: BarStore | None = None, db: EngineDB | None = None, config: dict | None = None,
                 costs: dict | None = None):
        self.store = store or BarStore()
        self.db = db or EngineDB()
        self.cfg = {**QUALIFICATION_CONFIG, "parameter_neighbours": [0.8, 0.9, 1.1, 1.2], **(config or {})}
        self.costs = {**EXECUTION_COST_CONFIG, **(costs or {})}

    def evaluate(self, ticker: str, strategy: StrategyMeta, timeframe: Timeframe) -> dict:
        run_id = uuid.uuid4().hex[:12]
        started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        t0 = time.time()
        base = {"run_id": run_id, "ticker": ticker.upper(), "strategy_id": strategy.id, "timeframe": str(timeframe),
                "started": started, "config_version": config_version(), "catalog_version": default_registry().version}
        try:
            bars = load_bars(self.store, ticker, timeframe)
            if bars.empty:
                raise ValueError(f"no stored {timeframe} bars for {ticker}")
            df = to_qis_frame(bars, ticker)
            trades = run_trades(strategy.slug, df, timeframe=timeframe)
            span_years = max((bars.index[-1] - bars.index[0]).days / 365.25, 1 / 12)
            result = self._analyse(ticker, strategy, timeframe, trades, bars, span_years, run_id)
            summary = {k: result["all_time"].get(k) for k in ("trade_count", "profit_factor", "sharpe", "max_drawdown")}
            summary["seconds"] = round(time.time() - t0, 1)
            self.db.record_run(**base, finished=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               bars_from=str(bars.index[0]), bars_to=str(bars.index[-1]),
                               data_version=data_version(bars), status="OK", summary=summary)
            return result
        except Exception as exc:  # recorded, never silently skipped
            self.db.record_run(**base, finished=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               status="ERROR", error=f"{type(exc).__name__}: {exc}"[:500])
            raise

    # -- analysis ---------------------------------------------------------------
    def _analyse(self, ticker, strategy: StrategyMeta, timeframe, trades, bars, span_years, run_id) -> dict:
        c1 = self.costs["rth_slippage"]
        tags = tag_trades(_unix(trades["entry_time"]) if len(trades) else np.array([], dtype=int),
                          self.db.load_market_history(), self.db.load_ticker_history(ticker),
                          self.db.load_premarket_history(ticker), strategy.uses_premarket)
        trades = pd.concat([trades.reset_index(drop=True), tags], axis=1)
        trades["entry_time"] = _unix(trades["entry_time"]) if len(trades) else np.array([], dtype=int)
        trades["exit_time"] = _unix(trades["exit_time"]) if len(trades) else np.array([], dtype=int)
        base_pf = metrics(costed_returns(trades, c1))["profit_factor"] if len(trades) else None
        stab, variants = self._parameter_stability(strategy, bars, ticker, base_pf, timeframe)
        t_start, t_end = bars.index[0].timestamp(), bars.index[-1].timestamp()
        rows, all_time, details, robustness = aggregate(trades, t_start, t_end, strategy, run_id, self.cfg, c1, stab)
        details.update({"bars_from": str(bars.index[0]), "bars_to": str(bars.index[-1])})
        trades["variant"] = "base"
        trades["gross_return"] = costed_returns(trades, 0.0) if len(trades) else []
        stored = [trades] + [v for v in variants if len(v)]
        self.db.replace_trades(run_id, ticker, strategy.id, str(timeframe), pd.concat(stored, ignore_index=True))
        self.db.replace_performance(ticker, strategy.id, str(timeframe), rows)
        return {"all_time": all_time, "rows": len(rows), "details": details, "robustness": robustness}

    def _parameter_stability(self, strategy: StrategyMeta, bars: pd.DataFrame, ticker: str,
                             base_pf: float | None, timeframe: Timeframe | None = None) -> tuple[dict, list[pd.DataFrame]]:
        """(stability summary, neighbour trade lists). The neighbours' trades are
        stored as variants so stability can be recomputed point-in-time."""
        cls = _strategy_class(strategy.slug)
        model = getattr(cls, "MODEL", None)
        if not model:
            return {"status": "NOT_APPLICABLE", "score": None, "reason": "strategy exposes no parameter model"}, []
        df = to_qis_frame(bars, ticker)
        variants, surface = [], []
        for f in self.cfg["parameter_neighbours"]:
            variant, changes = _scaled_model(model, f)
            if not changes:
                continue
            entry = {"factor": f, "changes": changes}
            try:
                t = run_trades(strategy.slug, df, model_override=variant, timeframe=timeframe)
                if len(t):
                    t = t.assign(entry_time=_unix(t["entry_time"]), exit_time=_unix(t["exit_time"]),
                                 variant=variant_name(f), gross_return=costed_returns(t, 0.0),
                                 market_regime=None, ticker_regime=None, premarket_regime=None, sample=None)
                    variants.append(t)
                entry["trades"] = t
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"[:200]
            surface.append(entry)
        if not surface:
            return {"status": "NOT_APPLICABLE", "score": None, "reason": "no numeric period/length inputs to perturb",
                    "surface": []}, []
        return stability(surface, base_pf, self.costs["rth_slippage"]), variants


# ----------------------------------------------------------------------------
# aggregation -- shared by the evaluator and point-in-time qualification
# ----------------------------------------------------------------------------


def utc(ts) -> pd.Timestamp:
    """Timestamp in UTC; naive values are taken as UTC (how evaluations store them)."""
    t = pd.Timestamp(ts)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def variant_name(factor: float) -> str:
    return f"params_x{factor:g}"


def stability(surface: list[dict], base_pf: float | None, cost: float) -> dict:
    """surface: [{"factor", "changes", "trades": DataFrame | None, "error"?}] ->
    share of neighbouring parameter sets that stay profitable (and within 70%
    of the base profit factor)."""
    out = []
    for s in surface:
        t = s.get("trades")
        m = metrics(costed_returns(t, cost)) if t is not None and len(t) else metrics([])
        out.append({"factor": s["factor"], "changes": s.get("changes"), "error": s.get("error"),
                    **{k: m.get(k) for k in ("trade_count", "profit_factor", "total_return")}})
    good = [s for s in out if (s.get("profit_factor") or 0) >= 1.0
            and (base_pf is None or (s.get("profit_factor") or 0) >= 0.7 * base_pf)]
    return {"status": "TESTED", "score": round(len(good) / len(out), 4), "neighbours": len(out),
            "stable_neighbours": len(good), "base_profit_factor": base_pf, "surface": out}


def aggregate(trades: pd.DataFrame, t_start: float, t_end: float, strategy: StrategyMeta, run_id: str | None,
              cfg: dict, c1: float, stab: dict) -> tuple[list[dict], dict, dict, str]:
    """Performance rows (ALL_TIME + per regime) for trades over [t_start, t_end].

    `trades` needs direction, entry_price, exit_price, entry_time (unix s) and
    the regime tag columns. Returns (rows, all_time, details, robustness);
    also sets trades["sample"]."""
    span_years = max((t_end - t_start) / (365.25 * 86400), 1 / 12)
    entry_s = trades["entry_time"].to_numpy(dtype="int64") if len(trades) else np.array([], dtype="int64")
    r1 = costed_returns(trades, c1) if len(trades) else np.array([])

    # out-of-sample split (chronological)
    split = t_start + (1 - cfg["oos_fraction"]) * (t_end - t_start)
    is_oos = entry_s >= split
    trades["sample"] = np.where(is_oos, "OUT_OF_SAMPLE", "IN_SAMPLE") if len(trades) else []
    in_m = metrics(r1[~is_oos], span_years=span_years * (1 - cfg["oos_fraction"]))
    oos_m = metrics(r1[is_oos], span_years=span_years * cfg["oos_fraction"])

    # walk-forward windows
    k = cfg["walk_forward_periods"]
    edges = np.linspace(t_start, t_end, k + 1)
    windows = []
    for i in range(k):
        sel = (entry_s >= edges[i]) & ((entry_s < edges[i + 1]) if i < k - 1 else (entry_s <= edges[i + 1]))
        m = metrics(r1[sel], span_years=span_years / k)
        windows.append({"from": str(pd.Timestamp(edges[i], unit="s", tz="UTC").date()),
                        "to": str(pd.Timestamp(edges[i + 1], unit="s", tz="UTC").date()),
                        "trades": m["trade_count"], "profit_factor": m["profit_factor"],
                        "return": m["total_return"], "profitable": bool(m["trade_count"] and (m["total_return"] or 0) > 0)})
    with_trades = [w for w in windows if w["trades"]]
    wf = {"walk_forward_periods": len(with_trades), "profitable_periods": sum(w["profitable"] for w in with_trades),
          "pass_rate": round(sum(w["profitable"] for w in with_trades) / len(with_trades), 4) if with_trades else None,
          "windows": windows}

    # slippage robustness
    slip = {}
    for mult in cfg["slippage_multipliers"]:
        m = metrics(costed_returns(trades, c1 * mult), span_years=span_years) if len(trades) else metrics([])
        slip[f"{mult}x"] = {"profit_factor": m["profit_factor"], "total_return": m["total_return"], "expectancy": m["expectancy"]}
    pf2 = slip.get("2x", {}).get("profit_factor")
    pf1 = slip.get("1x", {}).get("profit_factor")
    robustness = ("HIGH" if pf2 is not None and pf2 >= cfg["min_pf_at_2x_slippage"]
                  else "MEDIUM" if pf1 is not None and pf1 >= 1.0 else "LOW")

    all_time = metrics(r1, span_years=span_years)
    if len(trades):
        hold_days = np.maximum((trades["exit_time"].to_numpy(dtype="float64")
                                - trades["entry_time"].to_numpy(dtype="float64")) / 86400, 1 / 24)
        # total return per capital-day, NOT the mean of per-trade ratios: a
        # 20-minute loss would otherwise count as a huge daily rate and swamp
        # longer winning trades.
        all_time["expectancy_per_capital_day"] = round(float(r1.sum() / hold_days.sum()), 6)
        all_time["mean_hold_days"] = round(float(hold_days.mean()), 3)
    else:
        all_time["expectancy_per_capital_day"] = all_time["mean_hold_days"] = None
    details = {"costs": {"one_way_slippage_1x": c1}, "in_sample": in_m, "out_of_sample": oos_m, "walk_forward": wf,
               "slippage": slip, "parameter_stability": stab, "span_years": round(span_years, 2),
               "expectancy_per_capital_day": all_time["expectancy_per_capital_day"],
               "mean_hold_days": all_time["mean_hold_days"]}
    rows = [perf_row("ALL_TIME", ANY, ANY, ANY, strategy, all_time, run_id, details=details,
                     oos_pf=oos_m["profit_factor"], wf=wf["pass_rate"], stab=stab.get("score"), robust=robustness)]
    groups = [("MARKET", ["market_regime"]), ("TICKER", ["ticker_regime"]), ("PREMARKET", ["premarket_regime"]),
              ("MARKET_TICKER", ["market_regime", "ticker_regime"])]
    positions = np.arange(len(trades))
    for scope, cols in groups:
        if not len(trades):
            break
        # untagged trades (regime unknown at entry) group under "UNKNOWN"
        keyed = trades[cols].reset_index(drop=True).map(lambda v: v if isinstance(v, str) else "UNKNOWN")
        for key, idx in keyed.groupby(cols).indices.items():
            key = key if isinstance(key, tuple) else (key,)
            labels = dict(zip(cols, key))
            sel = np.isin(positions, idx)
            m = metrics(r1[sel], span_years=span_years)
            oos_sel = sel & is_oos
            rows.append(perf_row(scope, labels.get("market_regime", ANY), labels.get("ticker_regime", ANY),
                                 labels.get("premarket_regime", ANY), strategy, m, run_id,
                                 oos_pf=metrics(r1[oos_sel])["profit_factor"],
                                 details={"oos_trades": int(oos_sel.sum())}))
    return rows, all_time, details, robustness


def perf_row(scope, market, tick, pm, strategy: StrategyMeta, m: dict, run_id: str | None, *, details=None, oos_pf=None,
             wf=None, stab=None, robust=None) -> dict:
    return {"scope": scope, "market_regime": market, "ticker_regime": tick, "premarket_regime": pm,
            "family": str(strategy.family), "trade_count": m["trade_count"], "win_rate": m["win_rate"],
            "profit_factor": m["profit_factor"], "expectancy": m["expectancy"], "sharpe": m["sharpe"],
            "max_drawdown": m["max_drawdown"], "oos_profit_factor": oos_pf, "walk_forward_pass_rate": wf,
            "parameter_stability": stab, "slippage_robustness": robust, "run_id": run_id, "details": details or {}}


def point_in_time_performance(db: EngineDB, ticker: str, strategy: StrategyMeta, timeframe: str,
                              as_of: pd.Timestamp, stored_details: dict, cfg: dict | None = None,
                              costs: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """Rebuild the performance rows from stored trades CLOSED before `as_of`,
    over the window [bars_from, as_of) -- exactly what an evaluation run at
    that moment would have produced (same aggregation code). Returns
    (rows as a load_performance-shaped frame, info)."""
    cfg = {**QUALIFICATION_CONFIG, **(cfg or {})}
    c1 = {**EXECUTION_COST_CONFIG, **(costs or {})}["rth_slippage"]
    cutoff = int(utc(as_of).timestamp())
    t_start = utc(stored_details["bars_from"]).timestamp()
    all_trades = db.load_trades(ticker, strategy.id, timeframe, variant=None)
    closed = all_trades[all_trades["exit_time"].notna() & (all_trades["exit_time"] < cutoff)]
    base = closed[closed["variant"] == "base"].reset_index(drop=True)
    base_pf = metrics(costed_returns(base, c1))["profit_factor"] if len(base) else None

    stored_stab = stored_details.get("parameter_stability") or {}
    have_variants = (closed["variant"] != "base").any() or (all_trades["variant"] != "base").any()
    if stored_stab.get("status") != "TESTED":
        stab, stab_pit = stored_stab, True
    elif have_variants:
        surface = [{"factor": s["factor"], "changes": s.get("changes"), "error": s.get("error"),
                    "trades": closed[closed["variant"] == variant_name(s["factor"])]}
                   for s in stored_stab.get("surface", [])]
        stab, stab_pit = stability(surface, base_pf, c1), True
    else:
        stab, stab_pit = stored_stab, False       # evaluated before neighbour trades were stored

    if t_start >= cutoff:
        rows = []
    else:
        rows, _, details, _ = aggregate(base, t_start, cutoff, strategy, None, cfg, c1, stab)
        details.update({"bars_from": stored_details["bars_from"], "bars_to": str(pd.Timestamp(as_of)),
                        "point_in_time": True})
        rows[0]["details"] = details
    frame = pd.DataFrame([{**r, "details": json.dumps(r["details"], default=str)} for r in rows])
    return frame, {"trades_closed_before": len(base), "trades_total": int((all_trades["variant"] == "base").sum()),
                   "parameter_stability_point_in_time": stab_pit}
