"""
Research dataset for improving strategy selection.

One row per (ticker, timeframe, strategy, trading day D). Every feature is
computed ONLY from trades that had closed before D at the decision time
(09:25 New York) and from the regimes known then; the outcome is what the
strategy's trades entered on D (at or after the decision time) returned,
after 1x costs. Selection rules can then be evaluated in seconds instead of
re-running the engine, and tuned on a development period while a later
holdout period stays untouched.
"""

from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

import numpy as np
import pandas as pd

from app.strategy_engine.data.calendar import NY, trading_days
from app.strategy_engine.evaluation import costed_returns
from app.strategy_engine.historical import EngineDB
from app.strategy_engine.models import AssetScope
from app.strategy_engine.registry import default_registry
from app.strategy_engine.strategy_family import NOT_APPLICABLE, StrategyFamilyEngine
from app.strategy_engine.thresholds import EXECUTION_COST_CONFIG

DECISION_TIME = "09:25"
# A stop closer than this cannot be trusted at bar resolution: the backtest
# fills it exactly at the level, while a real fill slips through it.
MIN_TRUSTED_STOP = 0.0025
WINDOWS = (20, 50)
RECENT_DAYS = 90


def _last_known_idx(known: np.ndarray, ts: np.ndarray) -> np.ndarray:
    return np.searchsorted(known, ts, side="right") - 1


class _Cum:
    """Prefix sums over trades ordered by exit time -> O(1) stats of any
    prefix / suffix window."""

    def __init__(self, r: np.ndarray):
        z = np.zeros(1)
        self.n = len(r)
        self.ret = np.concatenate([z, np.cumsum(r)])
        self.pos = np.concatenate([z, np.cumsum(np.where(r > 0, r, 0.0))])
        self.neg = np.concatenate([z, np.cumsum(np.where(r < 0, -r, 0.0))])
        self.win = np.concatenate([z, np.cumsum(r > 0)])

    def window(self, lo: np.ndarray, hi: np.ndarray) -> dict:
        n = hi - lo
        with np.errstate(divide="ignore", invalid="ignore"):
            pos, neg = self.pos[hi] - self.pos[lo], self.neg[hi] - self.neg[lo]
            return {"n": n, "exp": np.where(n > 0, (self.ret[hi] - self.ret[lo]) / np.maximum(n, 1), np.nan),
                    "pf": np.where(n > 0, np.where(neg > 0, pos / np.where(neg > 0, neg, 1), np.where(pos > 0, 99.0, np.nan)), np.nan),
                    "win": np.where(n > 0, (self.win[hi] - self.win[lo]) / np.maximum(n, 1), np.nan)}


def stop_distances() -> dict[str, float]:
    """slug -> stop-loss distance (fraction) declared by the model, if any."""
    from app.strategies.trendspider.strategy import _risk_settings, load_models

    models = load_models()
    out = {}
    for slug, model in models.items():
        sl = _risk_settings(model).get("stop_loss_pct")
        if sl is not None:
            out[slug] = sl
    return out


def duplicate_groups(db: EngineDB, ticker: str, timeframe: str, strategy_ids: list[int],
                     overlap: float = 0.9) -> dict[int, int]:
    """Strategies whose trades are (nearly) the same on this ticker/timeframe
    map to one group id -- picking both would double the position while the
    backtest counts them as two independent edges."""
    entries = {}
    for sid in strategy_ids:
        sid = int(sid)                      # numpy ints bind to no rows in sqlite
        t = db.load_trades(ticker, sid, timeframe)
        if len(t):
            entries[sid] = set(t["entry_time"].tolist())
    group, gid = {}, {}
    for sid, e in entries.items():
        for other, g in list(gid.items()):
            o = entries[other]
            if o and e and len(e & o) / max(len(e | o), 1) >= overlap:
                group[sid] = g
                break
        else:
            gid[sid] = group[sid] = len(gid)
    return group


def build_dataset(tickers: list[str], timeframes: list[str], start: dt.date, end: dt.date,
                  db: EngineDB | None = None) -> pd.DataFrame:
    db = db or EngineDB()
    reg = default_registry()
    fam_engine = StrategyFamilyEngine()
    cost = EXECUTION_COST_CONFIG["rth_slippage"]
    days = trading_days(start, end)
    day_ts = np.array([int(pd.Timestamp(f"{d} {DECISION_TIME}", tz=NY).timestamp()) for d in days])
    day_str = np.array([str(d) for d in days])
    market_h = db.load_market_history()
    frames = []
    for ticker in tickers:
        ticker = ticker.upper()
        ticker_h = db.load_ticker_history(ticker)
        pm_h = db.load_premarket_history(ticker)
        mi = _last_known_idx(market_h["known_at"].to_numpy(), day_ts)
        ti = _last_known_idx(ticker_h["known_at"].to_numpy(), day_ts)
        pm_by_day = {r.date: r for r in pm_h.itertuples() if r.known_at <= int(pd.Timestamp(f"{r.date} {DECISION_TIME}", tz=NY).timestamp())}
        ctx = pd.DataFrame({
            "date": day_str,
            "market_regime": np.where(mi >= 0, market_h["market_regime"].to_numpy()[np.maximum(mi, 0)], None),
            "market_direction": np.where(mi >= 0, market_h["market_direction"].to_numpy()[np.maximum(mi, 0)], None),
            "market_volatility": np.where(mi >= 0, market_h["market_volatility"].to_numpy()[np.maximum(mi, 0)], None),
            "ticker_regime": np.where(ti >= 0, ticker_h["ticker_regime"].to_numpy()[np.maximum(ti, 0)], None),
            "ticker_trend": np.where(ti >= 0, ticker_h["trend"].to_numpy()[np.maximum(ti, 0)], None),
            "ticker_momentum": np.where(ti >= 0, ticker_h["momentum"].to_numpy()[np.maximum(ti, 0)], None),
            "ticker_volatility": np.where(ti >= 0, ticker_h["volatility"].to_numpy()[np.maximum(ti, 0)], None),
            "premarket_regime": [pm_by_day[d].premarket_regime if d in pm_by_day else "PREMARKET_DATA_UNAVAILABLE" for d in day_str],
            "premarket_structure": [pm_by_day[d].premarket_structure if d in pm_by_day else None for d in day_str],
        })
        # the family decision for each day (same rules as the live engine)
        fams = []
        for row in ctx.itertuples():
            m = SimpleNamespace(direction=row.market_direction, volatility=row.market_volatility, market_regime=row.market_regime)
            t = SimpleNamespace(trend=row.ticker_trend, momentum=row.ticker_momentum, ticker_regime=row.ticker_regime)
            p = SimpleNamespace(premarket_regime=row.premarket_regime, structure=row.premarket_structure)
            fams.append(fam_engine.decide(m, t, p))

        for tf in timeframes:
            for s in reg.all():
                if not s.runnable or not any(str(x) == tf for x in s.timeframes):
                    continue
                if s.asset_scope is AssetScope.SPECIFIC_TICKER and ticker not in s.allowed_tickers:
                    continue
                t = db.load_trades(ticker, s.id, tf)
                if t.empty:
                    continue
                t = t[t["exit_time"].notna()].copy()
                t["ret"] = costed_returns(t, cost)
                by_exit = t.sort_values("exit_time")
                exit_s = by_exit["exit_time"].to_numpy(dtype="int64")
                r = by_exit["ret"].to_numpy()
                cum = _Cum(r)
                hold_days_tr = np.maximum((by_exit["exit_time"] - by_exit["entry_time"]).to_numpy() / 86400, 1 / 24)
                cum_day = _Cum(r / hold_days_tr)        # return per day of capital
                k = np.searchsorted(exit_s, day_ts, side="left")               # trades closed strictly before 09:25
                feats = {"n_closed": k}
                allw = cum.window(np.zeros_like(k), k)
                feats.update({"exp_all": allw["exp"], "pf_all": allw["pf"], "win_all": allw["win"]})
                for w in WINDOWS:
                    ww = cum.window(np.maximum(k - w, 0), k)
                    feats.update({f"exp_last{w}": ww["exp"], f"pf_last{w}": ww["pf"], f"win_last{w}": ww["win"]})
                dayw = cum_day.window(np.zeros_like(k), k)
                feats["exp_day_all"] = dayw["exp"]
                feats["exp_day_last50"] = cum_day.window(np.maximum(k - 50, 0), k)["exp"]
                lo90 = np.searchsorted(exit_s, day_ts - RECENT_DAYS * 86400, side="left")
                w90 = cum.window(np.minimum(lo90, k), k)
                feats.update({"n_90d": w90["n"], "exp_90d": w90["exp"], "pf_90d": w90["pf"]})
                feats["days_since_close"] = np.where(k > 0, (day_ts - exit_s[np.maximum(k - 1, 0)]) / 86400, np.nan)
                # regime-matched records: trades whose entry-time regime equals today's
                for col, today in (("market_regime", ctx["market_regime"].to_numpy()),
                                   ("ticker_regime", ctx["ticker_regime"].to_numpy())):
                    lab = by_exit[col].fillna("UNKNOWN").to_numpy()
                    n_m, e_m = np.zeros(len(days)), np.full(len(days), np.nan)
                    for label in set(today) - {None}:
                        mask = lab == label
                        c = _Cum(np.where(mask, r, 0.0))
                        cnt = np.concatenate([[0], np.cumsum(mask)])
                        sel = today == label
                        n_here = cnt[k[sel]]
                        n_m[sel] = n_here
                        e_m[sel] = np.where(n_here > 0, c.ret[k[sel]] / np.maximum(n_here, 1), np.nan)
                    feats[f"n_{col}"] = n_m
                    feats[f"exp_{col}"] = e_m
                hold_h = (by_exit["exit_time"] - by_exit["entry_time"]).to_numpy() / 3600
                feats["median_hold_h"] = np.array([np.median(hold_h[:kk]) if kk else np.nan for kk in k])
                # outcome: trades entered on D at/after the decision time
                entry_day = pd.to_datetime(t["entry_time"], unit="s", utc=True).dt.tz_convert(NY).dt.date.astype(str).to_numpy()
                ok = t["entry_time"].to_numpy() >= np.array([int(pd.Timestamp(f"{d} {DECISION_TIME}", tz=NY).timestamp()) for d in entry_day])
                out = pd.DataFrame({"date": entry_day[ok], "ret": t["ret"].to_numpy()[ok],
                                    "hold_h": ((t["exit_time"] - t["entry_time"]).to_numpy() / 3600)[ok],
                                    "same_day": (entry_day[ok] == pd.to_datetime(t["exit_time"].to_numpy()[ok], unit="s", utc=True)
                                                 .tz_convert(NY).date.astype(str))})
                out["hold_days"] = np.maximum(out["hold_h"] / 24.0, 1 / 24)   # a trade uses capital for at least an hour
                g = out.groupby("date").agg(n_today=("ret", "size"), ret_today=("ret", "sum"),
                                            same_day_today=("same_day", "all"), hold_days_today=("hold_days", "sum"))
                f = pd.DataFrame({"ticker": ticker, "timeframe": tf, "strategy_id": s.id, "strategy": s.name,
                                  "family": str(s.family), "date": day_str, **feats})
                f["family_status"] = [fam_engine.strategy_status(s, fd)[0] for fd in fams]
                f = f.merge(g, left_on="date", right_index=True, how="left")
                f["n_today"] = f["n_today"].fillna(0).astype(int)
                f["ret_today"] = f["ret_today"].fillna(0.0)
                f["hold_days_today"] = f["hold_days_today"].fillna(0.0)
                frames.append(f.merge(ctx, on="date", how="left"))
    data = pd.concat(frames, ignore_index=True)
    data["family_ok"] = data["family_status"] != NOT_APPLICABLE
    stops = stop_distances()
    by_id = {s.id: s for s in reg.all()}
    data["stop_pct"] = data["strategy_id"].map(lambda i: stops.get(by_id[i].slug.replace("ts_", "", 1), stops.get(by_id[i].slug)))
    data["fragile_stop"] = data["stop_pct"].notna() & (data["stop_pct"] < MIN_TRUSTED_STOP)
    groups = {}
    for (tk, tf), part in data.groupby(["ticker", "timeframe"]):
        for sid, g in duplicate_groups(db, tk, tf, sorted(part["strategy_id"].unique())).items():
            groups[(tk, tf, sid)] = g
    data["dup_group"] = [groups.get((t, f, int(i)), -1) for t, f, i in zip(data["ticker"], data["timeframe"], data["strategy_id"])]
    if (data["dup_group"] < 0).any():       # every strategy with trades must land in a group
        missing = sorted(set(data.loc[data["dup_group"] < 0, "strategy"]))
        raise ValueError(f"duplicate grouping missed {len(missing)} strategies, e.g. {missing[:3]}")
    return data
