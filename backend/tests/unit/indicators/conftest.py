"""Fixtures specific to the indicators test directory (see tests/conftest.py for the shared ohlcv_df fixture)."""

import pytest

from app.indicators.registry import discover_indicators


@pytest.fixture(autouse=True)
def _ensure_indicators_discovered():
    """
    Several tests in this directory call get_indicator()/list_indicators()
    directly, relying on some OTHER test having already called
    discover_indicators() first to populate the registry. That's a latent
    ordering dependency, not a guarantee -- so make it explicit and
    unconditional here instead of leaving it to test execution order.
    """
    discover_indicators()
