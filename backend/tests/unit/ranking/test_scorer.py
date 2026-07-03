"""Tests for app.ranking.scorer."""

from app.ranking.models import RankingConfig
from app.ranking.scorer import score_results


def test_higher_net_profit_ranks_first():
    raw = [
        ("a", "Strategy A", {"net_profit": 100.0}, 5, [], None),
        ("b", "Strategy B", {"net_profit": 500.0}, 5, [], None),
        ("c", "Strategy C", {"net_profit": 200.0}, 5, [], None),
    ]
    config = RankingConfig(weights={"net_profit": 1.0}, min_trades=1)
    results = score_results(raw, config)

    assert [r.strategy_name for r in results] == ["b", "c", "a"]
    assert results[0].rank == 1
    assert results[0].overall_score > results[1].overall_score


def test_lower_is_better_metric_is_inverted():
    # max_drawdown: lower is better, so strategy with SMALLER drawdown should rank first.
    raw = [
        ("a", "Strategy A", {"max_drawdown": 30.0}, 5, [], None),
        ("b", "Strategy B", {"max_drawdown": 5.0}, 5, [], None),
    ]
    config = RankingConfig(weights={"max_drawdown": 1.0}, min_trades=1)
    results = score_results(raw, config)
    assert results[0].strategy_name == "b"


def test_strategies_below_min_trades_are_unscored_and_ranked_last():
    raw = [
        ("a", "Strategy A", {"net_profit": 1000.0}, 0, [], None),  # zero trades
        ("b", "Strategy B", {"net_profit": 10.0}, 5, [], None),
    ]
    config = RankingConfig(weights={"net_profit": 1.0}, min_trades=1)
    results = score_results(raw, config)

    assert results[0].strategy_name == "b"
    assert results[0].overall_score is not None
    assert results[-1].strategy_name == "a"
    assert results[-1].overall_score is None
    assert results[-1].rank is None


def test_missing_metric_values_do_not_crash_scoring():
    raw = [
        ("a", "Strategy A", {"net_profit": 100.0, "sharpe_ratio": None}, 5, [], None),
        ("b", "Strategy B", {"net_profit": 200.0, "sharpe_ratio": 1.5}, 5, [], None),
    ]
    config = RankingConfig(weights={"net_profit": 1.0, "sharpe_ratio": 1.0}, min_trades=1)
    results = score_results(raw, config)
    assert all(r.overall_score is not None for r in results)


def test_configurable_weights_change_the_ranking():
    raw = [
        ("a", "Strategy A", {"net_profit": 1000.0, "max_drawdown": 50.0}, 5, [], None),
        ("b", "Strategy B", {"net_profit": 100.0, "max_drawdown": 1.0}, 5, [], None),
    ]
    # Weighted entirely on profit -> a wins
    profit_heavy = score_results(raw, RankingConfig(weights={"net_profit": 1.0}, min_trades=1))
    assert profit_heavy[0].strategy_name == "a"

    # Weighted entirely on drawdown -> b wins
    risk_heavy = score_results(raw, RankingConfig(weights={"max_drawdown": 1.0}, min_trades=1))
    assert risk_heavy[0].strategy_name == "b"


def test_all_equal_values_produce_tied_scores_without_crashing():
    raw = [
        ("a", "Strategy A", {"net_profit": 100.0}, 5, [], None),
        ("b", "Strategy B", {"net_profit": 100.0}, 5, [], None),
    ]
    results = score_results(raw, RankingConfig(weights={"net_profit": 1.0}, min_trades=1))
    assert results[0].overall_score == results[1].overall_score
