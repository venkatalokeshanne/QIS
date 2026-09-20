"""
Walk-forward evaluation of the selection engine.

For every (date, ticker) in chronological order: score the candidates using
only days already seen, take the top K, then compare against that day's actual
ranking and finally let the predictors learn from the day. Nothing is fitted
on a day it is scored on, so these numbers are out-of-sample by construction.

The question being answered is the spec's: if the engine names 5 strategies at
09:30, how often are they in the actual end-of-day top 5?

    precision@5   |predicted n actual top5| / 5
    recall@5      same denominator -- actual top-5 always has exactly 5
    top1_hit      the pick ranked #1 landed inside the actual top 5
    top1_rank     what the #1 pick actually placed (median is the honest one)
    MRR           1 / rank of the best-placing pick
    NDCG@5        rank-weighted overlap
An ABSTAIN threshold suppresses a day when the best score is too weak; days
abstained are reported as coverage, not quietly dropped from the average.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.strategy_forecast.baselines import Predictor

K = 5


def _ndcg(pred_ranks: np.ndarray, k: int = K) -> float:
    gains = 1.0 / np.log2(pred_ranks + 1)
    ideal = (1.0 / np.log2(np.arange(1, k + 1) + 1)).sum()
    return float(gains[pred_ranks <= k].sum() / ideal) if ideal else 0.0


def evaluate_day(day: pd.DataFrame, scores: np.ndarray, k: int = K,
                 abstain_below: float | None = None, rank_col: str = "rank") -> dict | None:
    picks = day.assign(score=scores).sort_values("score", ascending=False).head(k)
    if rank_col != "rank":                      # rank among the strategies that traded
        picks = picks.assign(rank=picks[rank_col].fillna(len(day) + 1))
        day = day.assign(rank=day[rank_col].fillna(len(day) + 1))
    if abstain_below is not None and float(picks["score"].iloc[0]) < abstain_below:
        return {"abstained": True}
    actual_ranks = picks["rank"].to_numpy()
    hits = int((actual_ranks <= k).sum())
    return {
        "abstained": False,
        "precision_at_k": hits / k,
        "recall_at_k": hits / min(k, len(day)),
        "hits": hits,
        "top1_hit": bool(actual_ranks[0] <= k),
        "top1_rank": int(actual_ranks[0]),
        "top1_traded": bool(picks["triggered"].iloc[0]),
        "mean_pick_rank": float(actual_ranks.mean()),
        "best_pick_rank": int(actual_ranks.min()),
        "mrr": float(1.0 / actual_ranks.min()),
        "ndcg": _ndcg(actual_ranks, k),
        "picked_return_pct": float(picks["day_return"].sum() * 100),
        "actual_top5_return_pct": float(day.nsmallest(k, "rank")["day_return"].sum() * 100),
        "picks": list(picks["strategy"]),
        "scores": [round(float(s), 4) for s in picks["score"]],
    }


def walk_forward(labelled: pd.DataFrame, predictors: list[Predictor], k: int = K,
                 warmup_days: int = 60, abstain_below: dict | None = None,
                 progress=None, rank_col: str = "rank",
                 candidates_traded_only: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (per-day records, summary per predictor)."""
    abstain_below = abstain_below or {}
    d = labelled.sort_values(["date", "ticker"])
    dates = sorted(d["date"].unique())
    records = []
    for i, date in enumerate(dates):
        day_all = d[d["date"] == date]
        scoring = i >= warmup_days                 # earlier days only teach, never score
        for ticker, day in day_all.groupby("ticker", sort=True):
            scorable = day[day["triggered"] == 1] if candidates_traded_only else day
            if scoring and len(scorable) > k:
                prior = k / len(scorable)
                for p in predictors:
                    res = evaluate_day(scorable, p.score(scorable, prior), k,
                                       abstain_below.get(p.name), rank_col)
                    if res is not None:
                        records.append({"date": date, "ticker": ticker, "predictor": p.name,
                                        "candidates": len(scorable), "traded": int(day["triggered"].sum()), **res})
            for p in predictors:                    # learn only after scoring
                p.update(day)
        if progress and i % 50 == 0:
            progress(f"{i + 1}/{len(dates)} days")
    rec = pd.DataFrame(records)
    return rec, summarize(rec)


def summarize(rec: pd.DataFrame) -> pd.DataFrame:
    if rec.empty:
        return pd.DataFrame()
    scored = rec[~rec["abstained"]]
    rows = []
    for name, g in scored.groupby("predictor"):
        total = int((rec["predictor"] == name).sum())
        rows.append({
            "predictor": name,
            "days_scored": len(g),
            "coverage": round(len(g) / total, 3) if total else 0.0,
            "precision@5": round(float(g["precision_at_k"].mean()), 4),
            "recall@5": round(float(g["recall_at_k"].mean()), 4),
            "top1_hit": round(float(g["top1_hit"].mean()), 4),
            "median_top1_rank": float(g["top1_rank"].median()),
            "mean_pick_rank": round(float(g["mean_pick_rank"].mean()), 1),
            "MRR": round(float(g["mrr"].mean()), 4),
            "NDCG@5": round(float(g["ndcg"].mean()), 4),
            "picked_ret%/day": round(float(g["picked_return_pct"].mean()), 3),
            "best_possible%/day": round(float(g["actual_top5_return_pct"].mean()), 3),
        })
    return pd.DataFrame(rows).sort_values("precision@5", ascending=False).set_index("predictor")


def rolling_scorecard(rec: pd.DataFrame, predictor: str, windows=(5, 20, 50, 100)) -> pd.DataFrame:
    """Recent form of one predictor -- the daily scorecard the spec asks for."""
    g = rec[(rec["predictor"] == predictor) & (~rec["abstained"])].sort_values("date")
    out = {}
    for w in windows:
        tail = g.tail(w * g["ticker"].nunique())
        out[f"last_{w}d"] = {"precision@5": round(float(tail["precision_at_k"].mean()), 4),
                             "top1_hit": round(float(tail["top1_hit"].mean()), 4),
                             "median_top1_rank": float(tail["top1_rank"].median())}
    return pd.DataFrame(out).T
