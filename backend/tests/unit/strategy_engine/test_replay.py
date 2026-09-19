"""Step 14: historical replay -- no look-ahead anywhere in the selection path.

For a set of past decision times (premarket, the open, intraday, the close,
after hours) the selector is run twice: once on the full bar store, and once
on a store that physically contains nothing at or after the decision time.
Every regime, family decision, gate verdict and data version must be
identical -- if any component peeked at a future bar, the two runs would
differ. Runs on the real local bar store; skipped when it is not populated.
"""

import pandas as pd
import pytest

from app.strategy_engine.data.store import DEFAULT_DB, BarStore
from app.strategy_engine.historical import EngineDB
from app.strategy_engine.models import Timeframe
from app.strategy_engine.selector import StrategySelector

NY = "America/New_York"
TICKER = "AAPL"

DECISIONS = [
    "2026-06-02 08:00",   # deep premarket
    "2026-06-02 09:25",   # just before the open
    "2026-06-02 09:30",   # the open: premarket frozen
    "2026-07-15 10:00",   # before extended-hours coverage began
    "2026-09-02 08:00",   # premarket with coverage
    "2026-09-02 09:25",
    "2026-08-20 12:37",   # off a bar boundary
    "2026-09-17 15:55",
    "2026-09-17 18:30",   # after hours
    "2026-07-04 11:00",   # holiday: market closed
]


class CutoffStore:
    """A BarStore view that holds only bars stamped before `cutoff` -- what the
    database would have contained at that moment, give or take bars still
    forming (which the detectors must ignore on their own)."""

    def __init__(self, store: BarStore, cutoff: pd.Timestamp):
        self.store, self.cutoff = store, cutoff

    def load(self, symbol, timeframe, source=None, start=None, end=None):
        end = self.cutoff if end is None else min(pd.Timestamp(end), self.cutoff)
        return self.store.load(symbol, timeframe, source=source, start=start, end=end)


def _store():
    if not DEFAULT_DB.exists():
        pytest.skip("no local bar store")
    s = BarStore()
    if s.load(TICKER, Timeframe.M5, end=pd.Timestamp("2026-06-03", tz=NY)).empty:
        pytest.skip(f"bar store has no {TICKER} 5m history")
    return s


def _run(store, ts, include_premarket=True):
    sel = StrategySelector(store=store, db=EngineDB(), log=False)
    r = sel.select(TICKER, Timeframe.M5, ts, include_premarket=include_premarket)
    return {
        "status": r.status,
        "market": r.market_regime,
        "ticker": r.ticker_regime,
        "premarket": r.premarket_regime,
        "families": (r.eligible_families, r.lower_priority_families),
        "verdicts": sorted((v["strategy"], v["status"], v["reason"]) for v in r.rejected_strategies)
        + sorted((q["strategy"], "QUALIFIED") for q in r.qualified_strategies),
        "data_version": r.versions.get("data_version"),
    }


@pytest.mark.parametrize("when", DECISIONS)
def test_future_bars_do_not_change_a_past_selection(when):
    store = _store()
    ts = pd.Timestamp(when, tz=NY)
    full = _run(store, ts)
    past = _run(CutoffStore(store, ts), ts)
    for key in full:
        assert full[key] == past[key], f"{key} differs at {when}: look-ahead"


def test_premarket_is_frozen_at_the_open():
    store = _store()
    at_open = _run(store, pd.Timestamp("2026-09-02 09:30", tz=NY))["premarket"]
    later = _run(store, pd.Timestamp("2026-09-02 14:00", tz=NY))["premarket"]
    if at_open.get("status") != "AVAILABLE":
        pytest.skip("no premarket data on the replay day")
    assert at_open["premarket_regime"] == later["premarket_regime"]
    assert at_open["premarket_data_through"] == later["premarket_data_through"]


def test_premarket_before_the_open_only_sees_elapsed_minutes():
    store = _store()
    r = _run(store, pd.Timestamp("2026-09-02 08:00", tz=NY))["premarket"]
    through = r.get("premarket_data_through")
    if through:
        assert pd.Timestamp(through) <= pd.Timestamp("2026-09-02 08:00", tz=NY)


def test_replay_qualification_is_point_in_time():
    store = _store()
    sel = StrategySelector(store=store, db=EngineDB(), log=False)
    r = sel.select(TICKER, Timeframe.M5, pd.Timestamp("2026-06-02 10:00", tz=NY))
    evals = [(v.get("qualification") or {}).get("evaluation") or {} for v in r.rejected_strategies]
    evals = [e for e in evals if e.get("bars_to")]
    if not evals:
        pytest.skip("no evaluations stored for the replay ticker")
    assert all(e["point_in_time"] and e["trades_closed_before"] <= e["trades_total"] for e in evals)
    assert any(n.startswith("POINT_IN_TIME_REPLAY") for n in r.notes)


def test_point_in_time_equals_an_evaluation_run_at_that_moment(tmp_path):
    """The gold standard: statistics rebuilt from stored trades closed before T
    must equal a fresh evaluation on bars that end at T -- same trades, same
    prices, same PF / OOS / walk-forward / parameter stability."""
    import json
    import shutil

    from app.strategy_engine.evaluation import StrategyEvaluator, point_in_time_performance
    from app.strategy_engine.registry import default_registry

    store = _store()
    s = default_registry().get("ts_macd_momentum_strategy")
    tf, as_of = Timeframe.parse("1h"), pd.Timestamp("2025-12-01 10:00", tz=NY)
    if store.load(TICKER, tf, source="twelvedata").empty:
        pytest.skip(f"no {TICKER} 1h bars")
    full_db = EngineDB(tmp_path / "full.sqlite")
    shutil.copy(EngineDB().path, full_db.path)          # regime histories for trade tagging
    StrategyEvaluator(store=store, db=full_db).evaluate(TICKER, s, tf)
    cut_db = EngineDB(tmp_path / "cut.sqlite")
    shutil.copy(full_db.path, cut_db.path)
    StrategyEvaluator(store=CutoffStore(store, as_of), db=cut_db).evaluate(TICKER, s, tf)

    perf = full_db.load_performance(TICKER, s.id, str(tf))
    details = json.loads(perf[perf.scope == "ALL_TIME"].iloc[0]["details"])
    pit, info = point_in_time_performance(full_db, TICKER, s, str(tf), as_of, details)
    assert info["parameter_stability_point_in_time"]
    cut = cut_db.load_performance(TICKER, s.id, str(tf))
    a, b = pit[pit.scope == "ALL_TIME"].iloc[0], cut[cut.scope == "ALL_TIME"].iloc[0]
    for k in ("trade_count", "profit_factor", "oos_profit_factor", "walk_forward_pass_rate", "parameter_stability",
              "slippage_robustness", "max_drawdown"):
        assert a[k] == b[k], k

    closed = full_db.load_trades(TICKER, s.id, str(tf))
    closed = closed[closed.exit_time < as_of.timestamp()].reset_index(drop=True)
    fresh = cut_db.load_trades(TICKER, s.id, str(tf)).reset_index(drop=True)
    cols = ["entry_time", "exit_time", "entry_price", "exit_price"]
    pd.testing.assert_frame_equal(closed[cols], fresh[cols])     # the strategy itself never peeks ahead
