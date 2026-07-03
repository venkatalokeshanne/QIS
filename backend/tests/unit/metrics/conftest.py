"""Shared fixtures for metrics tests."""

from datetime import datetime, timedelta

import pytest

from app.domain.interfaces.strategy import Trade, TradeDirection


def _trade(pnl, minutes_held=5, day_offset=0):
    entry = datetime(2024, 1, 2) + timedelta(days=day_offset)
    return Trade(
        entry_time=entry,
        exit_time=entry + timedelta(minutes=minutes_held),
        direction=TradeDirection.LONG,
        entry_price=100.0,
        exit_price=100.0 + pnl,
        quantity=1.0,
        pnl=pnl,
        exit_reason="signal_exit",
    )


@pytest.fixture
def mixed_trades():
    """3 wins, 2 losses. Net profit = 10+20+5-8-12 = 15."""
    return [_trade(10), _trade(-8), _trade(20), _trade(-12), _trade(5)]


@pytest.fixture
def all_winning_trades():
    return [_trade(10), _trade(5), _trade(15)]


@pytest.fixture
def empty_trades():
    return []
