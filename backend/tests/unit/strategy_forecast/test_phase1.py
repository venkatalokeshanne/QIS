"""Phase 1: labels, shrinkage, and the no-look-ahead property of the walk-forward."""

import numpy as np
import pandas as pd
import pytest

from app.strategy_forecast.baselines import KeyedRate, Predictor, _Rate
from app.strategy_forecast.evaluate import evaluate_day, walk_forward
from app.strategy_forecast.labels import build_labels_from_daily


def daily(rows):
    """rows: (date, ticker, strategy, pnl, trades)"""
    return pd.DataFrame([{"date": d, "ticker": t, "timeframe": "15m", "strategy": s, "pnl": p,
                          "return_pct": p / 1000, "trade_count": n, "wins": int(p > 0), "losses": int(p <= 0),
                          "win_rate": None, "profit_factor": None, "expectancy": None, "worst_trade": None,
                          "hold_hours": 2.0 * n} for d, t, s, p, n in rows])


def test_rank_is_by_pnl_and_ties_are_deterministic():
    d = build_labels_from_daily(daily([
        ("2026-01-05", "AAPL", "b_winner", 100.0, 2),
        ("2026-01-05", "AAPL", "a_loser", -50.0, 1),
        ("2026-01-05", "AAPL", "c_idle", 0.0, 0),
        ("2026-01-05", "AAPL", "d_idle", 0.0, 0),
    ]))
    by = d.set_index("strategy")["rank"].to_dict()
    assert by["b_winner"] == 1                       # best P&L first
    assert by["a_loser"] == 4                        # a loss ranks below doing nothing
    assert by["c_idle"] < by["d_idle"]               # ties broken by name, reproducibly
    assert d.set_index("strategy")["triggered"].to_dict() == {"b_winner": 1, "a_loser": 1, "c_idle": 0, "d_idle": 0}


def test_traded_ranking_excludes_strategies_that_never_fired():
    d = build_labels_from_daily(daily([
        ("2026-01-05", "AAPL", "traded_win", 100.0, 1),
        ("2026-01-05", "AAPL", "traded_loss", -10.0, 1),
        ("2026-01-05", "AAPL", "idle", 0.0, 0),
    ]))
    by = d.set_index("strategy")
    assert by.loc["idle", "rank"] == 2                       # idle outranks the loser in the raw ranking
    assert pd.isna(by.loc["idle", "rank_traded"])            # ... but is not in the traded ranking at all
    assert by.loc["traded_win", "rank_traded"] == 1
    assert by.loc["traded_loss", "rank_traded"] == 2
    assert by.loc["idle", "top5_traded"] == 0


def test_shrinkage_beats_a_single_lucky_observation():
    """1 top-5 from 1 appearance must not outrank 40 from 100 -- the trap this
    dataset is full of (60% of top-5 days come from a single trade)."""
    r = _Rate(alpha=20.0)
    r.add("lucky", 1.0)
    for i in range(100):
        r.add("solid", 1.0 if i < 40 else 0.0)
    prior = 0.07
    assert r.rate("lucky", prior) < r.rate("solid", prior)
    assert r.rate("unseen", prior) == pytest.approx(prior)   # no data -> the base rate, not zero, not one


def test_precision_at_5_counts_only_real_hits():
    day = pd.DataFrame({"strategy": list("abcdefgh"), "rank": [3, 1, 9, 2, 8, 7, 6, 5],
                        "triggered": 1, "day_return": 0.01})
    res = evaluate_day(day, scores=np.array([9, 8, 7, 6, 5, 4, 3, 2]), k=5)   # picks a,b,c,d,e
    assert res["hits"] == 3 and res["precision_at_k"] == 0.6                  # ranks 3,1,2 are <=5
    assert res["top1_hit"] is True and res["top1_rank"] == 3
    assert res["best_pick_rank"] == 1 and res["mrr"] == 1.0


class SpyPredictor(Predictor):
    """Records the dates it had been taught when asked to score."""

    name = "SPY"

    def __init__(self):
        self.seen: list[str] = []
        self.seen_when_scoring: list[tuple[str, tuple[str, ...]]] = []

    def score(self, day, prior):
        self.seen_when_scoring.append((day["date"].iloc[0], tuple(self.seen)))
        return np.zeros(len(day))

    def update(self, day):
        self.seen.append(day["date"].iloc[0])


def test_walk_forward_never_lets_a_predictor_see_its_own_day_or_later():
    rows = []
    for day in range(1, 13):
        for s in range(8):
            rows.append((f"2026-01-{day:02d}", "AAPL", f"s{s}", float(s), 1))
    d = build_labels_from_daily(daily(rows))
    spy = SpyPredictor()
    rec, _ = walk_forward(d, [spy], warmup_days=2)
    assert rec["date"].nunique() == 10                       # first 2 days teach only
    for scoring_date, seen in spy.seen_when_scoring:
        assert all(s < scoring_date for s in seen), (scoring_date, seen[-3:])


def test_keyed_rate_falls_back_when_the_key_is_too_sparse():
    globally = KeyedRate("GLOBAL", lambda r: r.strategy, "top5_traded")
    keyed = KeyedRate("TICKER", lambda r: (r.ticker, r.strategy), "top5_traded",
                      fallback=globally, min_obs=5)
    day = pd.DataFrame({"ticker": ["AAPL"], "strategy": ["s"], "date": ["2026-01-01"],
                        "top5_traded": [1], "triggered": [1]})
    for _ in range(10):
        globally.update(day)
    sparse = keyed.score(day, prior=0.07)                    # ticker key unseen -> global evidence used
    assert sparse[0] == pytest.approx(globally.score(day, 0.07)[0])
