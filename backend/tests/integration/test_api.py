"""
End-to-end API tests using FastAPI's TestClient — proves the full
stack (routes -> services -> repositories -> domain logic) works
together over real HTTP requests, with storage redirected to a temp
directory so tests don't touch real app data.
"""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings


def _synthetic_bars(days=(2, 3)) -> pd.DataFrame:
    """Already normalized (DatetimeIndex, lowercase OHLCV columns) --
    fetch_backtest_bars is mocked out entirely in these tests, so this
    stands in for what its normalize_ohlcv pipeline would have produced."""
    dates = []
    opens, highs, lows, closes, volumes = [], [], [], [], []
    price = 100.0
    for day in days:
        for minute in range(40):
            price += 0.1 if minute % 3 else -0.05
            dates.append(pd.Timestamp(f"2024-01-{day:02d} 09:{minute:02d}:00"))
            opens.append(price)
            highs.append(price + 0.3)
            lows.append(price - 0.3)
            closes.append(price + 0.1)
            volumes.append(500)
    df = pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes})
    df.index = pd.DatetimeIndex(dates)
    return df


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")

    from app.main import app  # import after monkeypatch so ensure_dirs uses temp paths

    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_backtest_bars(monkeypatch):
    """Monkeypatches backtest_routes.fetch_backtest_bars so backtest tests
    run against a synthetic in-memory frame instead of a real Tastytrade call."""
    from app.api.routes import backtest_routes

    def fake_fetch(symbol, interval, start_date=None, end_date=None, **kwargs):
        return _synthetic_bars()

    monkeypatch.setattr(backtest_routes, "fetch_backtest_bars", fake_fetch)
    return fake_fetch


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_catalog_endpoints_return_discovered_items(client):
    assert any(i["name"] == "ema" for i in client.get("/api/catalog/indicators").json())
    assert any(f["name"] == "gap_up" for f in client.get("/api/catalog/filters").json())
    assert any(s["name"] == "orb_breakout" for s in client.get("/api/catalog/strategies").json())
    assert any(m["name"] == "sharpe_ratio" for m in client.get("/api/catalog/metrics").json())


def test_run_backtest_end_to_end(client, mock_backtest_bars):
    run_resp = client.post(
        "/api/backtests/run",
        json={"symbols": ["AAPL"], "interval": "5min", "strategy_names": None},
    )
    assert run_resp.status_code == 200
    body = run_resp.json()

    assert len(body["ticker_results"]) == 1
    ticker_result = body["ticker_results"][0]
    assert ticker_result["symbol"] == "AAPL"

    names = {r["strategy_name"] for r in ticker_result["results"]}
    assert "orb_breakout" in names
    assert "hma_trend_cross" in names
    # Ranked results (if any scored) should have rank 1 first.
    scored = [r for r in ticker_result["results"] if r["overall_score"] is not None]
    if scored:
        assert scored[0]["rank"] == 1
    # /run no longer computes historical performance at all -- that's
    # the whole point of making it lazy (see
    # test_historical_performance_* below) -- so the field shouldn't
    # even be on this response anymore.
    assert "historical_metrics" not in ticker_result["results"][0]


def test_historical_performance_returns_a_three_month_window(client, mock_backtest_bars):
    resp = client.post(
        "/api/backtests/historical-performance",
        json={
            "symbol": "AAPL",
            "interval": "5min",
            "strategy_name": "orb_breakout",
            "end_date": "2026-08-03",
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["historical_metrics"] is not None
    assert "net_profit" in body["historical_metrics"]
    assert body["historical_trade_count"] is not None
    assert body["historical_period_start"] is not None
    assert body["historical_period_end"] is not None
    # Always sliced by month -- this is what lets Results.jsx show
    # consistency across the window, not just one aggregate number.
    assert body["historical_monthly_metrics"] is not None
    for month_key, month_metrics in body["historical_monthly_metrics"].items():
        assert month_key.count("-") == 1  # "YYYY-MM"
        assert "net_profit" in month_metrics


def test_historical_performance_fetches_only_a_three_month_window(client, monkeypatch):
    """Keep the on-demand comparison fetch bounded, and confirm it's
    exactly ONE fetch (see backtest_routes -- this is the whole reason
    it moved off the eager /run path)."""
    from app.api.routes import backtest_routes

    calls = []

    def fake_fetch(symbol, interval, start_date=None, end_date=None, **kwargs):
        calls.append((start_date, end_date))
        return _synthetic_bars()

    monkeypatch.setattr(backtest_routes, "fetch_backtest_bars", fake_fetch)
    response = client.post(
        "/api/backtests/historical-performance",
        json={
            "symbol": "AAPL",
            "interval": "5min",
            "strategy_name": "orb_breakout",
            "end_date": "2026-08-03",
        },
    )

    assert response.status_code == 200
    assert calls == [("2026-05-05", "2026-08-03")]  # exactly one, 90-day, fetch


def test_run_backtest_breakdown_by_month(client, mock_backtest_bars):
    # Default: no breakdown requested -> monthly_metrics stays absent.
    default_resp = client.post(
        "/api/backtests/run",
        json={"symbols": ["AAPL"], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )
    assert default_resp.json()["ticker_results"][0]["results"][0]["monthly_metrics"] is None

    # Requested: monthly_metrics is a dict of "YYYY-MM" -> metrics dict.
    monthly_resp = client.post(
        "/api/backtests/run",
        json={
            "symbols": ["AAPL"],
            "interval": "5min",
            "strategy_names": ["orb_breakout"],
            "breakdown_by_month": True,
        },
    )
    assert monthly_resp.status_code == 200
    result = monthly_resp.json()["ticker_results"][0]["results"][0]
    assert result["monthly_metrics"] is not None
    for month_key, month_metrics in result["monthly_metrics"].items():
        assert month_key.count("-") == 1  # "YYYY-MM"
        assert "net_profit" in month_metrics
        assert "total_trades" in month_metrics


def test_run_backtest_fetches_multiple_symbols_concurrently(client, monkeypatch):
    """The whole point of the concurrent fetch -- confirm two ticker
    fetches actually overlap in time, not just that the response is
    still correct (test_run_backtest_multiple_symbols_... below covers
    correctness/ordering already)."""
    import time

    from app.api.routes import backtest_routes

    active = []
    max_concurrent = []

    def fake_fetch(symbol, interval, start_date=None, end_date=None, **kwargs):
        active.append(symbol)
        max_concurrent.append(len(active))
        time.sleep(0.1)  # long enough for other concurrent fetches to overlap
        active.remove(symbol)
        return _synthetic_bars()

    monkeypatch.setattr(backtest_routes, "fetch_backtest_bars", fake_fetch)

    resp = client.post(
        "/api/backtests/run",
        json={
            "symbols": ["AAPL", "MSFT", "TSLA", "QCOM"],
            "interval": "5min",
            "strategy_names": ["orb_breakout"],
        },
    )

    assert resp.status_code == 200
    assert len(resp.json()["ticker_results"]) == 4
    assert max(max_concurrent) > 1  # at least two fetches were in flight at once


def test_run_backtest_computes_strategies_via_the_process_pool(client, mock_backtest_bars):
    """Strategy execution is CPU-bound, unlike the fetch above -- letting
    it run unbounded in THREADS alongside 8 concurrent fetches is what
    caused the 90-125s-per-ticker thrashing (and an outright 502) that
    this process pool fixes (threads can't give real parallelism for
    CPU-bound work; separate processes can). A worker's own closures
    can't cross the process boundary (unlike the thread-based version
    this replaced), so this checks pool wiring/correctness end-to-end
    with the real run_strategies instead of tracking a monkeypatched one."""
    from app.api.routes import backtest_routes
    from app.config.settings import settings

    assert backtest_routes._strategy_pool is not None
    assert backtest_routes._strategy_pool._max_workers == settings.strategy_worker_processes

    resp = client.post(
        "/api/backtests/run",
        json={
            "symbols": ["AAPL", "MSFT", "TSLA", "QCOM", "NVDA", "AMD"],
            "interval": "5min",
            "strategy_names": ["orb_breakout"],
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["ticker_results"]) == 6
    for ticker_result in body["ticker_results"]:
        assert len(ticker_result["results"]) == 1
        assert ticker_result["results"][0]["strategy_name"] == "orb_breakout"


def test_run_backtest_multiple_symbols_returns_one_result_set_per_symbol(client, mock_backtest_bars):
    run_resp = client.post(
        "/api/backtests/run",
        json={"symbols": ["AAPL", "TSLA"], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )
    assert run_resp.status_code == 200
    body = run_resp.json()

    assert [t["symbol"] for t in body["ticker_results"]] == ["AAPL", "TSLA"]
    for ticker_result in body["ticker_results"]:
        assert {r["strategy_name"] for r in ticker_result["results"]} == {"orb_breakout"}


def test_run_backtest_unknown_strategy_returns_404(client, mock_backtest_bars):
    resp = client.post(
        "/api/backtests/run",
        json={"symbols": ["AAPL"], "interval": "5min", "strategy_names": ["not_real"]},
    )
    assert resp.status_code == 404


def test_run_backtest_requires_at_least_one_symbol(client):
    resp = client.post(
        "/api/backtests/run",
        json={"symbols": [], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )
    assert resp.status_code == 422


def test_create_list_and_delete_watch(client):
    create_resp = client.post(
        "/api/watches",
        json={
            "symbol": "aapl",
            "strategy_name": "sma_cross",
            "strategy_params": {"fast_period": 3, "slow_period": 8},
            "interval": "5min",
            "execution": {"capital": 5000.0, "direction_filter": "short_only"},
        },
    )
    assert create_resp.status_code == 200
    watch = create_resp.json()
    assert watch["symbol"] == "AAPL"
    assert watch["interval"] == "5min"
    assert watch["last_notified_bar_time"] is None
    assert watch["execution_settings"]["capital"] == 5000.0
    assert watch["execution_settings"]["direction_filter"] == "short_only"

    list_resp = client.get("/api/watches")
    assert list_resp.status_code == 200
    assert any(w["id"] == watch["id"] for w in list_resp.json())

    delete_resp = client.delete(f"/api/watches/{watch['id']}")
    assert delete_resp.status_code == 204
    assert all(w["id"] != watch["id"] for w in client.get("/api/watches").json())


def test_create_watch_rejects_invalid_interval(client):
    resp = client.post(
        "/api/watches",
        json={
            "symbol": "AAPL",
            "strategy_name": "sma_cross",
            "strategy_params": {},
            "interval": "1hour",
        },
    )
    assert resp.status_code == 422


def test_delete_missing_watch_returns_404(client):
    resp = client.delete("/api/watches/does-not-exist")
    assert resp.status_code == 404


def test_create_list_and_delete_level_watch(client):
    create_resp = client.post("/api/level-watches", json={"symbol": "aapl"})
    assert create_resp.status_code == 200
    watch = create_resp.json()
    assert watch["symbol"] == "AAPL"
    assert watch["last_levels"] is None

    list_resp = client.get("/api/level-watches")
    assert list_resp.status_code == 200
    assert any(w["id"] == watch["id"] for w in list_resp.json())

    delete_resp = client.delete(f"/api/level-watches/{watch['id']}")
    assert delete_resp.status_code == 204
    assert all(w["id"] != watch["id"] for w in client.get("/api/level-watches").json())


def test_create_duplicate_level_watch_returns_422(client):
    client.post("/api/level-watches", json={"symbol": "AAPL"})
    resp = client.post("/api/level-watches", json={"symbol": "aapl"})
    assert resp.status_code == 422


def test_delete_missing_level_watch_returns_404(client):
    resp = client.delete("/api/level-watches/does-not-exist")
    assert resp.status_code == 404


def test_signal_check_returns_result(client, monkeypatch):
    from datetime import datetime

    from app.api.routes import signal_routes
    from app.services.signal_service import SignalCheck

    def fake_check_signal(symbol, interval, strategy_name, strategy_params, execution_config=None, cached_df=None):
        return SignalCheck(
            symbol=symbol.upper(),
            interval=interval,
            strategy_name=strategy_name,
            as_of=datetime(2024, 1, 2, 9, 35),
            price=101.5,
            event="entry",
            direction="long",
            exit_reason=None,
            position="long",
        )

    monkeypatch.setattr(signal_routes, "check_signal", fake_check_signal)

    resp = client.post(
        "/api/signals/check",
        json={"symbol": "aapl", "interval": "5min", "strategy_name": "sma_cross", "strategy_params": {}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["symbol"] == "AAPL"
    assert body["event"] == "entry"
    assert body["direction"] == "long"
    assert body["exit_reason"] is None


def test_signal_check_propagates_unknown_strategy_as_404(client, monkeypatch):
    from app.api.routes import signal_routes
    from app.core.exceptions import NotFoundError

    def fake_check_signal(*a, **kw):
        raise NotFoundError("Unknown strategy 'not_a_real_strategy'.")

    monkeypatch.setattr(signal_routes, "check_signal", fake_check_signal)

    resp = client.post(
        "/api/signals/check",
        json={"symbol": "AAPL", "interval": "5min", "strategy_name": "not_a_real_strategy", "strategy_params": {}},
    )
    assert resp.status_code == 404


def test_day_prep_returns_200_and_well_formed_results(client, monkeypatch):
    from app.services import day_prep_service

    def fake_fetch_backtest_bars(symbol, interval, start_date=None, end_date=None, **kwargs):
        return _synthetic_bars()

    monkeypatch.setattr(day_prep_service, "fetch_backtest_bars", fake_fetch_backtest_bars)

    resp = client.post(
        "/api/scanner/day-prep",
        json={"symbols": ["AAPL"], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["failed_symbols"] == []
    # orb_breakout may or may not have actually traded on this synthetic
    # fixture (that depends on its own entry conditions, not something
    # this test should assume) -- but if it did, AAPL should show up
    # with a well-formed top_strategies entry, not a crash or garbage.
    for ticker in body["tickers"]:
        assert ticker["symbol"] == "AAPL"
        assert ticker["concentration_score"] >= 0
        assert len(ticker["top_strategies"]) >= 1
        assert ticker["top_strategies"][0]["strategy_name"] == "orb_breakout"


def test_day_prep_drops_symbol_with_no_trading_history(client, monkeypatch):
    from app.services import day_prep_service

    def fake_fetch_backtest_bars(symbol, interval, start_date=None, end_date=None, **kwargs):
        # Flat bars -- no strategy should find an entry here.
        idx = pd.date_range("2024-01-02 09:30", periods=40, freq="5min")
        return pd.DataFrame(
            {"open": [100.0] * 40, "high": [100.1] * 40, "low": [99.9] * 40, "close": [100.0] * 40, "volume": [500] * 40},
            index=idx,
        )

    monkeypatch.setattr(day_prep_service, "fetch_backtest_bars", fake_fetch_backtest_bars)

    resp = client.post(
        "/api/scanner/day-prep",
        json={"symbols": ["AAPL"], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )
    assert resp.status_code == 200
    assert resp.json()["tickers"] == []
