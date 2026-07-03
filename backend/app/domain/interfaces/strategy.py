"""
Strategy contract.

A Strategy composes Indicators and Filters into entry/exit decisions
and emits Trades. It does NOT calculate its own performance metrics —
that responsibility belongs to the Metrics Engine, so every strategy
gets identical, comparable reporting for free.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd


class TradeDirection(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True)
class Trade:
    """A single completed (or open) trade produced by a strategy."""

    entry_time: datetime
    exit_time: datetime | None
    direction: TradeDirection
    entry_price: float
    exit_price: float | None
    quantity: float
    pnl: float | None = None
    exit_reason: str | None = None  # e.g. "stop_loss", "take_profit", "signal_exit"


@dataclass(frozen=True)
class StrategyMetadata:
    name: str  # unique slug, derived from folder name
    display_name: str
    description: str = ""
    category: str = "general"
    indicators_used: list[str] = field(default_factory=list)
    default_params: dict[str, Any] = field(default_factory=dict)
    # Plain-language bullet points shown in the UI's Info tab -- kept as
    # data on the metadata (not derived/generated) so they can only ever
    # describe what generate_entries/generate_exits actually do, right
    # next to the code that does it.
    entry_conditions: list[str] = field(default_factory=list)
    exit_conditions: list[str] = field(default_factory=list)


class Strategy(ABC):
    """
    Abstract base class every strategy must implement.

    Each concrete strategy lives in its own folder under app/strategies/
    and contains ONLY:
        - metadata (what it is)
        - parameters (what can be tuned)
        - entry logic
        - exit logic

    It must NOT re-implement indicator math or duplicate filter logic —
    it imports Indicators and Filters and composes them.
    """

    @property
    @abstractmethod
    def metadata(self) -> StrategyMetadata:
        raise NotImplementedError

    @abstractmethod
    def prepare(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        """
        Attach whatever indicator columns this strategy needs.
        Must return a NEW DataFrame (never mutate input).
        """
        raise NotImplementedError

    @abstractmethod
    def generate_entries(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        """
        Per-bar entry signal.

        Returns an object-dtype Series aligned to df.index where each
        value is either:
            - a TradeDirection (LONG or SHORT) -> enter a position here
            - None / falsy -> no entry signal on this bar

        Using TradeDirection instead of a plain bool lets a single
        strategy support long, short, or both without a separate
        "direction" signal channel.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_exits(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        """
        Boolean Series: True where an open position (long or short)
        should be closed. Exit logic is intentionally direction-agnostic
        here — the execution engine applies it only while a position is
        open, regardless of which side it's on.
        """
        raise NotImplementedError

    def run(
        self,
        df: pd.DataFrame,
        params: dict[str, Any],
        execution_config: "ExecutionConfig | None" = None,
    ) -> list[Trade]:
        """
        Default orchestration: prepare -> entries -> exits -> trades.
        Most strategies won't need to override this; it's here (not in
        the runner) so a strategy CAN override the whole lifecycle for
        unusual cases without touching shared engine code.
        """
        from app.strategies.execution import ExecutionConfig, simulate_trades  # local import avoids cycles

        enriched = self.prepare(df, params)
        entries = self.generate_entries(enriched, params)
        exits = self.generate_exits(enriched, params)
        return simulate_trades(enriched, entries, exits, execution_config or ExecutionConfig())

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        merged = {**self.metadata.default_params, **(params or {})}
        return merged
