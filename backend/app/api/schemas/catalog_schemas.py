"""Pydantic schemas for catalog endpoints (indicators, filters, strategies)."""

from typing import Any

from pydantic import BaseModel


class IndicatorSummary(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    default_params: dict[str, Any]


class FilterSummary(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    default_params: dict[str, Any]


class StrategySummary(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    indicators_used: list[str]
    default_params: dict[str, Any]
    entry_conditions: list[str]
    exit_conditions: list[str]


class MetricSummary(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    higher_is_better: bool
    format: str
