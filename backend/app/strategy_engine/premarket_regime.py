"""
Premarket Regime Detector (spec sections 19A-19J).

Uses ONLY bars tagged PREMARKET (04:00-09:30 ET), and only those completed
before the decision timestamp:
  decision 08:45 -> premarket bars up to 08:45
  decision 10:00 -> premarket frozen at 09:30 (the whole session)
Premarket bars never feed RTH indicators and vice versa.

Premarket trading is thin: missing minutes are normal (never forward-filled)
and a THIN premarket is reported as PREMARKET_UNRELIABLE rather than trusted.
With no premarket data at all the status is PREMARKET_DATA_UNAVAILABLE --
nothing is fabricated from regular-session bars.

Premarket volume is compared at the SAME time of day on prior sessions
(08:45 today vs 08:45 on earlier days), never against a whole-session or
whole-day average.

Categories: the spec's initial list, completed symmetrically so that e.g. a
normal gap-up on heavy volume isn't forced into a "low participation" label:
  {STRONG_GAP_UP, GAP_UP, STRONG_GAP_DOWN, GAP_DOWN}_{HIGH,LOW}_PARTICIPATION,
  FLAT_ACTIVE, FLAT_QUIET, PREMARKET_UNRELIABLE, PREMARKET_DATA_UNAVAILABLE.

`confidence` = agreement of the premarket features with the label; NOT a
probability of any future move.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from app.strategy_engine.data.calendar import NY, previous_trading_day, session_bounds
from app.strategy_engine.models import Session, Timeframe
from app.strategy_engine.thresholds import MARKET_REGIME_CONFIG, PREMARKET_CONFIG

AVAILABLE = "AVAILABLE"
UNAVAILABLE = "PREMARKET_DATA_UNAVAILABLE"
UNRELIABLE = "PREMARKET_UNRELIABLE"
VOLUME_LABELS = ["LOW_PREMARKET_VOLUME", "NORMAL_PREMARKET_VOLUME", "HIGH_PREMARKET_VOLUME", "EXTREME_PREMARKET_VOLUME"]


@dataclass
class PremarketRegime:
    ticker: str
    status: str
    decision_ts: str | None = None
    premarket_data_through: str | None = None
    session_date: str | None = None
    market_premarket: str = "NOT_EVALUATED"
    direction: str | None = None
    change_pct: float | None = None
    structure: str | None = None
    volume: str | None = None
    premarket_rvol: float | None = None
    liquidity: str | None = None
    reliability: str | None = None
    catalyst: str = "UNKNOWN"
    premarket_regime: str = UNAVAILABLE
    confidence: int | None = None
    features: dict = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _hm(s: str) -> dt.time:
    h, m = (int(x) for x in s.split(":"))
    return dt.time(h, m)


def _as_ny(ts) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_localize(NY) if t.tzinfo is None else t.tz_convert(NY)


def _session_premarket(bars: pd.DataFrame, day: dt.date, cutoff: pd.Timestamp, bar_minutes: int) -> pd.DataFrame:
    """PREMARKET bars of `day` that completed by `cutoff`."""
    pm = bars[bars["session"] == Session.PREMARKET.value]
    local = pm.index.tz_convert(NY)
    same_day = local.date == day
    complete = (pm.index + pd.Timedelta(minutes=bar_minutes)) <= cutoff.tz_convert("UTC")
    return pm[same_day & complete]


def _cum_volume_same_time(bars: pd.DataFrame, days: list[dt.date], clock: dt.time, bar_minutes: int) -> list[float]:
    """Premarket volume accumulated by `clock` on each of `days` (days with no
    premarket bars at all are skipped -- they are missing data, not zero)."""
    out = []
    for d in days:
        cutoff = pd.Timestamp(dt.datetime.combine(d, clock), tz=NY)
        sub = _session_premarket(bars, d, cutoff, bar_minutes)
        if len(sub):
            out.append(float(sub["volume"].sum()))
    return out


def _percentile_of(value: float, history: list[float]) -> float | None:
    h = np.asarray(history, dtype=float)
    if len(h) < 5:
        return None
    return float((h < value).sum() + 0.5 * (h == value).sum()) / len(h)


class PremarketRegimeDetector:
    def __init__(self, config: dict | None = None):
        self.cfg = {**PREMARKET_CONFIG, **(config or {})}

    def detect(self, ticker: str, bars: pd.DataFrame, bar_timeframe: Timeframe, decision_ts: pd.Timestamp,
               previous_close: float | None = None, previous_day: dict | None = None,
               earnings: dict | None = None, market: dict[str, pd.DataFrame] | None = None,
               market_previous_close: dict[str, float] | None = None) -> PremarketRegime:
        """
        bars              normalized intraday bars of the ticker (must include PREMARKET-tagged bars)
        previous_close    previous regular-session close (required for gap %)
        previous_day      optional {"high":..., "low":...} of the previous session
        earnings          optional {"expected_report_date": date, "time_of_day": "BMO"/"AMC"/...}
        market            optional intraday bars for SPY/QQQ/IWM (market premarket context)
        """
        cfg = self.cfg
        ts = _as_ny(decision_ts)
        out = PremarketRegime(ticker=ticker.upper(), status=UNAVAILABLE, decision_ts=ts.isoformat())
        day = ts.date()
        b = session_bounds(day)
        if b is None:
            out.reasons = [f"{day} is not a trading day"]
            return out
        start = pd.Timestamp(dt.datetime.combine(day, _hm(cfg["session_start"])), tz=NY)
        end = pd.Timestamp(dt.datetime.combine(day, _hm(cfg["session_end"])), tz=NY)
        cutoff = min(ts, end)
        out.session_date = str(day)
        if ts <= start:
            out.reasons = ["premarket session has not started yet"]
            return out
        tfm = bar_timeframe.minutes
        # Whether the source carries extended hours is judged only from bars
        # that existed at the decision time -- coverage that begins later
        # (e.g. a provider's limited intraday history) must not leak back.
        has_any_pm = bars is not None and not bars.empty and (
            (bars["session"] == Session.PREMARKET.value) & (bars.index < cutoff)).any()
        if not has_any_pm:
            out.reasons = ["the data source supplied no premarket bars (extended hours unavailable)"]
            return out
        pm = _session_premarket(bars, day, cutoff, tfm)
        if pm.empty:
            out.status, out.premarket_regime = UNRELIABLE, UNRELIABLE
            out.liquidity, out.reliability, out.volume = "THIN", "LOW", "INACTIVE"
            out.premarket_data_through = str(cutoff)
            out.reasons = ["no premarket trades so far today"]
            out.catalyst, _ = self._catalyst(earnings, day)
            return out
        if previous_close is None:
            out.reasons = ["previous regular-session close unknown -- cannot measure the premarket gap"]
            return out

        last_bar_end = pm.index[-1] + pd.Timedelta(minutes=tfm)
        out.premarket_data_through = str(last_bar_end.tz_convert(NY))
        o, h, l, c = float(pm["open"].iloc[0]), float(pm["high"].max()), float(pm["low"].min()), float(pm["close"].iloc[-1])
        vol = float(pm["volume"].sum())
        typical = (pm["high"] + pm["low"] + pm["close"]) / 3
        vwap = float((typical * pm["volume"]).sum() / vol) if vol > 0 else c
        change = c / previous_close - 1
        rng = h - l
        position = (c - l) / rng if rng > 0 else 0.5
        expected_bars = max(1, int((cutoff - start).total_seconds() // 60 // tfm))
        non_empty = int((pm["volume"] > 0).sum())
        non_empty_ratio = non_empty / expected_bars
        dollar_volume = float((pm["close"] * pm["volume"]).sum())

        # --- volume vs the same time of day on prior sessions ------------------
        clock = cutoff.time()
        prior_days = [d for d in sorted(set(bars.index.tz_convert(NY).date)) if d < day][-cfg["rvol_lookback_days"]:]
        hist_vol = _cum_volume_same_time(bars, prior_days, clock, tfm)
        rvol = vol / float(np.mean(hist_vol)) if hist_vol and np.mean(hist_vol) > 0 else None
        vol_pct = _percentile_of(vol, hist_vol)
        if vol == 0:
            vol_label = "INACTIVE"
        elif vol_pct is not None:
            vol_label = _cut(vol_pct, cfg["rvol_percentile_thresholds"], VOLUME_LABELS)
        elif rvol is not None:
            vol_label = _cut(rvol, [0.7, 1.5, 3.0], VOLUME_LABELS)
        else:
            vol_label = "NORMAL_PREMARKET_VOLUME"

        # --- gap size vs the ticker's own premarket-gap history ----------------
        hist_moves = []
        for d in prior_days:
            sub = _session_premarket(bars, d, pd.Timestamp(dt.datetime.combine(d, clock), tz=NY), tfm)
            prev = _prev_close_from_bars(bars, d)
            if len(sub) and prev:
                hist_moves.append(abs(float(sub["close"].iloc[-1]) / prev - 1))
        move_pct = _percentile_of(abs(change), hist_moves)
        cuts = cfg["gap_percentile_thresholds"]
        if move_pct is not None:
            size = "STRONG" if move_pct >= cuts[2] else "GAP" if move_pct >= cuts[1] else "FLAT"
            if abs(change) < cfg["market_gap_confirm_pct"]:
                size = "FLAT"                      # tiny moves are flat however quiet the history is
        else:
            size = ("STRONG" if abs(change) >= cfg["strong_gap_pct"] else "GAP" if abs(change) >= cfg["gap_pct"] else "FLAT")
        sign = "UP" if change > 0 else "DOWN"
        direction = "FLAT" if size == "FLAT" else f"{'STRONG_' if size == 'STRONG' else ''}GAP_{sign}"

        # --- structure ---------------------------------------------------------
        hh, hl = cfg["holding_highs_position"], cfg["holding_lows_position"]
        above_vwap = c >= vwap
        if direction.endswith("GAP_UP"):
            structure = "HOLDING_HIGHS" if (position >= hh and above_vwap) else "FADING" if (position <= hl or not above_vwap) else "RANGE_BOUND"
        elif direction.endswith("GAP_DOWN"):
            structure = "HOLDING_LOWS" if (position <= hl and not above_vwap) else "RECOVERING" if (position >= hh or above_vwap) else "RANGE_BOUND"
        else:
            structure = "HOLDING_HIGHS" if (position >= hh and above_vwap) else "HOLDING_LOWS" if (position <= hl and not above_vwap) else "RANGE_BOUND"

        # --- liquidity / reliability ------------------------------------------
        thin = non_empty_ratio < cfg["min_non_empty_bar_ratio"] or dollar_volume < cfg["min_premarket_dollar_volume"]
        active = non_empty_ratio >= 0.7 and dollar_volume >= 5 * cfg["min_premarket_dollar_volume"]
        liquidity = "THIN" if thin else "ACTIVE" if active else "ADEQUATE"
        reliability = "LOW" if thin else "HIGH"

        gap_fill = None
        if change > 0:
            gap_fill = "FILLED" if l <= previous_close else "OPEN"
        elif change < 0:
            gap_fill = "FILLED" if h >= previous_close else "OPEN"

        out.status = AVAILABLE if not thin else UNRELIABLE
        out.direction, out.change_pct, out.structure = direction, _r(change), structure
        out.volume, out.premarket_rvol = vol_label, _r(rvol)
        out.liquidity, out.reliability = liquidity, reliability
        out.catalyst, catalyst_note = self._catalyst(earnings, day)
        if thin:
            out.premarket_regime = UNRELIABLE
        elif direction == "FLAT":
            out.premarket_regime = "FLAT_ACTIVE" if vol_label in ("HIGH_PREMARKET_VOLUME", "EXTREME_PREMARKET_VOLUME") else "FLAT_QUIET"
        else:
            high = vol_label in ("HIGH_PREMARKET_VOLUME", "EXTREME_PREMARKET_VOLUME")
            out.premarket_regime = f"{direction}_{'HIGH' if high else 'LOW'}_PARTICIPATION"

        out.features = {
            "previous_close": _r(previous_close), "premarket_open": _r(o), "premarket_high": _r(h), "premarket_low": _r(l),
            "premarket_last": _r(c), "premarket_change_pct": _r(change), "premarket_range_pct": _r(rng / previous_close),
            "premarket_vwap": _r(vwap), "price_vs_premarket_vwap": _r(c / vwap - 1) if vwap else None,
            "position_in_premarket_range": _r(position),
            "premarket_high_vs_previous_day_high": _r(h / previous_day["high"] - 1) if previous_day else None,
            "premarket_low_vs_previous_day_low": _r(l / previous_day["low"] - 1) if previous_day else None,
            "gap_fill_status": gap_fill,
            "premarket_volume": _r(vol, 0), "premarket_dollar_volume": _r(dollar_volume, 0),
            "non_empty_bars": non_empty, "expected_bars": expected_bars, "non_empty_bar_ratio": _r(non_empty_ratio),
            "premarket_rvol": _r(rvol), "volume_percentile_same_time": _r(vol_pct),
            "history_days_for_volume": len(hist_vol), "gap_percentile": _r(move_pct), "history_days_for_gap": len(hist_moves),
            "catalyst_note": catalyst_note,
        }
        if market is not None:
            out.market_premarket, out.features["market"] = self.market_premarket(market, ts, market_previous_close or {}, tfm)
        out.confidence = self._confidence(out)
        out.reasons = self._reasons(out)
        return out

    # -- market ------------------------------------------------------------------
    def market_premarket(self, market: dict[str, pd.DataFrame], decision_ts, previous_close: dict[str, float],
                         bar_minutes: int) -> tuple[str, dict]:
        cfg = self.cfg
        ts = _as_ny(decision_ts)
        day = ts.date()
        cutoff = min(ts, pd.Timestamp(dt.datetime.combine(day, _hm(cfg["session_end"])), tz=NY))
        changes = {}
        for sym in MARKET_REGIME_CONFIG["reference_symbols"]:
            df = market.get(sym)
            prev = previous_close.get(sym) if previous_close else None
            if df is None or prev is None:
                continue
            pm = _session_premarket(df, day, cutoff, bar_minutes)
            if len(pm):
                changes[sym] = _r(float(pm["close"].iloc[-1]) / prev - 1)
        need = MARKET_REGIME_CONFIG["direction_symbols"]
        if not all(s in changes for s in need):
            return "UNAVAILABLE", changes
        th = cfg["market_gap_confirm_pct"]
        vals = [changes[s] for s in need]
        if all(v > th for v in vals):
            return "GAP_UP_CONFIRMED", changes
        if all(v < -th for v in vals):
            return "GAP_DOWN_CONFIRMED", changes
        if all(abs(v) <= th for v in vals):
            return "FLAT", changes
        return "MIXED", changes

    # -- helpers -----------------------------------------------------------------
    @staticmethod
    def _catalyst(earnings: dict | None, day: dt.date) -> tuple[str, str]:
        if not earnings or not earnings.get("expected_report_date"):
            return "UNKNOWN", "no event/news provider data for this date -- UNKNOWN is not NO_CATALYST"
        d, when = earnings["expected_report_date"], str(earnings.get("time_of_day") or "").upper()
        if d == day and when in ("BMO", "BEFORE_OPEN", "PRE_MARKET"):
            return "EARNINGS_BEFORE_OPEN", f"earnings {d} {when}"
        if d == previous_trading_day(day) and when in ("AMC", "AFTER_CLOSE", "POST_MARKET"):
            return "EARNINGS_AFTER_CLOSE_PREVIOUS_DAY", f"earnings {d} {when}"
        if d in (day, previous_trading_day(day)):
            return "UNKNOWN", f"earnings {d} but the report time ({when or 'not given'}) doesn't place it before this premarket"
        return "UNKNOWN", "no earnings around this premarket; news is not covered by any provider"

    def _confidence(self, r: PremarketRegime) -> int:
        f = r.features
        checks = [r.reliability == "HIGH"]
        if r.direction and r.direction != "FLAT":
            up = r.direction.endswith("UP")
            checks += [(f["price_vs_premarket_vwap"] or 0) >= 0 if up else (f["price_vs_premarket_vwap"] or 0) <= 0,
                       r.structure in (("HOLDING_HIGHS",) if up else ("HOLDING_LOWS",)),
                       f["gap_fill_status"] == "OPEN",
                       r.premarket_regime.endswith("HIGH_PARTICIPATION")]
            if r.market_premarket in ("GAP_UP_CONFIRMED", "GAP_DOWN_CONFIRMED"):
                checks.append((r.market_premarket == "GAP_UP_CONFIRMED") == up)
        else:
            checks += [r.structure == "RANGE_BOUND", abs(f["premarket_change_pct"] or 0) < self.cfg["gap_pct"]]
        if f.get("history_days_for_volume", 0) < 10:
            checks.append(False)   # thin history for time-of-day comparison
        return int(round(100 * sum(bool(c) for c in checks) / len(checks)))

    @staticmethod
    def _reasons(r: PremarketRegime) -> list[str]:
        f = r.features
        return [
            f"premarket data through {r.premarket_data_through}",
            f"change vs previous close {f['previous_close']}: {f['premarket_change_pct']} "
            f"(own-history percentile {f['gap_percentile']} over {f['history_days_for_gap']} days) -> {r.direction}",
            f"last {f['premarket_last']} vs premarket VWAP {f['premarket_vwap']}, position in range {f['position_in_premarket_range']} -> {r.structure}",
            f"volume {f['premarket_volume']} vs same time on {f['history_days_for_volume']} prior sessions: RVOL {f['premarket_rvol']}, "
            f"percentile {f['volume_percentile_same_time']} -> {r.volume}",
            f"liquidity: {f['non_empty_bars']}/{f['expected_bars']} bars traded, ${f['premarket_dollar_volume']} -> {r.liquidity} (reliability {r.reliability})",
            f"catalyst: {r.catalyst} ({f['catalyst_note']})",
            f"market premarket: {r.market_premarket}",
        ]


def _prev_close_from_bars(bars: pd.DataFrame, day: dt.date) -> float | None:
    rth = bars[bars["session"] == Session.RTH.value]
    prev = previous_trading_day(day)
    sub = rth[rth.index.tz_convert(NY).date == prev]
    return float(sub["close"].iloc[-1]) if len(sub) else None


def _cut(value, levels, labels):
    for lvl, lab in zip(levels, labels):
        if value < lvl:
            return lab
    return labels[-1]


def _r(v, nd: int = 4):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) else round(f, nd)
