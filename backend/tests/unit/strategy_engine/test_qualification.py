"""Steps 8-9: qualification and regime-matched performance (spec 28-35, 48)."""

import pytest

from app.strategy_engine.historical import ANY, EngineDB
from app.strategy_engine.models import Timeframe
from app.strategy_engine.qualification import NOT_EVALUATED, NOT_QUALIFIED, QUALIFIED, StrategyQualificationEngine
from app.strategy_engine.registry import default_registry
from app.strategy_engine.thresholds import QUALIFICATION_CONFIG

S = default_registry().get("ts_orb_trading_strategy_backtest_3r_long")   # intraday, uses premarket
TF = Timeframe.M5


def good_details(**over):
    d = {"out_of_sample": {"profit_factor": 1.4, "trade_count": 90},
         "walk_forward": {"walk_forward_periods": 8, "profitable_periods": 6, "pass_rate": 0.75},
         "parameter_stability": {"status": "TESTED", "score": 0.75, "neighbours": 4, "stable_neighbours": 3},
         "slippage": {"0x": {"profit_factor": 1.9}, "1x": {"profit_factor": 1.6}, "2x": {"profit_factor": 1.35},
                      "3x": {"profit_factor": 1.1}},
         "bars_from": "2024-01-02", "bars_to": "2026-09-18", "span_years": 2.7}
    d.update(over)
    return d


def row(scope="ALL_TIME", m=ANY, t=ANY, p=ANY, **over):
    r = {"scope": scope, "market_regime": m, "ticker_regime": t, "premarket_regime": p, "family": "BREAKOUT_MOMENTUM",
         "trade_count": 284, "win_rate": 0.55, "profit_factor": 1.62, "expectancy": 0.003, "sharpe": 1.38,
         "max_drawdown": 0.17, "oos_profit_factor": 1.48, "walk_forward_pass_rate": 0.75, "parameter_stability": 0.75,
         "slippage_robustness": "HIGH", "run_id": "r1", "details": good_details()}
    r.update(over)
    return r


@pytest.fixture
def db(tmp_path):
    return EngineDB(tmp_path / "e.sqlite")


def qualify(db, rows, market="BULLISH_HIGH_VOLATILITY", ticker="HIGH_MOMENTUM_HIGH_VOLATILITY", pm=None, **cfg):
    db.replace_performance("INFQ", S.id, str(TF), rows)
    return StrategyQualificationEngine(db, cfg or None).qualify("INFQ", S, TF, market, ticker, pm)


def test_all_checks_pass_is_qualified(db):
    r = qualify(db, [row()])
    assert r.qualification_status == QUALIFIED, r.reasons


def test_no_history_is_not_evaluated(db):
    r = StrategyQualificationEngine(db).qualify("INFQ", S, TF, "X", "Y")
    assert r.qualification_status == NOT_EVALUATED


def test_profit_factor_below_threshold_is_rejected(db):
    r = qualify(db, [row(profit_factor=1.05)])
    assert r.qualification_status == NOT_QUALIFIED
    assert any(c.name == "profit_factor" for c in r.failed_checks)


def test_out_of_sample_below_threshold_is_rejected(db):
    # the spec's example: in-sample PF 1.85 but OOS PF 0.92 -> NOT QUALIFIED
    r = qualify(db, [row(profit_factor=1.85, oos_profit_factor=0.92)])
    assert r.qualification_status == NOT_QUALIFIED
    assert "out_of_sample_profit_factor: 0.92 (required >= 1.1)" in r.reasons[0]


def test_insufficient_trades_is_rejected(db):
    r = qualify(db, [row(trade_count=40)])
    assert r.qualification_status == NOT_QUALIFIED and r.failed_checks[0].name == "min_trades"


def test_low_slippage_robustness_is_rejected(db):
    r = qualify(db, [row(slippage_robustness="LOW")])
    assert any(c.name == "slippage_robustness" for c in r.failed_checks)


def test_walk_forward_and_parameter_stability(db):
    assert any(c.name == "walk_forward_pass_rate" for c in qualify(db, [row(walk_forward_pass_rate=0.4)]).failed_checks)
    unstable = row(details=good_details(parameter_stability={"status": "TESTED", "score": 0.25, "neighbours": 4, "stable_neighbours": 1}))
    assert any(c.name == "parameter_stability" for c in qualify(db, [unstable]).failed_checks)
    no_params = row(details=good_details(parameter_stability={"status": "NOT_APPLICABLE", "reason": "no parameters"}))
    assert qualify(db, [no_params]).qualification_status == QUALIFIED


def test_regime_matched_results_can_reject_a_good_all_time_strategy(db):
    # ORB all-time PF 1.38 but 0.94 in today's regime -> not qualified today
    rows = [row(profit_factor=1.38),
            row("MARKET_TICKER", "BULLISH_LOW_VOLATILITY", "HIGH_MOMENTUM_HIGH_VOLATILITY", trade_count=60, profit_factor=0.94)]
    r = qualify(db, rows, market="BULLISH_LOW_VOLATILITY")
    assert r.regime_matched["status"] == "MATCHED" and r.regime_matched["profit_factor"] == 0.94
    assert r.qualification_status == NOT_QUALIFIED


def test_small_regime_sample_falls_back_to_all_time(db):
    rows = [row(), row("MARKET_TICKER", "BULLISH_HIGH_VOLATILITY", "HIGH_MOMENTUM_HIGH_VOLATILITY", trade_count=5, profit_factor=0.2)]
    r = qualify(db, rows)
    assert r.regime_matched["status"] == "INSUFFICIENT_SAMPLE"
    assert r.qualification_status == QUALIFIED


def test_regime_match_falls_back_from_combined_to_market_level(db):
    rows = [row(), row("MARKET_TICKER", "BULLISH_HIGH_VOLATILITY", "HIGH_MOMENTUM_HIGH_VOLATILITY", trade_count=5),
            row("MARKET", "BULLISH_HIGH_VOLATILITY", ANY, trade_count=80, profit_factor=1.67)]
    r = qualify(db, rows)
    assert r.regime_matched["level"] == "MARKET" and r.regime_matched["profit_factor"] == 1.67


def test_premarket_matching_is_skipped_when_premarket_is_unreliable(db):
    rows = [row(), row("PREMARKET", ANY, ANY, "STRONG_GAP_UP_HIGH_PARTICIPATION", trade_count=61, profit_factor=0.5)]
    assert qualify(db, rows, pm="PREMARKET_UNRELIABLE").qualification_status == QUALIFIED
    assert qualify(db, rows, pm="STRONG_GAP_UP_HIGH_PARTICIPATION").qualification_status == NOT_QUALIFIED


def test_thresholds_are_configurable(db):
    assert qualify(db, [row(trade_count=40)], min_trades=30).qualification_status == QUALIFIED


def _store_trades(db, n=240, start="2024-01-02", end="2026-09-18"):
    import numpy as np
    import pandas as pd

    t = pd.date_range(start, end, periods=n, tz="UTC").as_unit("s")
    entry = t.asi8 // 1_000_000_000 if t.asi8[0] > 10**12 else t.asi8
    trades = pd.DataFrame({"variant": "base", "entry_time": entry, "exit_time": entry + 3600, "direction": "LONG",
                           "entry_price": 100.0, "exit_price": np.where(np.arange(n) % 3, 101.0, 99.5),
                           "gross_return": 0.0, "market_regime": "M", "ticker_regime": "T",
                           "premarket_regime": "NOT_AVAILABLE", "sample": "IN_SAMPLE"})
    db.replace_trades("r1", "INFQ", S.id, str(TF), trades)
    return trades


def test_replay_rebuilds_statistics_from_trades_closed_before_the_decision(db):
    import pandas as pd

    trades = _store_trades(db)
    no_params = good_details(parameter_stability={"status": "NOT_APPLICABLE", "reason": "no parameters"})
    db.replace_performance("INFQ", S.id, str(TF), [row(trade_count=len(trades), details=no_params)])
    as_of = pd.Timestamp("2025-06-01 12:00", tz="America/New_York")
    cutoff = int(as_of.timestamp())
    # a trade open across the decision time is excluded: its outcome was unknown then
    straddle = trades[(trades.entry_time < cutoff) & (trades.exit_time >= cutoff)]
    closed = int((trades.exit_time < cutoff).sum())

    r = StrategyQualificationEngine(db).qualify("INFQ", S, TF, "M", "T", None, as_of=as_of)
    assert r.evaluation["point_in_time"] and r.evaluation["trades_closed_before"] == closed
    assert r.historical["trade_count"] == closed < len(trades)
    assert straddle.empty or closed == int((trades.entry_time < cutoff).sum()) - len(straddle)
    live = StrategyQualificationEngine(db).qualify("INFQ", S, TF, "M", "T", None, as_of=pd.Timestamp("2026-09-19", tz="UTC"))
    assert not live.evaluation["point_in_time"] and live.historical["trade_count"] == len(trades)


def test_replay_before_the_evaluation_window_is_not_evaluated(db):
    import pandas as pd

    _store_trades(db)
    db.replace_performance("INFQ", S.id, str(TF), [row()])
    r = StrategyQualificationEngine(db).qualify("INFQ", S, TF, "M", "T", None,
                                                as_of=pd.Timestamp("2023-06-01", tz="UTC"))
    assert r.qualification_status == NOT_EVALUATED


def test_aggregate_handles_trades_without_regime_tags():
    # e.g. a young ticker: trades before its regime history exists carry no tag
    import pandas as pd

    from app.strategy_engine.evaluation import aggregate

    entry = [1_700_000_000, 1_710_000_000, 1_720_000_000]
    t = pd.DataFrame({"direction": "LONG", "entry_price": 100.0, "exit_price": [101.0, 99.0, 102.0],
                      "entry_time": entry, "exit_time": [e + 7200 for e in entry],
                      "market_regime": ["M", "M", None], "ticker_regime": [None, None, None],
                      "premarket_regime": ["NOT_AVAILABLE"] * 3})
    rows, all_time, _, _ = aggregate(t, 1_690_000_000, 1_730_000_000, S, "r", QUALIFICATION_CONFIG, 0.0005, {})
    assert all_time["trade_count"] == 3
    # 2h holds: the per-capital-day expectancy is 12x the per-trade expectancy
    assert all_time["expectancy_per_capital_day"] == pytest.approx(all_time["expectancy"] * 12, rel=1e-3)
    ticker_rows = [r for r in rows if r["scope"] == "TICKER"]
    assert [(r["ticker_regime"], r["trade_count"]) for r in ticker_rows] == [("UNKNOWN", 3)]


def test_fragile_stop_is_reported_as_a_warning_not_a_rejection(db):
    from app.strategy_engine.execution_risk import fragility, stop_pct

    fragile = default_registry().get("ts_zero_lag_ma_long_strategy")
    assert stop_pct(fragile.slug) == pytest.approx(0.0005)
    assert fragility(fragile.slug)["status"] == "FRAGILE_STOP"
    db.replace_performance("INFQ", fragile.id, str(TF), [row()])
    r = StrategyQualificationEngine(db).qualify("INFQ", fragile, TF, "BULLISH_HIGH_VOLATILITY",
                                                "HIGH_MOMENTUM_HIGH_VOLATILITY")
    warn = [c for c in r.checks if c.name == "execution_realism"]
    assert warn and warn[0].passed is None and "optimistic" in warn[0].note
    assert r.qualification_status == QUALIFIED          # a warning must not silently drop it
    assert fragility(S.slug)["status"] in ("OK", "NO_STOP")
