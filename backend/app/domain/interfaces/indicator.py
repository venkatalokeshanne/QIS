"""
Indicator contract.

An Indicator is a pure mathematical transformation over OHLCV data.
It must NEVER contain trading logic (no buy/sell decisions).

Design rationale
-----------------
Every indicator implements the same `calculate()` interface so that:
- The engine can call any indicator without knowing its internals
  (Dependency Inversion: high-level code depends on this abstraction,
  not on concrete indicator classes).
- New indicators can be added by creating one file and registering
  via the IndicatorRegistry decorator, with no edits to existing code
  (Open/Closed Principle).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class IndicatorMetadata:
    """Descriptive metadata used by the frontend Strategy Library / docs."""

    name: str
    display_name: str
    description: str = ""
    category: str = "general"
    default_params: dict[str, Any] = field(default_factory=dict)


class Indicator(ABC):
    """
    Abstract base class for all indicators.

    Contract:
        - `calculate` takes a DataFrame with at least the OHLCV columns
          (open, high, low, close, volume) and returns a NEW DataFrame
          (never mutate the input in place) with additional column(s)
          containing the computed values.
        - `metadata` returns static info about the indicator for
          discovery, validation, and UI display.
    """

    @property
    @abstractmethod
    def metadata(self) -> IndicatorMetadata:
        """Return static metadata describing this indicator."""
        raise NotImplementedError

    @abstractmethod
    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        """
        Compute the indicator and return a new DataFrame with the
        result column(s) appended.

        Args:
            df: OHLCV dataframe (columns: open, high, low, close, volume).
            params: Indicator-specific parameters (e.g. {"period": 20}).

        Returns:
            A new DataFrame (copy) including the original columns plus
            the indicator's output column(s).
        """
        raise NotImplementedError

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Merge user-supplied params with defaults and validate types.
        Subclasses may override for custom validation; default behavior
        just fills in missing keys from metadata.default_params.
        """
        merged = {**self.metadata.default_params, **(params or {})}
        return merged
