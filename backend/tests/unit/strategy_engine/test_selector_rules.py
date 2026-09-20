"""Selector ranking and duplicate handling (capital efficiency, double exposure)."""

import pandas as pd
import pytest

from app.strategy_engine.selector import DUPLICATE, StrategySelector, StrategyVerdict


def verdict(sid, name, per_day=None, regime_pf=None, oos=None):
    return StrategyVerdict(strategy_id=sid, strategy=name, slug=name.lower(), family="TREND_FOLLOWING",
                           status="QUALIFIED", reason="",
                           qualification={"historical": {"expectancy_per_capital_day": per_day},
                                          "regime_matched": {"status": "MATCHED", "profit_factor": regime_pf} if regime_pf else {},
                                          "out_of_sample": {"profit_factor": oos}})


class StubDB:
    """Stored trades per strategy id, as entry timestamps."""

    def __init__(self, entries):
        self.entries = entries

    def load_trades(self, ticker, sid, tf, variant="base"):
        return pd.DataFrame({"entry_time": self.entries.get(sid, [])})


def selector(entries):
    s = StrategySelector.__new__(StrategySelector)
    s.db = StubDB(entries)
    return s


def test_ranking_prefers_capital_efficiency():
    slow_big = verdict(1, "Daily holder", per_day=0.0004, oos=2.0)     # 1% over 25 days
    quick = verdict(2, "Intraday", per_day=0.0030, oos=1.3)            # 0.3% in 2 hours
    ranked = sorted([slow_big, quick], key=StrategySelector._strength, reverse=True)
    assert [v.strategy for v in ranked] == ["Intraday", "Daily holder"]


def test_missing_metric_sorts_last_but_still_ranks_by_profit_factor():
    a, b = verdict(1, "No metric", oos=1.9), verdict(2, "No metric too", oos=1.2)
    ranked = sorted([b, a], key=StrategySelector._strength, reverse=True)
    assert [v.strategy for v in ranked] == ["No metric", "No metric too"]


def test_near_identical_strategies_are_dropped_keeping_the_stronger():
    twin_a, twin_b = list(range(100)), list(range(2, 100))             # ~98% the same signals
    s = selector({1: twin_a, 2: twin_b, 3: list(range(500, 560))})
    ranked = [verdict(1, "EMA Cross", per_day=0.003), verdict(2, "Basic EMA Cross", per_day=0.002),
              verdict(3, "Different", per_day=0.001)]
    kept, dropped = s._drop_duplicates(ranked, "AAPL", "30m")
    assert [v.strategy for v in kept] == ["EMA Cross", "Different"]
    assert dropped == [(ranked[1], "EMA Cross")]


def test_partly_overlapping_strategies_are_both_kept():
    s = selector({1: list(range(100)), 2: list(range(50, 150))})       # 33% overlap
    kept, dropped = s._drop_duplicates([verdict(1, "A", per_day=0.003), verdict(2, "B", per_day=0.002)], "AAPL", "30m")
    assert len(kept) == 2 and not dropped


def test_duplicate_status_is_reported_not_hidden():
    assert DUPLICATE == "DUPLICATE"
