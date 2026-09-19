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
    run against a synthetic in-memory frame instead of a real Twelve Data call."""
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


def test_run_backtest_isolates_one_failed_ticker_from_the_rest(client, monkeypatch):
    """A bad/unlucky ticker's fetch failure shouldn't take down the
    whole batch response -- confirm the other tickers still come back
    successfully and the bad one is reported in failed_symbols instead
    of the whole request erroring out."""
    from app.api.routes import backtest_routes

    monkeypatch.setattr(backtest_routes, "_FETCH_RETRY_DELAY_SECONDS", 0)

    def fake_fetch(symbol, interval, start_date=None, end_date=None, **kwargs):
        if symbol == "BADTICKER":
            raise RuntimeError("no data for this symbol")
        return _synthetic_bars()

    monkeypatch.setattr(backtest_routes, "fetch_backtest_bars", fake_fetch)

    resp = client.post(
        "/api/backtests/run",
        json={"symbols": ["AAPL", "BADTICKER", "MSFT"], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["failed_symbols"] == ["BADTICKER"]
    assert {t["symbol"] for t in body["ticker_results"]} == {"AAPL", "MSFT"}


def test_run_backtest_retries_a_transient_fetch_failure(client, monkeypatch):
    """Concurrent connections make a one-off dropped/rate-limited fetch
    more likely than the old one-at-a-time code ever saw -- confirm a
    symbol that fails once but succeeds on retry still makes it into
    the results, not into failed_symbols."""
    from app.api.routes import backtest_routes

    monkeypatch.setattr(backtest_routes, "_FETCH_RETRY_DELAY_SECONDS", 0)

    attempts = {"count": 0}

    def flaky_fetch(symbol, interval, start_date=None, end_date=None, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("transient connection drop")
        return _synthetic_bars()

    monkeypatch.setattr(backtest_routes, "fetch_backtest_bars", flaky_fetch)

    resp = client.post(
        "/api/backtests/run",
        json={"symbols": ["AAPL"], "interval": "5min", "strategy_names": ["orb_breakout"]},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["failed_symbols"] == []
    assert body["ticker_results"][0]["symbol"] == "AAPL"
    assert attempts["count"] == 2


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


# --- Daily Strategy Selector ---------------------------------------------


def _daily_selection_synthetic_bars(symbol, interval, start_date=None, end_date=None, **kwargs):
    """Already-normalized synthetic bars for the Daily Strategy
    Selector's tests -- a slow noise-free uptrend, long enough (when
    interval == '1day') for ADX/ATR regime classification to warm up,
    and with real intraday sessions for interval != '1day' so
    sma_cross/vwap_reversion/rsi_reversal have something to trade."""
    start = pd.Timestamp(start_date) if start_date else pd.Timestamp("2023-01-01")
    end = pd.Timestamp(end_date) if end_date else start + pd.Timedelta(days=30)

    if interval == "1day":
        idx = pd.DatetimeIndex(pd.bdate_range(start, end))
    else:
        days = pd.bdate_range(max(start, end - pd.Timedelta(days=5)), end)
        bars = []
        for d in days:
            bars.extend(
                pd.date_range(d + pd.Timedelta(hours=9, minutes=30), d + pd.Timedelta(hours=16), freq="5min", inclusive="left")
            )
        idx = pd.DatetimeIndex(bars)

    n = len(idx)
    closes = [100 + i * 0.05 for i in range(n)]
    df = pd.DataFrame(
        {"open": closes, "high": [c + 0.3 for c in closes], "low": [c - 0.3 for c in closes], "close": closes, "volume": [1000.0] * n}
    )
    df.index = idx
    return df


@pytest.fixture
def mock_daily_selection_bars(monkeypatch):
    """Monkeypatches fetch_backtest_bars/fetch_symbol_bars in every
    module the Daily Strategy Selector's services import them into, so
    /calibrate, /run, and /backtest all run their real pipeline against
    synthetic data instead of a live Twelve Data call."""
    from app.services import calibration_service, daily_selector_service

    monkeypatch.setattr(calibration_service, "fetch_backtest_bars", _daily_selection_synthetic_bars)
    monkeypatch.setattr(daily_selector_service, "fetch_backtest_bars", _daily_selection_synthetic_bars)
    monkeypatch.setattr(
        daily_selector_service, "fetch_symbol_bars", lambda symbol, interval, **kwargs: _daily_selection_synthetic_bars(symbol, interval)
    )
    return _daily_selection_synthetic_bars


_DAILY_SELECTION_STRATEGIES = ["sma_cross", "vwap_reversion", "rsi_reversal"]


def test_daily_selection_calibrate_and_profile_round_trip(client, mock_daily_selection_bars):
    resp = client.post(
        "/api/daily-selection/calibrate",
        json={
            "symbols": ["AAPL"],
            "interval": "5min",
            "start_date": "2024-02-01",
            "cutoff_date": "2024-03-15",
            "strategy_names": _DAILY_SELECTION_STRATEGIES,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["failed_symbols"] == []
    assert len(body["profiles"]) == 1
    profile = body["profiles"][0]
    assert profile["symbol"] == "AAPL"
    assert profile["default_strategy"] in _DAILY_SELECTION_STRATEGIES

    profile_resp = client.get("/api/daily-selection/profile/AAPL")
    assert profile_resp.status_code == 200
    assert profile_resp.json()["symbol"] == "AAPL"

    missing_resp = client.get("/api/daily-selection/profile/NOPE")
    assert missing_resp.status_code == 404


def test_daily_selection_run_returns_a_selection_for_a_calibrated_symbol(client, mock_daily_selection_bars):
    calibrate_resp = client.post(
        "/api/daily-selection/calibrate",
        json={
            "symbols": ["AAPL"],
            "interval": "5min",
            "start_date": "2024-02-01",
            "cutoff_date": "2024-03-15",
            "strategy_names": _DAILY_SELECTION_STRATEGIES,
        },
    )
    assert calibrate_resp.status_code == 200

    run_resp = client.post("/api/daily-selection/run", json={"symbols": ["AAPL", "UNCALIBRATED"], "interval": "5min"})
    assert run_resp.status_code == 200
    body = run_resp.json()
    assert body["failed_symbols"] == ["UNCALIBRATED"]
    assert len(body["selections"]) == 1
    selection = body["selections"][0]
    assert selection["symbol"] == "AAPL"
    assert selection["selected_strategy"] in _DAILY_SELECTION_STRATEGIES


def test_daily_selection_backtest_returns_switching_and_baseline_metrics(client, mock_daily_selection_bars):
    # Backtest reads the ALREADY-CALIBRATED profile -- calibrate first,
    # same as a real user would via the Calibrate tab.
    calibrate_resp = client.post(
        "/api/daily-selection/calibrate",
        json={
            "symbols": ["AAPL"],
            "interval": "5min",
            "start_date": "2024-01-01",
            "cutoff_date": "2024-03-01",
            "strategy_names": _DAILY_SELECTION_STRATEGIES,
        },
    )
    assert calibrate_resp.status_code == 200

    # Requested start (2024-01-01) predates the calibration cutoff
    # (2024-03-01) -- should be clamped up to the cutoff, not honored
    # verbatim, to preserve the out-of-sample guarantee.
    resp = client.post(
        "/api/daily-selection/backtest",
        json={"symbol": "AAPL", "interval": "5min", "start_date": "2024-01-01", "test_end_date": "2024-04-15"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["symbol"] == "AAPL"
    assert body["test_start"] == "2024-03-01"
    assert body["test_end"] == "2024-04-15"
    assert body["baseline_strategy"] in _DAILY_SELECTION_STRATEGIES
    assert "switching_metrics" in body and "baseline_metrics" in body
    assert len(body["switching_trades"]) == body["switching_trade_count"]
    for trade in body["switching_trades"]:
        assert trade["strategy_name"]
        assert trade["entry_time"] >= "2024-03-01"
    for segment in body["segments"]:
        assert segment["start_date"] >= "2024-03-01"
        assert segment["end_date"] <= "2024-04-15"


def test_daily_selection_backtest_returns_404_for_uncalibrated_symbol(client, mock_daily_selection_bars):
    resp = client.post(
        "/api/daily-selection/backtest",
        json={"symbol": "NEVERCALIBRATED", "interval": "5min", "start_date": "2024-01-01", "test_end_date": "2024-04-15"},
    )
    assert resp.status_code == 404
