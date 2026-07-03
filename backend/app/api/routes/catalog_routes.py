"""
Catalog routes.

Read-only discovery endpoints for the Strategy Library / Indicator
docs / metric definitions pages. Each just triggers discovery and
returns what the registry found — no business logic.
"""

from fastapi import APIRouter

from app.api.schemas.catalog_schemas import (
    FilterSummary,
    IndicatorSummary,
    MetricSummary,
    StrategySummary,
)
from app.filters.registry import discover_filters, list_filters
from app.indicators.registry import discover_indicators, list_indicators
from app.metrics.registry import discover_metrics, list_metric_definitions
from app.strategies.registry import discover_strategies, list_strategies

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("/indicators", response_model=list[IndicatorSummary])
def get_indicators():
    discover_indicators()
    return list_indicators()


@router.get("/filters", response_model=list[FilterSummary])
def get_filters():
    discover_filters()
    return list_filters()


@router.get("/strategies", response_model=list[StrategySummary])
def get_strategies():
    discover_strategies()
    return list_strategies()


@router.get("/metrics", response_model=list[MetricSummary])
def get_metrics():
    discover_metrics()
    return list_metric_definitions()
