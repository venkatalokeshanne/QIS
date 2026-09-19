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
