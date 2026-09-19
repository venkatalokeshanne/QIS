"""Steps 5-6: timeframe compatibility and strategy-family eligibility."""

from app.strategy_engine.models import Timeframe
from app.strategy_engine.registry import default_registry
from app.strategy_engine.strategy_family import ELIGIBLE, LOWER_PRIORITY, NOT_APPLICABLE, StrategyFamilyEngine
from app.strategy_engine.timeframe import COMPATIBLE, DATA_MISMATCH, TIMEFRAME_MISMATCH, TimeframeSelector

REG = default_registry()


def test_declared_timeframe_is_compatible():
    assert TimeframeSelector().check(REG.get("ts_orb_long_15_min"), Timeframe.M15).status == COMPATIBLE


def test_wrong_timeframe_is_rejected_with_reason():
    c = TimeframeSelector().check(REG.get("ts_turtle_traders_long_daily"), Timeframe.M5)
    assert c.status == TIMEFRAME_MISMATCH
    assert "1D" in c.reason and "5m" in c.reason


def test_intraday_strategy_on_daily_bars_is_a_data_mismatch():
    assert TimeframeSelector().check(REG.get("ts_orb_long_15_min"), Timeframe.D1).status == DATA_MISMATCH


M_BULL_HIGH = {"direction": "BULLISH", "volatility": "HIGH", "trend_strength": "STRONG"}
M_NEUTRAL_NORMAL = {"direction": "NEUTRAL", "volatility": "NORMAL", "trend_strength": "WEAK"}
T_STRONG_MOM = {"trend": "UPTREND", "momentum": "STRONG", "volatility": "HIGH", "volume": "HIGH_VOLUME"}
T_NEUTRAL = {"trend": "NEUTRAL", "momentum": "NEUTRAL", "volatility": "NORMAL", "volume": "NORMAL_VOLUME"}


def test_bullish_high_vol_strong_momentum_prefers_breakout_vwap_trend():
    d = StrategyFamilyEngine().decide(M_BULL_HIGH, T_STRONG_MOM)
    for f in ("BREAKOUT_MOMENTUM", "VWAP_INTRADAY", "TREND_FOLLOWING"):
        assert f in d.eligible
    assert "MEAN_REVERSION" in d.lower_priority
    assert any(r["name"] == "bullish_high_volatility_strong_momentum" for r in d.fired_rules)


def test_neutral_calm_market_prefers_mean_reversion_and_reversal():
    d = StrategyFamilyEngine().decide(M_NEUTRAL_NORMAL, T_NEUTRAL)
    assert set(d.eligible) >= {"MEAN_REVERSION", "REVERSAL"}
    assert "BREAKOUT_MOMENTUM" in d.not_applicable


def test_unreliable_premarket_does_not_change_families():
    base = StrategyFamilyEngine().decide(M_NEUTRAL_NORMAL, T_NEUTRAL, None)
    unreliable = StrategyFamilyEngine().decide(M_NEUTRAL_NORMAL, T_NEUTRAL,
                                               {"premarket_regime": "PREMARKET_UNRELIABLE", "structure": "FADING"})
    assert unreliable.eligible == base.eligible and unreliable.lower_priority == base.lower_priority
    assert any("does not add or remove" in n for n in unreliable.notes)


def test_strong_premarket_gap_adds_breakout_families():
    d = StrategyFamilyEngine().decide(M_NEUTRAL_NORMAL, T_NEUTRAL,
                                      {"premarket_regime": "STRONG_GAP_UP_HIGH_PARTICIPATION", "structure": "HOLDING_HIGHS"})
    assert "BREAKOUT_MOMENTUM" in d.eligible and "VWAP_INTRADAY" in d.eligible


def test_no_rule_matched_keeps_everything_applicable():
    d = StrategyFamilyEngine({"rules": []}).decide(M_NEUTRAL_NORMAL, T_NEUTRAL)
    assert len(d.eligible) == 7 and not d.not_applicable


def test_wrong_family_strategy_is_rejected():
    d = StrategyFamilyEngine().decide(M_NEUTRAL_NORMAL, T_NEUTRAL)
    status, reason = StrategyFamilyEngine.strategy_status(REG.get("ts_orb_long_15_min"), d)
    assert status == NOT_APPLICABLE and "BREAKOUT_MOMENTUM" in reason
    ok, _ = StrategyFamilyEngine.strategy_status(REG.get("ts_keltner_channel_bounce"), d)
    assert ok == ELIGIBLE


def test_secondary_family_can_make_a_strategy_applicable():
    d = StrategyFamilyEngine().decide(M_BULL_HIGH, T_STRONG_MOM)
    # Donchian Crawl: primary BREAKOUT_MOMENTUM, secondary TREND_FOLLOWING
    assert StrategyFamilyEngine.strategy_status(REG.get("ts_donchian_crawl"), d)[0] in (ELIGIBLE, LOWER_PRIORITY)
