"""
End-to-end API tests using FastAPI's TestClient — proves the full
stack (routes -> services -> repositories -> domain logic) works
together over real HTTP requests, with storage redirected to a temp
directory so tests don't touch real app data.
"""

import io

import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings


def _synthetic_csv() -> bytes:
    lines = ["Date,Open,High,Low,Close,Volume"]
    price = 100.0
    for day in (2, 3):
        for minute in range(40):
            price += 0.1 if minute % 3 else -0.05
            ts = f"2024-01-{day:02d} 09:{minute:02d}:00" if minute < 60 else None
            lines.append(f"2024-01-{day:02d} 09:{minute:02d}," f"{price},{price+0.3},{price-0.3},{price+0.1},500")
    return ("\n".join(lines) + "\n").encode()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    monkeypatch.setattr(settings, "dataset_storage_dir", tmp_path / "data" / "datasets")

    from app.main import app  # import after monkeypatch so ensure_dirs uses temp paths

    with TestClient(app) as c:
        yield c


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_catalog_endpoints_return_discovered_items(client):
    assert any(i["name"] == "ema" for i in client.get("/api/catalog/indicators").json())
    assert any(f["name"] == "gap_up" for f in client.get("/api/catalog/filters").json())
    assert any(s["name"] == "orb_breakout" for s in client.get("/api/catalog/strategies").json())
    assert any(m["name"] == "sharpe_ratio" for m in client.get("/api/catalog/metrics").json())


def test_upload_list_preview_and_delete_dataset(client):
    csv_bytes = _synthetic_csv()
    upload_resp = client.post(
        "/api/datasets",
        files={"file": ("prices.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "My Test Dataset"},
    )
    assert upload_resp.status_code == 200
    dataset_id = upload_resp.json()["dataset"]["id"]

    list_resp = client.get("/api/datasets")
    assert any(d["id"] == dataset_id for d in list_resp.json())

    preview_resp = client.get(f"/api/datasets/{dataset_id}/preview?rows=5")
    assert len(preview_resp.json()["rows"]) == 5

    delete_resp = client.delete(f"/api/datasets/{dataset_id}")
    assert delete_resp.status_code == 204
    assert client.get(f"/api/datasets/{dataset_id}").status_code == 404


def test_upload_invalid_csv_returns_422(client):
    bad_csv = b"Date,Open\n2024-01-02,100\n"
    resp = client.post(
        "/api/datasets",
        files={"file": ("bad.csv", io.BytesIO(bad_csv), "text/csv")},
        data={"name": "Bad Dataset"},
    )
    assert resp.status_code == 422
    assert "issues" in resp.json()


def test_run_backtest_end_to_end(client):
    csv_bytes = _synthetic_csv()
    upload_resp = client.post(
        "/api/datasets",
        files={"file": ("prices.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "Backtest Dataset"},
    )
    dataset_id = upload_resp.json()["dataset"]["id"]

    run_resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": [dataset_id], "strategy_names": None},
    )
    assert run_resp.status_code == 200
    body = run_resp.json()

    assert len(body["dataset_results"]) == 1
    dataset_result = body["dataset_results"][0]
    assert dataset_result["dataset_id"] == dataset_id
    assert dataset_result["dataset_name"] == "Backtest Dataset"

    names = {r["strategy_name"] for r in dataset_result["results"]}
    assert "orb_breakout" in names
    assert "hma_trend_cross" in names
    # Ranked results (if any scored) should have rank 1 first.
    scored = [r for r in dataset_result["results"] if r["overall_score"] is not None]
    if scored:
        assert scored[0]["rank"] == 1


def test_run_backtest_breakdown_by_month(client):
    csv_bytes = _synthetic_csv()
    upload_resp = client.post(
        "/api/datasets",
        files={"file": ("prices.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "Monthly Breakdown Dataset"},
    )
    dataset_id = upload_resp.json()["dataset"]["id"]

    # Default: no breakdown requested -> monthly_metrics stays absent.
    default_resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": [dataset_id], "strategy_names": ["orb_breakout"]},
    )
    assert default_resp.json()["dataset_results"][0]["results"][0]["monthly_metrics"] is None

    # Requested: monthly_metrics is a dict of "YYYY-MM" -> metrics dict.
    monthly_resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": [dataset_id], "strategy_names": ["orb_breakout"], "breakdown_by_month": True},
    )
    assert monthly_resp.status_code == 200
    result = monthly_resp.json()["dataset_results"][0]["results"][0]
    assert result["monthly_metrics"] is not None
    for month_key, month_metrics in result["monthly_metrics"].items():
        assert month_key.count("-") == 1  # "YYYY-MM"
        assert "net_profit" in month_metrics
        assert "total_trades" in month_metrics


def test_run_backtest_multiple_datasets_returns_one_result_set_per_dataset(client):
    csv_bytes = _synthetic_csv()
    ids = []
    for name in ("Ticker A", "Ticker B"):
        upload_resp = client.post(
            "/api/datasets",
            files={"file": ("prices.csv", io.BytesIO(csv_bytes), "text/csv")},
            data={"name": name},
        )
        ids.append(upload_resp.json()["dataset"]["id"])

    run_resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": ids, "strategy_names": ["orb_breakout"]},
    )
    assert run_resp.status_code == 200
    body = run_resp.json()

    assert [d["dataset_id"] for d in body["dataset_results"]] == ids
    assert [d["dataset_name"] for d in body["dataset_results"]] == ["Ticker A", "Ticker B"]
    for dataset_result in body["dataset_results"]:
        assert {r["strategy_name"] for r in dataset_result["results"]} == {"orb_breakout"}


def test_run_backtest_unknown_dataset_returns_404(client):
    resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": ["does-not-exist"], "strategy_names": ["orb_breakout"]},
    )
    assert resp.status_code == 404


def test_run_backtest_unknown_strategy_returns_404(client):
    csv_bytes = _synthetic_csv()
    upload_resp = client.post(
        "/api/datasets",
        files={"file": ("prices.csv", io.BytesIO(csv_bytes), "text/csv")},
        data={"name": "D"},
    )
    dataset_id = upload_resp.json()["dataset"]["id"]

    resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": [dataset_id], "strategy_names": ["not_real"]},
    )
    assert resp.status_code == 404


def test_run_backtest_requires_at_least_one_dataset(client):
    resp = client.post(
        "/api/backtests/run",
        json={"dataset_ids": [], "strategy_names": ["orb_breakout"]},
    )
    assert resp.status_code == 422




def test_create_list_and_delete_watch(client):
    create_resp = client.post(
        "/api/watches",
        json={
            "expo_push_token": "ExponentPushToken[abc123]",
            "symbol": "aapl",
            "strategy_name": "sma_cross",
            "strategy_params": {"fast_period": 3, "slow_period": 8},
            "interval": "5min",
        },
    )
    assert create_resp.status_code == 200
    watch = create_resp.json()
    assert watch["symbol"] == "AAPL"
    assert watch["interval"] == "5min"
    assert watch["last_notified_bar_time"] is None

    list_resp = client.get("/api/watches", params={"expo_push_token": "ExponentPushToken[abc123]"})
    assert list_resp.status_code == 200
    assert any(w["id"] == watch["id"] for w in list_resp.json())

    other_token_resp = client.get("/api/watches", params={"expo_push_token": "some-other-token"})
    assert other_token_resp.json() == []

    delete_resp = client.delete(f"/api/watches/{watch['id']}")
    assert delete_resp.status_code == 204
    assert client.get("/api/watches", params={"expo_push_token": "ExponentPushToken[abc123]"}).json() == []


def test_create_watch_rejects_invalid_interval(client):
    resp = client.post(
        "/api/watches",
        json={
            "expo_push_token": "ExponentPushToken[abc123]",
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
