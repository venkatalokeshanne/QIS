"""
Tests for app.services.levels_signal -- an explainable, rule-based
buy/sell/neutral read of the CURRENT moment against the Daily Levels
snapshot. Not a backtestable strategy -- these tests check each rule's
scoring/reasons in isolation using synthetic DailyLevels fixtures, not
historical win rate.
"""

from datetime import datetime

from app.services.levels_service import DailyLevels
from app.services.levels_signal import compute_signal

_EMPTY_PIVOTS = {"pivot": None, "r1": None, "r2": None, "r3": None, "s1": None, "s2": None, "s3": None}
_EMPTY_CAMARILLA = {"r1": None, "r2": None, "r3": None, "r4": None, "s1": None, "s2": None, "s3": None, "s4": None}
_EMPTY_DEMARK = {"pivot": None, "resistance": None, "support": None}
_EMPTY_FIB = {"236": None, "382": None, "50": None, "618": None, "786": None}


def _base_levels(**overrides) -> DailyLevels:
    defaults = dict(
        symbol="TEST",
        as_of=datetime(2024, 1, 2, 15, 55),
        current_price=100.0,
        session_open=100.0,
        prior_close=100.0,
        prior_high=105.0,
        prior_low=95.0,
        gap_pct=0.0,
        opening_range_high=None,
        opening_range_low=None,
        vwap=None,
        adr=None,
        adr_expected_high=None,
        adr_expected_low=None,
        pivot_points=dict(_EMPTY_PIVOTS),
        camarilla_pivots=dict(_EMPTY_CAMARILLA),
        demark_pivots=dict(_EMPTY_DEMARK),
        auto_support_resistance=[],
        fibonacci_retracement=dict(_EMPTY_FIB),
    )
    defaults.update(overrides)
    return DailyLevels(**defaults)


def test_neutral_when_nothing_lines_up():
    levels = _base_levels()
    result = compute_signal(levels)
    assert result.verdict == "neutral"
    assert result.score == 0


def test_price_above_vwap_contributes_bullish_point():
    levels = _base_levels(vwap=95.0)  # price 100 > vwap 95
    result = compute_signal(levels)
    assert result.score >= 1
    assert any("above VWAP" in r for r in result.reasons)


def test_price_below_vwap_contributes_bearish_point():
    levels = _base_levels(vwap=105.0)  # price 100 < vwap 105
    result = compute_signal(levels)
    assert result.score <= -1
    assert any("below VWAP" in r for r in result.reasons)


def test_at_adr_expected_low_contributes_bullish_point():
    levels = _base_levels(adr_expected_low=100.0, adr_expected_high=110.0)
    result = compute_signal(levels)
    assert any("ADR-projected low" in r for r in result.reasons)


def test_at_adr_expected_high_contributes_bearish_point():
    levels = _base_levels(adr_expected_high=100.0, adr_expected_low=90.0)
    result = compute_signal(levels)
    assert any("ADR-projected high" in r for r in result.reasons)


def test_gap_up_giving_back_the_move_is_bearish():
    levels = _base_levels(session_open=105.0, prior_close=100.0, current_price=100.0, gap_pct=5.0)
    result = compute_signal(levels)
    assert any("gap-fill tendency favors further downside" in r for r in result.reasons)


def test_gap_down_recovering_is_bullish():
    levels = _base_levels(session_open=95.0, prior_close=100.0, current_price=100.0, gap_pct=-5.0)
    result = compute_signal(levels)
    assert any("gap-fill tendency favors further upside" in r for r in result.reasons)


def test_confluence_support_zone_produces_buy_verdict():
    """Price sitting right at a support zone confirmed by multiple
    independent level families (pivot S1, Camarilla S1, an Auto S/R
    level all landing within tolerance) should score a clear buy,
    reinforced by VWAP and ADR agreeing."""
    levels = _base_levels(
        current_price=99.9,
        vwap=99.0,  # price above vwap -- bullish
        adr_expected_low=99.9,  # price AT the adr low -- bullish (exhaustion)
        adr_expected_high=110.0,
        pivot_points={**_EMPTY_PIVOTS, "s1": 99.8},
        camarilla_pivots={**_EMPTY_CAMARILLA, "s1": 99.85},
        auto_support_resistance=[99.75],
    )
    result = compute_signal(levels)
    assert result.verdict == "buy"
    assert result.score >= 2
    assert any("confirmed by" in r for r in result.reasons)


def test_confluence_resistance_zone_produces_sell_verdict():
    levels = _base_levels(
        current_price=100.1,
        vwap=101.0,  # price below vwap -- bearish
        adr_expected_high=100.1,  # price AT the adr high -- bearish (exhaustion)
        adr_expected_low=90.0,
        pivot_points={**_EMPTY_PIVOTS, "r1": 100.2},
        camarilla_pivots={**_EMPTY_CAMARILLA, "r1": 100.15},
        auto_support_resistance=[100.25],
    )
    result = compute_signal(levels)
    assert result.verdict == "sell"
    assert result.score <= -2
    assert any("confirmed by" in r for r in result.reasons)


def test_single_unconfirmed_level_does_not_alone_trigger_a_verdict():
    """Being near a level that NO other family agrees with shouldn't,
    by itself, produce a buy/sell verdict -- that's the whole point of
    requiring confluence."""
    levels = _base_levels(current_price=99.9, pivot_points={**_EMPTY_PIVOTS, "s1": 99.8})
    result = compute_signal(levels)
    assert result.verdict == "neutral"
    assert any("no other level family confirms it" in r for r in result.reasons)
