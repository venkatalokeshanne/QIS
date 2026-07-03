"""
Tests for the indicator registry / discovery mechanism itself —
this is the contract the whole 'add one file, no edits' promise rests on.
"""

from app.indicators.registry import discover_indicators, get_indicator, list_indicators


def test_discovery_finds_all_built_in_indicators():
    discover_indicators()
    names = {i["name"] for i in list_indicators()}
    assert {"sma", "ema", "vwap", "atr", "rsi", "opening_range", "macd"}.issubset(names)


def test_get_indicator_returns_correct_instance():
    discover_indicators()
    sma = get_indicator("sma")
    assert sma.metadata.name == "sma"


def test_unknown_indicator_raises_keyerror():
    discover_indicators()
    try:
        get_indicator("does_not_exist")
        assert False, "expected KeyError"
    except KeyError as e:
        assert "does_not_exist" in str(e)


def test_every_indicator_exposes_required_metadata():
    discover_indicators()
    for meta in list_indicators():
        assert meta["name"]
        assert meta["display_name"]
        assert isinstance(meta["default_params"], dict)
