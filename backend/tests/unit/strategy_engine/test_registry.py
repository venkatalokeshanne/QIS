"""Step 1: strategy registry (spec section 24)."""

import json

import pytest

from app.strategy_engine.models import AssetScope, Family, Timeframe
from app.strategy_engine.registry import CATALOG_PATH, CatalogError, StrategyRegistry, default_registry


def test_catalog_loads_every_ported_strategy_with_a_version():
    reg = default_registry()
    assert len(reg) == 81
    assert reg.version  # logged with every decision


def test_every_entry_has_the_required_metadata():
    for s in default_registry().all():
        assert s.family in Family
        assert s.timeframes, s.slug
        assert s.session and s.minimum_data and s.direction
        if s.asset_scope is AssetScope.SPECIFIC_TICKER:
            assert s.allowed_tickers, s.slug


def test_ticker_specific_strategies_are_restricted():
    reg = default_registry()
    assert reg.get("ts_tsla_21_ema_pullback_long").allowed_tickers == ("TSLA",)
    assert reg.get("ts_qqq_vwap_rush").allowed_tickers == ("QQQ",)
    assert reg.get("ts_orb_long_15_min").asset_scope is AssetScope.EQUITY


def test_timeframes_are_declared_not_assumed():
    reg = default_registry()
    assert reg.get("ts_orb_long_15_min").timeframes == (Timeframe.M15,)
    assert reg.get("ts_turtle_traders_long_daily").timeframes == (Timeframe.D1,)


def test_unrunnable_strategies_keep_their_reason():
    s = default_registry().get("ts_supertrend_swing_long_4_hour")
    assert not s.runnable and "IST" in s.not_runnable_reason


def test_ids_are_unique_and_stable_lookup_works():
    reg = default_registry()
    ids = [s.id for s in reg.all()]
    assert len(ids) == len(set(ids))
    s = reg.all()[0]
    assert reg.get(s.id) is reg.get(s.slug)


@pytest.mark.parametrize("alias,expected", [("5min", Timeframe.M5), ("1day", Timeframe.D1), ("60min", Timeframe.H1),
                                            ("D", Timeframe.D1), ("65m", Timeframe.M65)])
def test_timeframe_aliases(alias, expected):
    assert Timeframe.parse(alias) is expected


def test_invalid_catalog_entries_are_rejected(tmp_path):
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    bad = dict(data["strategies"][0], asset_scope="SPECIFIC_TICKER", allowed_tickers=[])
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"version": "t", "strategies": [bad]}))
    with pytest.raises(CatalogError):
        StrategyRegistry.from_file(p)
