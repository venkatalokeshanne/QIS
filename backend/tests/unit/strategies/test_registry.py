"""Tests for the strategy registry / discovery mechanism."""

from app.strategies.registry import discover_strategies, get_strategy, list_strategies


def test_discovery_finds_built_in_strategies():
    discover_strategies()
    names = {s["name"] for s in list_strategies()}
    assert {"orb_breakout", "hma_trend_cross"}.issubset(names)


def test_get_strategy_returns_correct_instance():
    discover_strategies()
    orb = get_strategy("orb_breakout")
    assert orb.metadata.name == "orb_breakout"


def test_every_strategy_declares_an_indicators_used_list():
    # Not required to be non-empty -- a strategy can legitimately react
    # to raw price action without composing any prepared indicator.
    discover_strategies()
    for meta in list_strategies():
        assert isinstance(meta["indicators_used"], list)
