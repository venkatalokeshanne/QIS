"""
Market Regime Detector (spec sections 5-12).

Classifies the broad US equity market from SPY and QQQ (direction), IWM
(confirmation) and optionally VIX (volatility), using ONLY daily bars whose
session had closed before the decision timestamp.

Rules (all thresholds in thresholds.MARKET_REGIME_CONFIG):
  per symbol  BULLISH  close > EMA20 and EMA20 > EMA50 and structure BULLISH
              BEARISH  close < EMA20 and EMA20 < EMA50 and structure BEARISH
              NEUTRAL  otherwise
  market      BULLISH/BEARISH when every direction symbol agrees, else NEUTRAL
  strength    ADX(14) of SPY: >= strong -> STRONG, >= trend -> MODERATE, else WEAK
  volatility  percentile of SPY ATR% and 20-day realized vol within their own
              trailing history (and VIX if supplied), averaged, then cut into
              LOW / NORMAL / HIGH / EXTREME
  persistence direction and volatility each change only after N consecutive
              confirming days

`confidence` is how strongly the available indicators AGREE with the
classification (0-100). It is NOT a probability of any future move.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from app.strategy_engine import indicators as ind
from app.strategy_engine.data.normalize import daily_upto
from app.strategy_engine.thresholds import MARKET_REGIME_CONFIG
from app.strategy_engine.validators import DATA_INSUFFICIENT, OK, check_bars
from app.strategy_engine.models import Timeframe

VOL_LABELS = ["LOW", "NORMAL", "HIGH", "EXTREME"]


@dataclass
class MarketRegime:
    status: str
    as_of: str | None = None                  # last daily bar used (trading date)
    direction: str | None = None
    trend_strength: str | None = None
    volatility: str | None = None
    breadth: str = "UNAVAILABLE"
    market_premarket: str = "NOT_EVALUATED"   # filled by the premarket detector
    market_regime: str | None = None
    confidence: int | None = None
    raw_direction: str | None = None          # before persistence
    raw_volatility: str | None = None
    symbols: dict = field(default_factory=dict)
    volatility_inputs: dict = field(default_factory=dict)
    breadth_inputs: dict = field(default_factory=dict)
    data_quality: list = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _symbol_frame(daily: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    c = daily["close"]
    f = pd.DataFrame(index=daily.index)
    f["close"] = c
    f["ema_fast"] = ind.ema(c, cfg["ema_fast"])
    f["ema_slow"] = ind.ema(c, cfg["ema_slow"])
    f["sma_mid"] = ind.sma(c, cfg["sma_mid"])
    f["sma_long"] = ind.sma(c, cfg["sma_long"])
    f["adx"] = ind.adx(daily, cfg["adx_period"])
    f["structure"] = ind.structure_series(daily, cfg["swing_lookback"], cfg["structure_swings"])
    bull = (c > f["ema_fast"]) & (f["ema_fast"] > f["ema_slow"]) & (f["structure"] == "BULLISH")
    bear = (c < f["ema_fast"]) & (f["ema_fast"] < f["ema_slow"]) & (f["structure"] == "BEARISH")
    ready = f["ema_slow"].notna() & f["structure"].notna()
    f["direction"] = np.where(~ready, None, np.where(bull, "BULLISH", np.where(bear, "BEARISH", "NEUTRAL")))
    return f


def _combine_direction(rows: list[str | None]) -> str | None:
    if any(r is None for r in rows):
        return None
    if all(r == "BULLISH" for r in rows):
        return "BULLISH"
    if all(r == "BEARISH" for r in rows):
        return "BEARISH"
    return "NEUTRAL"


class MarketRegimeDetector:
    def __init__(self, config: dict | None = None):
        self.cfg = {**MARKET_REGIME_CONFIG, **(config or {})}

    def detect(self, daily: dict[str, pd.DataFrame], decision_ts: pd.Timestamp,
               vix: pd.DataFrame | None = None, breadth: dict | None = None) -> MarketRegime:
        """`daily`: normalized daily frames for SPY/QQQ/IWM (keys = symbols).
        Only bars closed before `decision_ts` are used."""
        cfg = self.cfg
        frames, quality = {}, []
        for sym in cfg["reference_symbols"]:
            df = daily.get(sym)
            if df is None:
                quality.append(f"{sym}: no data")
                continue
            df = daily_upto(df, decision_ts)
            rep = check_bars(df, sym, Timeframe.D1)
            quality.append(rep.to_dict())
            if rep.status != OK:
                continue
            frames[sym] = df
        missing = [s for s in cfg["direction_symbols"] if s not in frames]
        if missing:
            return MarketRegime(status=DATA_INSUFFICIENT, data_quality=quality,
                                reasons=[f"insufficient data for {', '.join(missing)}"])

        per = {s: _symbol_frame(df, cfg) for s, df in frames.items()}
        # Align on the common trading days of the direction symbols.
        common = per[cfg["direction_symbols"][0]].index
        for s in cfg["direction_symbols"][1:]:
            common = common.intersection(per[s].index)
        raw_dir = pd.Series([_combine_direction([per[s].loc[t, "direction"] for s in cfg["direction_symbols"]])
                             for t in common], index=common, dtype=object)

        vol_frame = self._volatility_frame(frames[cfg["direction_symbols"][0]], vix, decision_ts)
        vol_frame = vol_frame.reindex(common)
        raw_vol = vol_frame["label"]

        n = cfg["minimum_confirmation_period"]
        direction = ind.persist(raw_dir, n)
        volatility = ind.persist(raw_vol, n)
        t = common[-1]
        if direction.iloc[-1] is None or volatility.iloc[-1] is None:
            return MarketRegime(status=DATA_INSUFFICIENT, data_quality=quality,
                                reasons=["not enough history for moving averages / swing structure / volatility percentiles"])

        lead = per[cfg["direction_symbols"][0]]
        adx_v = float(lead.loc[t, "adx"])
        strength = ("STRONG" if adx_v >= cfg["strong_adx_threshold"]
                    else "MODERATE" if adx_v >= cfg["trend_adx_threshold"] else "WEAK")

        symbols_out = {}
        for s, f in per.items():
            if t not in f.index:
                continue
            row = f.loc[t]
            symbols_out[s] = {
                "direction": row["direction"], "close": round(float(row["close"]), 4),
                "ema20": _r(row["ema_fast"]), "ema50": _r(row["ema_slow"]), "sma50": _r(row["sma_mid"]),
                "sma200": _r(row["sma_long"]), "adx": _r(row["adx"]), "structure": row["structure"],
                "close_above_ema20": bool(row["close"] > row["ema_fast"]),
                "ema20_above_ema50": bool(row["ema_fast"] > row["ema_slow"]),
                "close_above_sma200": bool(row["close"] > row["sma_long"]) if not np.isnan(row["sma_long"]) else None,
            }

        dir_v, vol_v = direction.iloc[-1], volatility.iloc[-1]
        breadth_status, breadth_inputs = self._breadth(breadth)
        regime = MarketRegime(
            status=OK, as_of=str(t.tz_convert("America/New_York").date()),
            direction=dir_v, trend_strength=strength, volatility=vol_v,
            breadth=breadth_status, breadth_inputs=breadth_inputs,
            market_regime=f"{dir_v}_{vol_v}_VOLATILITY",
            raw_direction=raw_dir.iloc[-1], raw_volatility=raw_vol.iloc[-1],
            symbols=symbols_out,
            volatility_inputs={k: _r(v) for k, v in vol_frame.iloc[-1].items() if k != "label"} | {"label": vol_frame.iloc[-1]["label"]},
            data_quality=quality,
        )
        regime.confidence = self._confidence(regime)
        regime.reasons = self._reasons(regime, raw_dir, raw_vol)
        return regime

    def classify_history(self, daily: dict[str, pd.DataFrame], vix: pd.DataFrame | None = None) -> pd.DataFrame:
        """Persisted regime for EVERY trading day (as known after that day's
        close) -- for market_regime_history. Row t uses bars <= t only."""
        cfg = self.cfg
        per = {s: _symbol_frame(daily[s], cfg) for s in cfg["reference_symbols"] if s in daily}
        common = per[cfg["direction_symbols"][0]].index
        for s in cfg["direction_symbols"][1:]:
            common = common.intersection(per[s].index)
        raw_dir = pd.Series([_combine_direction([per[s].loc[t, "direction"] for s in cfg["direction_symbols"]])
                             for t in common], index=common, dtype=object)
        vol = self._volatility_frame(daily[cfg["direction_symbols"][0]], vix, None).reindex(common)
        n = cfg["minimum_confirmation_period"]
        out = pd.DataFrame(index=common)
        for s in ("SPY", "QQQ", "IWM"):
            out[f"{s.lower()}_direction"] = per[s]["direction"].reindex(common) if s in per else None
        out["market_direction"] = ind.persist(raw_dir, n)
        out["market_volatility"] = ind.persist(vol["label"], n)
        out["breadth"] = "UNAVAILABLE"
        out["market_regime"] = [f"{d}_{v}_VOLATILITY" if d and v else None
                                for d, v in zip(out["market_direction"], out["market_volatility"])]
        return out

    # -- helpers ---------------------------------------------------------------
    def _volatility_frame(self, lead: pd.DataFrame, vix: pd.DataFrame | None, decision_ts) -> pd.DataFrame:
        cfg = self.cfg
        w = cfg["volatility_history_bars"]
        f = pd.DataFrame(index=lead.index)
        f["atr_pct"] = ind.atr(lead, cfg["atr_period"]) / lead["close"]
        f["hv"] = ind.realized_vol(lead["close"], cfg["hv_period"])
        f["atr_pct_pctile"] = ind.trailing_percentile(f["atr_pct"], w)
        f["hv_pctile"] = ind.trailing_percentile(f["hv"], w)
        cols = ["atr_pct_pctile", "hv_pctile"]
        if vix is not None and not vix.empty:
            v = vix if decision_ts is None else daily_upto(vix, decision_ts)
            v = v["close"].copy()
            v.index = v.index.tz_convert("America/New_York").normalize().tz_convert("UTC")
            aligned = v.reindex(f.index.tz_convert("America/New_York").normalize().tz_convert("UTC"))
            f["vix"] = aligned.to_numpy()
            f["vix_pctile"] = ind.trailing_percentile(f["vix"], w)
            cols.append("vix_pctile")
        f["combined_pctile"] = f[cols].mean(axis=1, skipna=False) if "vix_pctile" not in cols else f[cols].mean(axis=1)
        f["label"] = [ind.classify_percentile(p, cfg["volatility_percentiles"], VOL_LABELS) for p in f["combined_pctile"]]
        return f

    @staticmethod
    def _breadth(breadth: dict | None) -> tuple[str, dict]:
        if not breadth:
            return "UNAVAILABLE", {}
        pct50 = breadth.get("percentage_above_50dma")
        adr = breadth.get("advance_decline_ratio")
        if pct50 is None and adr is None:
            return "UNAVAILABLE", breadth
        positive = (pct50 is None or pct50 >= 0.5) and (adr is None or adr >= 1.0)
        negative = (pct50 is None or pct50 < 0.5) and (adr is None or adr < 1.0)
        return ("POSITIVE" if positive else "NEGATIVE" if negative else "MIXED"), breadth

    def _confidence(self, r: MarketRegime) -> int:
        """Share of individual checks that agree with the final direction and
        volatility class. Agreement, not probability."""
        checks = []
        want_up = r.direction == "BULLISH"
        want_down = r.direction == "BEARISH"
        for s, v in r.symbols.items():
            if r.direction == "NEUTRAL":
                checks.append(v["direction"] == "NEUTRAL")
                continue
            checks += [v["close_above_ema20"] == want_up, v["ema20_above_ema50"] == want_up,
                       v["structure"] == ("BULLISH" if want_up else "BEARISH")]
            if v["close_above_sma200"] is not None:
                checks.append(v["close_above_sma200"] == want_up or (want_down and not v["close_above_sma200"]))
        vi = r.volatility_inputs
        cuts = self.cfg["volatility_percentiles"]
        for key in ("atr_pct_pctile", "hv_pctile", "vix_pctile"):
            if vi.get(key) is not None:
                checks.append(ind.classify_percentile(vi[key], cuts, VOL_LABELS) == r.volatility)
        checks.append(r.raw_direction == r.direction)
        if r.breadth in ("POSITIVE", "NEGATIVE") and r.direction in ("BULLISH", "BEARISH"):
            checks.append((r.breadth == "POSITIVE") == want_up)
        return int(round(100 * sum(checks) / len(checks))) if checks else 0

    def _reasons(self, r: MarketRegime, raw_dir: pd.Series, raw_vol: pd.Series) -> list[str]:
        out = []
        for s, v in r.symbols.items():
            out.append(f"{s}: close {v['close']} vs EMA20 {v['ema20']} / EMA50 {v['ema50']}, structure {v['structure']}, "
                       f"ADX {v['adx']} -> {v['direction']}")
        out.append(f"direction symbols {self.cfg['direction_symbols']} -> {r.raw_direction} (raw)")
        vi = r.volatility_inputs
        out.append(f"volatility percentiles: ATR% {vi.get('atr_pct_pctile')}, realized vol {vi.get('hv_pctile')}"
                   + (f", VIX {vi.get('vix_pctile')}" if vi.get("vix_pctile") is not None else ", VIX not supplied")
                   + f" -> {r.raw_volatility} (raw)")
        n = self.cfg["minimum_confirmation_period"]
        if r.raw_direction != r.direction:
            out.append(f"direction kept at {r.direction}: raw {r.raw_direction} not yet confirmed for {n} days")
        if r.raw_volatility != r.volatility:
            out.append(f"volatility kept at {r.volatility}: raw {r.raw_volatility} not yet confirmed for {n} days")
        out.append(f"breadth: {r.breadth}")
        return out


def _r(v, nd: int = 4):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) else round(f, nd)
