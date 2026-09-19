"""Tests for the ported TrendSpider strategies (app.strategies.trendspider).

Offline only: every check runs against synthetic bars, so the suite never
depends on a data vendor. Parity against TrendSpider's own recorded
results is a separate, network-dependent harness
(scripts/trendspider_parity.py).
"""

import json

import pandas as pd
import pytest

from app.domain.interfaces.strategy import TradeDirection
from app.indicators.trendspider_store._runtime.indicator import StoreScriptError
from app.strategies.evaluator_errors import StrategyUnsupported
from app.strategies.registry import discover_strategies, strategy_registry
from app.strategies.trendspider.strategy import MODELS_DIR, load_models


@pytest.fixture(scope="module", autouse=True)
def _discovered():
    discover_strategies()


def _bars(n=300):
    """An OSCILLATING series, so moving averages genuinely cross.

    A monotonic ramp looks like reasonable test data but is useless
    here: the fast MA sits above the slow one from the first non-NaN bar
    onwards and never crosses again, so every cross-based strategy
    reports zero signals and the tests pass vacuously.
    """
    import math

    idx = pd.date_range("2023-01-02 09:30", periods=n, freq="1D")
    close = pd.Series(
        [100 + i * 0.15 + 12 * math.sin(i / 9.0) + 3 * math.sin(i / 2.3) for i in range(n)],
        index=idx,
    )
    return pd.DataFrame(
        {
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close + 1.5,
            "low": close - 1.5,
            "close": close,
            "volume": [1_000_000 + (i % 13) * 50_000 for i in range(n)],
        },
        index=idx,
    )


def _ts_strategies():
    return {n: c for n, c in strategy_registry.all().items() if n.startswith("ts_")}


def test_every_extracted_model_is_registered():
    # 75 backtested strategies + 6 subscribed/built-in ones that never ran
    # (disabled in the automation config) = the account's full
    # subscribed + built-in set.
    assert len(_ts_strategies()) == len(load_models()) == 81


def test_models_all_carry_entry_conditions():
    for path in MODELS_DIR.glob("*.json"):
        model = json.loads(path.read_text(encoding="utf-8"))["model"]
        assert (model.get("enterCondition") or {}).get("conditions"), path.name


def test_supported_strategies_produce_aligned_signal_series():
    df = _bars()
    checked = 0
    for name, cls in _ts_strategies().items():
        strategy = cls()
        if not strategy.support_status()[0]:
            continue
        try:
            entries = strategy.generate_entries(strategy.prepare(df, {}), {})
            exits = strategy.generate_exits(strategy.prepare(df, {}), {})
        except StoreScriptError:
            # Intraday-only scripts (ORB) refuse daily bars exactly as the
            # TrendSpider script asserts; covered by their own tests.
            continue
        assert len(entries) == len(df), name
        assert len(exits) == len(df), name
        assert exits.dtype == bool, name
        assert set(entries.dropna().unique()) <= {TradeDirection.LONG, TradeDirection.SHORT}, name
        checked += 1
    assert checked >= 50, f"expected most of the 75 to be runnable, got {checked}"


def test_unsupported_strategies_raise_rather_than_returning_empty_signals():
    """A strategy that cannot be reproduced must fail loudly. Quietly
    returning no signals would look like 'this strategy simply had no
    trades', which is indistinguishable from a real (wrong) result."""
    df = _bars()
    for name, cls in _ts_strategies().items():
        strategy = cls()
        if strategy.support_status()[0]:
            continue
        with pytest.raises(StrategyUnsupported):
            strategy.generate_entries(df, {})


def test_recommended_execution_reproduces_trendspider_execution():
    strategy = strategy_registry.get("ts_8_21_ema_cross_long_daily")()
    config = strategy.recommended_execution()

    # TrendSpider fills at the next bar's open, holds overnight, and the
    # extracted models all carry a 0% cost of trade.
    assert config.fill_at == "next_open"
    assert config.force_close_at_session_end is False
    assert config.slippage_pct == 0.0


def test_risk_settings_are_read_from_the_model():
    """The stop/target/trailing values live only in the model's exit
    conditions -- they are invisible in TrendSpider's condition UI, so a
    regression here would silently drop risk management."""
    strategy = strategy_registry.get("ts_1_hr_webster_power_trend_long")()
    config = strategy.recommended_execution()
    assert config.stop_loss_pct == pytest.approx(0.045)
    assert config.trailing_stop_pct == pytest.approx(0.06)
    assert config.take_profit_pct == pytest.approx(0.25)


def test_timeframe_is_not_pinned_to_the_authoring_interval():
    """Every extracted strategy was verified single-timeframe, and
    TrendSpider recomputed them on whatever chart interval was selected.
    So a Daily-authored strategy must still run on intraday bars."""
    strategy = strategy_registry.get("ts_8_21_ema_cross_long_daily")()
    assert strategy.metadata.default_params["source_timeframe"] == "1day"

    intraday = _bars().copy()
    intraday.index = pd.date_range("2023-01-02 09:30", periods=len(intraday), freq="5min")
    entries = strategy.generate_entries(strategy.prepare(intraday, {}), {})
    assert len(entries) == len(intraday)
    assert entries.notna().any(), "should still generate signals on 5-minute bars"


# --- ORB Trading Strategy Indicator (port of publisher-released source) ---


def _orb_session():
    """One NY session of 5-minute bars. OR = the 9:30 bar (99-101, range 2);
    9:40 closes above 101 (long breakout); 10:30 crosses the 3R target 107."""
    idx = pd.date_range("2024-03-04 09:30", "2024-03-04 15:55", freq="5min")
    special = {
        "09:30": (100, 101, 99, 100),
        "09:35": (100, 100.8, 99.5, 100.5),
        "09:40": (100.5, 102, 100.4, 101.8),
        "10:30": (106, 107.5, 105.9, 107.2),
    }
    rows = [special.get(t.strftime("%H:%M"), (103, 104, 102.5, 103.5)) + (1000,) for t in idx]
    return pd.DataFrame(rows, index=idx, columns=["open", "high", "low", "close", "volume"])


def test_orb_long_follows_the_published_script():
    from app.strategies.trendspider.script_orb import compute_orb

    out = compute_orb(_orb_session(), {"session": "New York (9:30 AM ET)", "or_window": "Auto"})
    at = lambda name: [t.strftime("%H:%M") for t, v in out[name].items() if v]  # noqa: E731

    assert at("entry__long__strategy_") == ["09:40"]      # close crossed above ORH
    assert at("target__long_3r") == ["10:30"]              # ORH + 3 * range = 107
    assert at("session_exit") == ["15:55"]                 # 16:00 minus one 5m bar
    # Safe entry window: OR locked (from 9:35) and before 16:00 - floor(5 * 3.5) = 15:43.
    safe = at("safe_entry_window")
    assert safe[0] == "09:35" and safe[-1] == "15:40"


def test_orb_allows_only_one_entry_per_session():
    from app.strategies.trendspider.script_orb import compute_orb

    df = _orb_session()
    # A second, later close back above ORH must not create another entry.
    df.loc["2024-03-04 11:00"] = (100, 100.5, 99.5, 100.2, 1000)
    df.loc["2024-03-04 11:05"] = (100.2, 102, 100.1, 101.9, 1000)
    out = compute_orb(df, {"session": "New York (9:30 AM ET)", "or_window": "Auto"})
    assert int(out["entry__long__strategy_"].sum()) == 1


def test_orb_refuses_unsupported_bar_sizes_like_the_script_does():
    from app.strategies.trendspider.script_orb import compute_orb

    daily = _bars()  # 1-day bars: the script asserts on non 1/5/10/15/30/60m charts
    with pytest.raises(ValueError, match="1/5/10/15/30/60"):
        compute_orb(daily, {"session": "New York (9:30 AM ET)", "or_window": "Auto"})
