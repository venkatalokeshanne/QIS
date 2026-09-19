"""
Ticker Regime Detector (spec sections 13-22).

Classifies ONE ticker independently of the market -- QQQ can be bullish
while the ticker is in a downtrend. Every threshold that depends on how
volatile a stock normally is uses the ticker's OWN history (percentiles),
so INFQ and MSFT are never judged by the same absolute ATR.

Point in time: daily features use only sessions that had CLOSED before the
decision timestamp; intraday features (time-of-day RVOL, today's gap) use
only intraday bars completed before it.

`confidence` = agreement among the indicators behind the labels. It is NOT
a probability of any future return.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from app.strategy_engine import indicators as ind
from app.strategy_engine.data.calendar import NY, session_bounds, trading_days
from app.strategy_engine.data.normalize import daily_upto, upto
from app.strategy_engine.models import Session, Timeframe
from app.strategy_engine.thresholds import TICKER_REGIME_CONFIG
from app.strategy_engine.validators import DATA_INSUFFICIENT, OK, check_bars

VOL_LABELS = ["LOW", "NORMAL", "HIGH", "EXTREME"]
RVOL_LABELS = ["LOW_VOLUME", "NORMAL_VOLUME", "HIGH_VOLUME", "EXTREME_VOLUME"]
GAP_LABELS = ["NO_GAP", "SMALL_GAP", "MODERATE_GAP", "LARGE_GAP", "EXTREME_GAP"]


@dataclass
class TickerRegime:
    ticker: str
    status: str
    as_of: str | None = None
    decision_ts: str | None = None
    trend: str | None = None
    momentum: str | None = None
    relative_strength: str | None = None
    volatility: str | None = None
    volume: str | None = None
    gap: str | None = None
    gap_direction: str | None = None
    liquidity: str | None = None
    event_status: str = "UNKNOWN"
    news_status: str = "UNKNOWN"
    premarket_regime: str = "NOT_EVALUATED"   # filled by the premarket detector
    ticker_regime: str | None = None
    confidence: int | None = None
    raw_trend: str | None = None
    raw_volatility: str | None = None
    features: dict = field(default_factory=dict)
    data_quality: list = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _trend_frame(daily: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    c = daily["close"]
    f = pd.DataFrame(index=daily.index)
    f["close"] = c
    for p in cfg["ema_periods"]:
        f[f"ema{p}"] = ind.ema(c, p)
    f["sma200"] = ind.sma(c, cfg["sma_long"])
    lb = cfg["slope_lookback"]
    f["ema20_slope"] = f["ema20"] / f["ema20"].shift(lb) - 1
    f["ema50_slope"] = f["ema50"] / f["ema50"].shift(lb) - 1
    f["price_vs_ema20"] = c / f["ema20"] - 1
    f["price_vs_ema50"] = c / f["ema50"] - 1
    s = cfg["strong_trend_slope"]
    up = (c > f["ema20"]) & (f["ema20"] > f["ema50"]) & (f["ema20_slope"] > 0)
    strong_up = up & (f["ema20_slope"] > s) & (f["ema50_slope"] > 0) & (f["ema9"] > f["ema20"])
    down = (c < f["ema20"]) & (f["ema20"] < f["ema50"]) & (f["ema20_slope"] < 0)
    strong_down = down & (f["ema20_slope"] < -s) & (f["ema50_slope"] < 0) & (f["ema9"] < f["ema20"])
    label = np.select([strong_up, up, strong_down, down],
                      ["STRONG_UPTREND", "UPTREND", "STRONG_DOWNTREND", "DOWNTREND"], "NEUTRAL")
    f["trend"] = pd.Series(label, index=f.index, dtype=object).where(f["ema50_slope"].notna(), None)
    # momentum (descriptive)
    f["roc"] = ind.roc(c, cfg["roc_period"])
    f["rsi"] = ind.rsi(c, cfg["rsi_period"])
    m = ind.macd(c, *cfg["macd"])
    f["macd"], f["macd_signal"], f["macd_hist"] = m["macd"], m["signal"], m["hist"]
    pos = (f["roc"] > 0).astype(int) + (f["rsi"] > 50).astype(int) + (f["macd_hist"] > 0).astype(int) + (f["macd"] > 0).astype(int)
    strong = (f["roc"] > 0) & (f["rsi"] >= 60) & (f["macd_hist"] > 0) & (f["macd"] > 0)
    very_neg = (f["roc"] < 0) & (f["rsi"] <= 40) & (f["macd_hist"] < 0) & (f["macd"] < 0)
    mom = np.select([strong, very_neg, pos >= 3, pos <= 1], ["STRONG", "VERY_NEGATIVE", "POSITIVE", "NEGATIVE"], "NEUTRAL")
    f["momentum"] = pd.Series(mom, index=f.index, dtype=object).where(f["macd_signal"].notna() & f["rsi"].notna(), None)
    # volatility vs own history
    w = cfg["volatility_history_bars"]
    f["atr_pct"] = ind.atr(daily, cfg["atr_period"]) / c
    f["hv"] = ind.realized_vol(c, cfg["hv_period"])
    f["adr_pct"] = ((daily["high"] - daily["low"]) / c).rolling(20, min_periods=20).mean()
    f["atr_pct_pctile"] = ind.trailing_percentile(f["atr_pct"], w)
    f["hv_pctile"] = ind.trailing_percentile(f["hv"], w)
    f["vol_pctile"] = f[["atr_pct_pctile", "hv_pctile"]].mean(axis=1, skipna=False)
    f["volatility"] = [ind.classify_percentile(p, cfg["volatility_percentiles"], VOL_LABELS) for p in f["vol_pctile"]]
    # liquidity
    lb_liq = cfg["liquidity_lookback_days"]
    f["avg_volume"] = daily["volume"].rolling(lb_liq, min_periods=lb_liq).mean()
    f["avg_dollar_volume"] = (daily["volume"] * c).rolling(lb_liq, min_periods=lb_liq).mean()
    f["daily_rvol"] = daily["volume"] / daily["volume"].shift(1).rolling(cfg["rvol_lookback_days"], min_periods=cfg["rvol_lookback_days"]).mean()
    f["gap_pct"] = daily["open"] / c.shift(1) - 1
    return f


def _cut(value: float | None, levels: list[float], labels: list[str]) -> str | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    for lvl, lab in zip(levels, labels):
        if value < lvl:
            return lab
    return labels[-1]


class TickerRegimeDetector:
    def __init__(self, config: dict | None = None):
        self.cfg = {**TICKER_REGIME_CONFIG, **(config or {})}

    def detect(self, ticker: str, daily: pd.DataFrame, benchmarks: dict[str, pd.DataFrame],
               decision_ts: pd.Timestamp, intraday: pd.DataFrame | None = None,
               intraday_timeframe: Timeframe | None = None, earnings: dict | None = None) -> TickerRegime:
        """
        daily       normalized daily bars of the ticker
        benchmarks  normalized daily bars of SPY/QQQ (relative strength)
        intraday    optional normalized intraday bars (RTH used for time-of-day
                    RVOL and today's opening gap)
        earnings    optional {"expected_report_date": date|None} (Tastytrade);
                    None -> event_status UNKNOWN
        """
        cfg = self.cfg
        ts = _as_ny(decision_ts)
        d = daily_upto(daily, ts)
        rep = check_bars(d, ticker, Timeframe.D1, min_bars=cfg["min_daily_bars"])
        out = TickerRegime(ticker=ticker.upper(), status=OK, decision_ts=ts.isoformat(), data_quality=[rep.to_dict()])
        if rep.status != OK:
            out.status = DATA_INSUFFICIENT
            out.reasons = [f"daily data: {'; '.join(rep.issues)}"]
            return out

        f = _trend_frame(d, cfg)
        n = cfg["minimum_confirmation_period"]
        trend = ind.persist(f["trend"], n)
        vol = ind.persist(f["volatility"], n)
        last = f.iloc[-1]
        if trend.iloc[-1] is None or last["momentum"] is None or vol.iloc[-1] is None:
            out.status = DATA_INSUFFICIENT
            out.reasons = ["not enough daily history for EMA50/SMA200 slopes, MACD or volatility percentiles"]
            return out

        out.as_of = str(d.index[-1].tz_convert(NY).date())
        out.trend, out.raw_trend = trend.iloc[-1], last["trend"]
        out.momentum = last["momentum"]
        out.volatility, out.raw_volatility = vol.iloc[-1], last["volatility"]

        rs, rs_features = self._relative_strength(d, benchmarks, ts)
        out.relative_strength = rs

        # Volume: time-of-day RVOL when intraday bars exist and the session
        # has started; otherwise the last completed day's RVOL.
        vol_features = self._volume(d, f, ts, intraday, intraday_timeframe)
        out.volume = vol_features["label"]

        gap_features = self._gap(d, ts, intraday, intraday_timeframe)
        out.gap, out.gap_direction = gap_features["label"], gap_features["direction"]

        adv = last["avg_dollar_volume"]
        out.liquidity = _cut(adv, cfg["liquidity_dollar_volume"], ["LOW_LIQUIDITY", "MEDIUM_LIQUIDITY", "HIGH_LIQUIDITY"])

        out.event_status, event_note = self._event(earnings, ts.date())

        out.features = {
            "trend": {k: _r(last[k]) for k in ("close", "ema9", "ema20", "ema50", "sma200", "price_vs_ema20",
                                                 "price_vs_ema50", "ema20_slope", "ema50_slope")},
            "momentum": {k: _r(last[k]) for k in ("roc", "rsi", "macd", "macd_signal", "macd_hist")},
            "relative_strength": rs_features,
            "volatility": {k: _r(last[k]) for k in ("atr_pct", "hv", "adr_pct", "atr_pct_pctile", "hv_pctile", "vol_pctile")},
            "volume": vol_features,
            "gap": gap_features,
            "liquidity": {"avg_volume": _r(last["avg_volume"], 0), "avg_dollar_volume": _r(adv, 0), "spread": "UNAVAILABLE"},
            "event": {"note": event_note, **({k: str(v) for k, v in (earnings or {}).items()})},
        }
        out.ticker_regime = self._label(out)
        out.confidence = self._confidence(out)
        out.reasons = self._reasons(out, n)
        if len(d) < cfg["full_history_bars"]:
            out.warnings.append(f"SHORT_HISTORY: {len(d)} daily bars (< {cfg['full_history_bars']}); volatility "
                                f"percentiles use only this history and SMA200 is unavailable")
        return out

    def classify_history(self, ticker: str, daily: pd.DataFrame, benchmarks: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Per trading day, as known after that day's close (ticker_regime_history)."""
        cfg = self.cfg
        f = _trend_frame(daily, cfg)
        n = cfg["minimum_confirmation_period"]
        out = pd.DataFrame(index=f.index)
        out["ticker"] = ticker.upper()
        out["trend"] = ind.persist(f["trend"], n)
        out["momentum"] = f["momentum"]
        out["volatility"] = ind.persist(f["volatility"], n)
        rs_cols = []
        for b, bdf in benchmarks.items():
            aligned = bdf["close"].reindex(daily.index)
            ex = daily["close"].pct_change(20) - aligned.pct_change(20)
            out[f"rs20_vs_{b.lower()}"] = ex
            rs_cols.append(ex)
        avg = pd.concat(rs_cols, axis=1).mean(axis=1) if rs_cols else pd.Series(np.nan, index=daily.index)
        out["relative_strength"] = [None if np.isnan(v) else "STRONG_RELATIVE_STRENGTH" if v >= cfg["strong_rs_threshold"]
                                    else "WEAK_RELATIVE_STRENGTH" if v <= cfg["weak_rs_threshold"] else "NEUTRAL" for v in avg]
        out["volume"] = [_cut(v, cfg["rvol_levels"], RVOL_LABELS) for v in f["daily_rvol"]]
        out["gap"] = [_cut(abs(v), cfg["gap_levels"], GAP_LABELS) if not np.isnan(v) else None for v in f["gap_pct"]]
        out["ticker_regime"] = [self._label_from(m, v) if m and v else None for m, v in zip(out["momentum"], out["volatility"])]
        return out

    # -- components --------------------------------------------------------------
    def _relative_strength(self, d: pd.DataFrame, benchmarks: dict, ts) -> tuple[str | None, dict]:
        cfg = self.cfg
        feats, excess20 = {}, []
        for b in cfg["relative_strength_benchmarks"]:
            bdf = benchmarks.get(b)
            if bdf is None:
                feats[b] = "UNAVAILABLE"
                continue
            bd = daily_upto(bdf, ts)["close"]
            tc = d["close"]
            common = tc.index.intersection(bd.index)
            tc, bc = tc.reindex(common), bd.reindex(common)
            row = {}
            for w in cfg["relative_strength_windows"]:
                if len(common) > w:
                    tr = tc.iloc[-1] / tc.iloc[-1 - w] - 1
                    br = bc.iloc[-1] / bc.iloc[-1 - w] - 1
                    row[f"{w}d"] = {"ticker": _r(tr), "benchmark": _r(br), "excess": _r(tr - br)}
            feats[b] = row
            if "20d" in row:
                excess20.append(row["20d"]["excess"])
        if not excess20:
            return None, feats
        avg = float(np.mean(excess20))
        feats["avg_20d_excess"] = _r(avg)
        label = ("STRONG_RELATIVE_STRENGTH" if avg >= cfg["strong_rs_threshold"]
                 else "WEAK_RELATIVE_STRENGTH" if avg <= cfg["weak_rs_threshold"] else "NEUTRAL")
        return label, feats

    def _volume(self, d, f, ts, intraday, tf) -> dict:
        cfg = self.cfg
        today = ts.date()
        b = session_bounds(today)
        if intraday is not None and tf is not None and b is not None and ts > b.open:
            rth = intraday[intraday["session"] == Session.RTH.value]
            done = upto(rth, ts, tf.minutes)
            local = done.index.tz_convert(NY)
            elapsed = ts - b.open
            cutoff = (local - local.normalize()) < (pd.Timedelta(hours=9, minutes=30) + elapsed)
            by_day = done["volume"][cutoff].groupby(local[cutoff].date).sum()
            today_vol = by_day.get(today)
            prior = [v for day, v in by_day.items() if day < today][-cfg["rvol_lookback_days"]:]
            if today_vol is not None and len(prior) >= min(10, cfg["rvol_lookback_days"]) and np.mean(prior) > 0:
                rvol = today_vol / float(np.mean(prior))
                return {"method": "TIME_OF_DAY", "rvol": _r(rvol), "today_cum_volume": _r(today_vol, 0),
                        "avg_cum_volume_same_time": _r(float(np.mean(prior)), 0), "days_in_average": len(prior),
                        "label": _cut(rvol, cfg["rvol_levels"], RVOL_LABELS)}
        rvol = f["daily_rvol"].iloc[-1]
        return {"method": "PREVIOUS_SESSION_DAILY", "rvol": _r(rvol), "label": _cut(rvol, cfg["rvol_levels"], RVOL_LABELS),
                "note": "session not open yet or no intraday bars: last completed day vs its trailing average"}

    def _gap(self, d, ts, intraday, tf) -> dict:
        cfg = self.cfg
        prev_close = float(d["close"].iloc[-1])
        today = ts.date()
        b = session_bounds(today)
        if b is None or ts < b.open or intraday is None or tf is None:
            return {"label": None, "direction": None, "gap_pct": None,
                    "note": "regular session not open yet -- today's gap comes from the premarket regime"}
        rth = intraday[intraday["session"] == Session.RTH.value]
        done = upto(rth, ts, tf.minutes)
        todays = done[done.index.tz_convert(NY).date == today]
        if todays.empty:
            return {"label": None, "direction": None, "gap_pct": None, "note": "no completed regular-session bar yet today"}
        gap = float(todays["open"].iloc[0]) / prev_close - 1
        return {"label": _cut(abs(gap), cfg["gap_levels"], GAP_LABELS), "direction": "UP" if gap > 0 else "DOWN" if gap < 0 else "FLAT",
                "gap_pct": _r(gap), "open": _r(float(todays["open"].iloc[0])), "previous_close": _r(prev_close)}

    def _event(self, earnings: dict | None, today: dt.date) -> tuple[str, str]:
        if not earnings:
            return "UNKNOWN", "no event provider data -- UNKNOWN is not the same as no event"
        d = earnings.get("expected_report_date")
        if d is None:
            return "UNKNOWN", "provider returned no expected report date"
        if d == today:
            return "EARNINGS_TODAY", f"expected report date {d}"
        if d < today:
            return "UNKNOWN", f"last known report date {d} is in the past; next date not announced"
        days = len(trading_days(today, d)) - 1
        if days <= self.cfg["earnings_soon_days"]:
            return "EARNINGS_SOON", f"expected report date {d} ({days} trading days away)"
        return "NO_EARNINGS", f"next expected report date {d} ({days} trading days away)"

    # -- labels / confidence --------------------------------------------------------
    @staticmethod
    def _label_from(momentum: str, volatility: str) -> str:
        bucket = ("HIGH" if momentum in ("STRONG", "POSITIVE") else "NEGATIVE" if momentum in ("NEGATIVE", "VERY_NEGATIVE") else "NEUTRAL")
        return f"{bucket}_MOMENTUM_{volatility}_VOLATILITY"

    def _label(self, r: TickerRegime) -> str:
        return self._label_from(r.momentum, r.volatility)

    def _confidence(self, r: TickerRegime) -> int:
        up = r.trend in ("STRONG_UPTREND", "UPTREND")
        down = r.trend in ("STRONG_DOWNTREND", "DOWNTREND")
        t, m = r.features["trend"], r.features["momentum"]
        checks = [r.raw_trend == r.trend, r.raw_volatility == r.volatility]
        if up or down:
            sign = 1 if up else -1
            checks += [np.sign(t["price_vs_ema20"] or 0) == sign, np.sign(t["price_vs_ema50"] or 0) == sign,
                       np.sign(t["ema20_slope"] or 0) == sign, np.sign(m["roc"] or 0) == sign,
                       np.sign((m["rsi"] or 50) - 50) == sign, np.sign(m["macd_hist"] or 0) == sign]
            if r.relative_strength:
                checks.append(r.relative_strength == ("STRONG_RELATIVE_STRENGTH" if up else "WEAK_RELATIVE_STRENGTH")
                              or r.relative_strength == "NEUTRAL")
        else:
            checks += [abs(t["ema20_slope"] or 0) < self.cfg["strong_trend_slope"], r.momentum == "NEUTRAL"]
        v = r.features["volatility"]
        cuts = self.cfg["volatility_percentiles"]
        for key in ("atr_pct_pctile", "hv_pctile"):
            if v.get(key) is not None:
                checks.append(ind.classify_percentile(v[key], cuts, VOL_LABELS) == r.volatility)
        return int(round(100 * sum(bool(c) for c in checks) / len(checks)))

    def _reasons(self, r: TickerRegime, n: int) -> list[str]:
        t, m, v = r.features["trend"], r.features["momentum"], r.features["volatility"]
        out = [f"trend: close {t['close']} vs EMA20 {t['ema20']} / EMA50 {t['ema50']}, EMA20 slope {t['ema20_slope']} -> {r.raw_trend}",
               f"momentum: ROC {m['roc']}, RSI {m['rsi']}, MACD hist {m['macd_hist']} -> {r.momentum}",
               f"relative strength (avg 20d excess vs {self.cfg['relative_strength_benchmarks']}): "
               f"{r.features['relative_strength'].get('avg_20d_excess')} -> {r.relative_strength}",
               f"volatility vs own history: ATR% pctile {v['atr_pct_pctile']}, HV pctile {v['hv_pctile']} -> {r.raw_volatility}",
               f"volume: {r.features['volume']['method']} RVOL {r.features['volume']['rvol']} -> {r.volume}",
               f"gap: {r.features['gap'].get('gap_pct')} -> {r.gap}" + (f" ({r.features['gap'].get('note')})" if r.features['gap'].get('note') else ""),
               f"liquidity: avg $ volume {r.features['liquidity']['avg_dollar_volume']} -> {r.liquidity}",
               f"event: {r.event_status} ({r.features['event']['note']})"]
        if r.raw_trend != r.trend:
            out.append(f"trend kept at {r.trend}: raw {r.raw_trend} not yet confirmed for {n} days")
        if r.raw_volatility != r.volatility:
            out.append(f"volatility kept at {r.volatility}: raw {r.raw_volatility} not yet confirmed for {n} days")
        return out


def _as_ny(ts) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_localize(NY) if t.tzinfo is None else t.tz_convert(NY)


def _r(v, nd: int = 4):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) else round(f, nd)
