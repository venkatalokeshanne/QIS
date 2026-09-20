"""
Phase 1 -- turn the historical backtests into labelled observations.

One row per (date, ticker, strategy): what that strategy's trades entered on
that day returned, and where that placed it against every other strategy that
was a candidate for the same ticker that day.

Ranking universe: all runnable strategies for the ticker, on every timeframe,
whether or not they triggered. A strategy that never fired scores 0.0 and
therefore ranks above the day's losers and below its winners -- the same way
it appears in an end-of-day backtest table. `triggered` keeps the two cases
distinguishable (spec: "strategy did not trigger" != "triggered and lost"),
so P(top5) can later be split into P(trigger) x P(top5 | triggered).

Targets, deliberately several (the raw rank is not trusted on its own):
    rank            1 = best return that day for that ticker
    top1/3/5/10     rank <= k
    top5_reliable   top5 AND the day's result came from >= min_trades trades
    positive        the day's return was > 0
    risk_adjusted   return per day of capital the trades tied up
"""

from __future__ import annotations

import pandas as pd

TOP_K = (1, 3, 5, 10)
MIN_TRADES_RELIABLE = 1


def build_labels(obs: pd.DataFrame, min_trades: int = MIN_TRADES_RELIABLE) -> pd.DataFrame:
    """`obs` = the research dataset (one row per ticker/timeframe/strategy/day,
    features point-in-time as of 09:25, outcome = that day's trades)."""
    d = obs.copy()
    d["triggered"] = (d["n_today"] > 0).astype(int)
    d["day_return"] = d["ret_today"].fillna(0.0)
    d["capital_days"] = d["hold_days_today"].fillna(0.0)
    d["risk_adjusted"] = d["day_return"] / d["capital_days"].where(d["capital_days"] > 0)

    # Rank within (date, ticker). Ties -- above all, the many 0.0 rows for
    # strategies that did not fire -- are broken by strategy_id so the label is
    # deterministic and reproducible, never by anything from the future.
    order = d.sort_values(["date", "ticker", "day_return", "strategy_id"],
                          ascending=[True, True, False, True])
    order["rank"] = order.groupby(["date", "ticker"]).cumcount() + 1
    d = order
    d["candidates"] = d.groupby(["date", "ticker"])["strategy_id"].transform("size")

    for k in TOP_K:
        d[f"top{k}"] = (d["rank"] <= k).astype(int)
    d["top5_reliable"] = ((d["rank"] <= 5) & (d["n_today"] >= min_trades)).astype(int)
    d["positive"] = (d["day_return"] > 0).astype(int)
    # percentile target: 1.0 = best of the day, 0.0 = worst
    d["rank_pct"] = 1 - (d["rank"] - 1) / (d["candidates"] - 1).clip(lower=1)

    # Ranking among the strategies that ACTUALLY TRADED. Strategies that did
    # not fire score exactly 0.0, so on a day when fewer than five made money
    # they occupy top-5 slots by doing nothing, and which of them lands there
    # is decided by the tie-break rather than by merit. That is a property of
    # the ranking, not a signal to learn, so the honest question -- which of
    # the strategies that trade will finish top five -- gets its own label.
    traded = d[d["n_today"] > 0].copy()
    traded["rank_traded"] = traded.sort_values(["date", "ticker", key, "strategy"],
                                               ascending=[True, True, False, True])         .groupby(["date", "ticker"]).cumcount() + 1
    d = d.merge(traded[["date", "ticker", "strategy", "rank_traded"]], on=["date", "ticker", "strategy"], how="left")
    d["traded_candidates"] = d.groupby(["date", "ticker"])["n_today"].transform(lambda s: int((s > 0).sum()))
    d["top5_traded"] = ((d["rank_traded"] <= 5) & d["rank_traded"].notna()).astype(int)
    d["top1_traded"] = ((d["rank_traded"] == 1)).astype(int)
    return d.reset_index(drop=True)


def label_report(d: pd.DataFrame) -> dict:
    """Sanity numbers a model must be judged against."""
    per_day = d.groupby(["date", "ticker"])
    traded = d[d["triggered"] == 1]
    top5 = d[d["top5"] == 1]
    return {
        "observations": len(d),
        "day_tickers": per_day.ngroups,
        "days": d["date"].nunique(),
        "tickers": d["ticker"].nunique(),
        "strategies": d["strategy"].nunique() if "strategy" in d else d["strategy_id"].nunique(),
        "mean_candidates_per_day": round(float(per_day.size().mean()), 1),
        "mean_triggered_per_day": round(float(per_day["triggered"].sum().mean()), 1),
        "random_precision_at_5": round(5 / float(per_day.size().mean()), 4),
        "share_top5_that_traded": round(float(top5["triggered"].mean()), 4),
        "share_top5_with_one_trade": round(float((top5["n_today"] == 1).mean()), 4),
        "mean_top5_return_pct": round(float(top5["day_return"].mean()) * 100, 3),
        "mean_traded_return_pct": round(float(traded["day_return"].mean()) * 100, 3),
        "day_tickers_with_no_trades": int((per_day["triggered"].sum() == 0).sum()),
    }


def build_labels_from_daily(daily: pd.DataFrame, rank_by: str = "pnl",
                            min_trades: int = MIN_TRADES_RELIABLE) -> pd.DataFrame:
    """Labels straight from the daily_results table (see backtests.py).

    `rank_by` is "pnl" by default because that is what the Run Backtests page
    ranks on and therefore what "Top 5" means to the user; "return_pct" gives
    the same order whenever position sizing is uniform.
    """
    d = daily.copy()
    d["day_return"] = d["return_pct"].fillna(0.0)
    d["day_pnl"] = d["pnl"].fillna(0.0)
    d["n_today"] = d["trade_count"].fillna(0).astype(int)
    d["triggered"] = (d["n_today"] > 0).astype(int)
    d["capital_days"] = (d["hold_hours"].fillna(0.0) / 24).clip(lower=0)
    d["risk_adjusted"] = d["day_return"] / d["capital_days"].where(d["capital_days"] > 0)

    key = "day_pnl" if rank_by == "pnl" else "day_return"
    order = d.sort_values(["date", "ticker", key, "strategy"], ascending=[True, True, False, True])
    order["rank"] = order.groupby(["date", "ticker"]).cumcount() + 1
    d = order
    d["candidates"] = d.groupby(["date", "ticker"])["strategy"].transform("size")
    for k in TOP_K:
        d[f"top{k}"] = (d["rank"] <= k).astype(int)
    d["top5_reliable"] = ((d["rank"] <= 5) & (d["n_today"] >= min_trades)).astype(int)
    d["positive"] = (d["day_return"] > 0).astype(int)
    d["rank_pct"] = 1 - (d["rank"] - 1) / (d["candidates"] - 1).clip(lower=1)

    # Ranking among the strategies that ACTUALLY TRADED. Strategies that did
    # not fire score exactly 0.0, so on a day when fewer than five made money
    # they occupy top-5 slots by doing nothing, and which of them lands there
    # is decided by the tie-break rather than by merit. That is a property of
    # the ranking, not a signal to learn, so the honest question -- which of
    # the strategies that trade will finish top five -- gets its own label.
    traded = d[d["n_today"] > 0].copy()
    traded["rank_traded"] = traded.sort_values(["date", "ticker", key, "strategy"],
                                               ascending=[True, True, False, True])         .groupby(["date", "ticker"]).cumcount() + 1
    d = d.merge(traded[["date", "ticker", "strategy", "rank_traded"]], on=["date", "ticker", "strategy"], how="left")
    d["traded_candidates"] = d.groupby(["date", "ticker"])["n_today"].transform(lambda s: int((s > 0).sum()))
    d["top5_traded"] = ((d["rank_traded"] <= 5) & d["rank_traded"].notna()).astype(int)
    d["top1_traded"] = ((d["rank_traded"] == 1)).astype(int)
    return d.reset_index(drop=True)
