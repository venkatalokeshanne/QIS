"""Strategy Selection Engine API (spec 51): catalog, validation, response shape."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.strategy_engine.data.store import DEFAULT_DB


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_catalog_lists_every_strategy(client):
    r = client.get("/api/strategy-selection/catalog")
    assert r.status_code == 200
    body = r.json()
    assert body["version"] and len(body["strategies"]) == 81
    assert {"id", "name", "family", "timeframes", "runnable"} <= set(body["strategies"][0])


def test_bad_timeframe_is_rejected(client):
    assert client.get("/api/strategy-selection/AAPL", params={"timeframe": "7m"}).status_code == 422


def test_bad_timestamp_is_rejected(client):
    r = client.get("/api/strategy-selection/AAPL", params={"timeframe": "5m", "timestamp": "yesterday-ish"})
    assert r.status_code == 422


@pytest.mark.skipif(not DEFAULT_DB.exists(), reason="no local bar store")
def test_selection_response_shape(client):
    r = client.get("/api/strategy-selection/AAPL", params={"timeframe": "5m", "timestamp": "2026-09-18T10:00"})
    assert r.status_code == 200
    b = r.json()
    assert b["status"] in ("QUALIFIED_STRATEGIES_AVAILABLE", "NO_QUALIFIED_STRATEGY", "DATA_INSUFFICIENT")
    assert len(b["qualified_strategies"]) + len(b["rejected_strategies"]) == 81 or b["status"] == "DATA_INSUFFICIENT"
    assert {"configuration_version", "catalog_version", "data_version"} <= set(b["versions"])
    for q in b["qualified_strategies"]:
        assert q["why"] and q["why"][-1] == "Result: QUALIFIED"


@pytest.mark.skipif(not DEFAULT_DB.exists(), reason="no local bar store")
def test_day_replay(client):
    r = client.get("/api/strategy-selection/replay/AAPL", params={"date": "2026-09-14", "timeframes": "15m,65m"})
    assert r.status_code == 200
    b = r.json()
    assert b["status"] == "OK" and b["decision_time"] == "09:25"
    assert [t["timeframe"] for t in b["timeframes"]] == ["15m", "65m"]
    picked_ids = {p["strategy_id"] for t in b["timeframes"] for p in t["picked"]}
    for t in b["timeframes"]:
        for trade in t["trades"]:
            assert trade["entry"][:10] == "2026-09-14"                  # entered on the replayed day
            assert trade["entry"][11:] >= "09:25"                       # never before the decision
            assert trade["picked"] == (trade["strategy_id"] in picked_ids)
    engine = b["summary"]["engine"]
    picked_trades = [tr for t in b["timeframes"] for tr in t["trades"] if tr["picked"]]
    assert engine["trades"] == len(picked_trades)
    assert engine["total_return_pct"] == pytest.approx(sum(t["return_pct"] for t in picked_trades), abs=0.01)


def test_day_replay_rejects_a_bad_date(client):
    assert client.get("/api/strategy-selection/replay/AAPL", params={"date": "14-09-2026"}).status_code == 422
    assert client.get("/api/strategy-selection/replay/AAPL",
                      params={"date": "2026-09-14", "timeframes": "7m"}).status_code == 422
