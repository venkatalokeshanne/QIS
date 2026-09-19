"""Step 2: normalization, session tagging, no-look-ahead slicing, bar store, data quality."""

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from app.strategy_engine.data.normalize import daily_upto, normalize_bars, select_session, upto
from app.strategy_engine.data.store import BarStore, data_version
from app.strategy_engine.models import Session, Timeframe
from app.strategy_engine.validators import DATA_INSUFFICIENT, OK, check_bars


def intraday_raw(day="2026-03-10", start="04:00", end="20:00", freq="5min", tz=None):
    idx = pd.date_range(f"{day} {start}", f"{day} {end}", freq=freq, inclusive="left")
    if tz:
        idx = idx.tz_localize(tz)
    n = len(idx)
    close = 100 + np.arange(n) * 0.01
    return pd.DataFrame({"date": idx, "open": close, "high": close + 0.05, "low": close - 0.05, "close": close,
                         "volume": 1000.0})


def test_naive_exchange_times_become_utc_and_follow_dst():
    winter, _ = normalize_bars(intraday_raw("2026-03-06"), Timeframe.M5)   # before DST switch (EST)
    summer, _ = normalize_bars(intraday_raw("2026-03-10"), Timeframe.M5)   # after (EDT)
    assert str(winter.index.tz) == "UTC"
    first_rth_w = select_session(winter, Session.RTH).index[0]
    first_rth_s = select_session(summer, Session.RTH).index[0]
    assert (first_rth_w.hour, first_rth_w.minute) == (14, 30)
    assert (first_rth_s.hour, first_rth_s.minute) == (13, 30)


def test_sessions_are_tagged_and_overnight_is_dropped():
    raw = intraday_raw("2026-03-10", "00:00", "23:55")
    df, rep = normalize_bars(raw, Timeframe.M5)
    counts = df["session"].value_counts()
    assert counts[Session.PREMARKET.value] == 66   # 04:00-09:30
    assert counts[Session.RTH.value] == 78         # 09:30-16:00
    assert counts[Session.AFTER_HOURS.value] == 48  # 16:00-20:00
    assert rep.outside_session_dropped == len(raw) - 66 - 78 - 48


def test_early_close_day_boundaries():
    df, _ = normalize_bars(intraday_raw("2025-11-28"), Timeframe.M5)
    rth = select_session(df, Session.RTH)
    assert len(rth) == 42                          # 09:30-13:00
    assert len(select_session(df, Session.AFTER_HOURS)) == 48  # 13:00-17:00


def test_holiday_bars_and_duplicates_are_dropped():
    raw = pd.concat([intraday_raw("2026-03-10"), intraday_raw("2026-03-10").iloc[:3], intraday_raw("2025-12-25")])
    df, rep = normalize_bars(raw, Timeframe.M5)
    assert rep.duplicates_dropped == 3
    assert rep.closed_day_dropped == len(intraday_raw("2025-12-25"))
    assert df.index.is_unique


def test_invalid_ohlc_rows_are_dropped():
    raw = intraday_raw("2026-03-10")
    raw.loc[5, "high"] = raw.loc[5, "low"] - 1
    _, rep = normalize_bars(raw, Timeframe.M5)
    assert rep.invalid_ohlc_dropped == 1


def test_upto_returns_only_completed_bars():
    df, _ = normalize_bars(intraday_raw("2026-03-10"), Timeframe.M5)
    decision = pd.Timestamp("2026-03-10 10:00", tz="America/New_York")
    cut = upto(df, decision, 5)
    last_start = cut.index[-1].tz_convert("America/New_York")
    assert (last_start.hour, last_start.minute) == (9, 55)   # 09:55 bar closes at 10:00; 10:00 bar is not complete


def test_daily_upto_excludes_today_before_the_close():
    days = pd.bdate_range("2026-03-02", "2026-03-10")
    daily = pd.DataFrame({"date": days, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0})
    df, _ = normalize_bars(daily, Timeframe.D1)
    at_10am = daily_upto(df, pd.Timestamp("2026-03-10 10:00", tz="America/New_York"))
    assert at_10am.index[-1].tz_convert("America/New_York").date() == dt.date(2026, 3, 9)
    after_close = daily_upto(df, pd.Timestamp("2026-03-10 16:00", tz="America/New_York"))
    assert after_close.index[-1].tz_convert("America/New_York").date() == dt.date(2026, 3, 10)


def test_store_round_trip_and_data_version(tmp_path):
    store = BarStore(tmp_path / "b.sqlite")
    df, _ = normalize_bars(intraday_raw("2026-03-10"), Timeframe.M5)
    assert store.upsert("spy", Timeframe.M5, "twelvedata", df) == len(df)
    back = store.load("SPY", Timeframe.M5, source="twelvedata")
    assert len(back) == len(df) and (back["close"].values == df["close"].values).all()
    assert data_version(back) == data_version(df)
    changed = df.copy()
    changed.iloc[10, changed.columns.get_loc("close")] += 0.01
    assert data_version(changed) != data_version(df)


def test_each_session_comes_from_exactly_one_source(tmp_path):
    store = BarStore(tmp_path / "b.sqlite")
    df, _ = normalize_bars(intraday_raw("2026-03-10"), Timeframe.M5)
    tt = df.copy()
    tt["close"] = tt["close"] + 1
    td = df[df["session"] == "RTH"].iloc[:-5]         # Twelve Data: RTH only, with a gap at the end
    store.upsert("SPY", Timeframe.M5, "tastytrade", tt)
    store.upsert("SPY", Timeframe.M5, "twelvedata", td)
    merged = store.load("SPY", Timeframe.M5)
    rth = merged[merged["session"] == "RTH"]
    assert (rth["source"] == "twelvedata").all() and len(rth) == len(td)   # gap NOT filled from tastytrade
    assert (merged[merged["session"] != "RTH"]["source"] == "tastytrade").all()


def multi_day(days=25):
    frames = [intraday_raw(d.strftime("%Y-%m-%d")) for d in pd.bdate_range("2026-02-02", periods=days)
              if d.date() != dt.date(2026, 2, 16)]
    return normalize_bars(pd.concat(frames), Timeframe.M5)[0]


def test_quality_ok_on_clean_data():
    rep = check_bars(multi_day(), "SPY", Timeframe.M5)
    assert rep.status == OK, rep.issues


def test_quality_flags_missing_candles_and_short_history():
    df = multi_day()
    rth = df[df["session"] == "RTH"]
    holes = rth.index[::2]                          # drop half the RTH candles on every day
    rep = check_bars(df.drop(holes), "SPY", Timeframe.M5)
    assert rep.status == DATA_INSUFFICIENT
    assert any("missing" in i for i in rep.issues)
    assert check_bars(multi_day(5), "SPY", Timeframe.M5).status == DATA_INSUFFICIENT


def test_quality_rejects_bars_at_or_after_the_decision_time():
    df = multi_day()
    rep = check_bars(df, "SPY", Timeframe.M5, decision_ts=df.index[-10])
    assert rep.status == DATA_INSUFFICIENT and any("look-ahead" in i for i in rep.issues)


def test_missing_premarket_minutes_are_not_errors():
    df = multi_day()
    thin = df.drop(df[df["session"] == "PREMARKET"].index[::3])
    assert check_bars(thin, "SPY", Timeframe.M5).status == OK


def _fake_candles(times_ms, volume=1000.0):
    return [{"eventType": "Candle", "time": t, "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5, "volume": volume}
            for t in times_ms]


def test_tastytrade_daily_candles_keep_their_trading_date(monkeypatch):
    from app.strategy_engine.data.providers import TastytradeProvider

    # dxFeed stamps the 2026-09-18 daily candle at 2026-09-18 00:00 UTC (= 09-17 20:00 in New York)
    t = int(pd.Timestamp("2026-09-18", tz="UTC").timestamp() * 1000)
    p = TastytradeProvider()

    async def fake(sym, from_ms, **kw):
        return _fake_candles([t])

    monkeypatch.setattr(p, "_candles", fake)
    df = p.fetch("VIX", Timeframe.D1, dt.date(2026, 9, 1), dt.date(2026, 9, 18))
    assert df.index[0].tz_convert("America/New_York").date() == dt.date(2026, 9, 18)


def test_index_candles_without_volume_are_kept(monkeypatch):
    from app.strategy_engine.data.providers import TastytradeProvider

    t = int(pd.Timestamp("2026-09-17", tz="UTC").timestamp() * 1000)
    p = TastytradeProvider()

    async def fake(sym, from_ms, **kw):
        return _fake_candles([t], volume="NaN")

    monkeypatch.setattr(p, "_candles", fake)
    df = p.fetch("VIX", Timeframe.D1, dt.date(2026, 9, 1), dt.date(2026, 9, 18))
    assert len(df) == 1 and df["volume"].iloc[0] == 0.0
