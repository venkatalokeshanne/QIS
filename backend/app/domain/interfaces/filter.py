"""
Filter contract.

A Filter answers a single boolean question about market state at a
given row (e.g. "is price above VWAP?"). Filters never combine logic
themselves — that composition happens in a Strategy. This keeps each
filter a small, single-responsibility, independently testable unit.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class FilterMetadata:
    name: str
    display_name: str
    description: str = ""
    category: str = "general"
    default_params: dict[str, Any] = field(default_factory=dict)


class Filter(ABC):
    """
    Abstract base class for all filters.

    Contract:
        - `apply` takes an indicator-enriched DataFrame and returns a
          pandas Series of booleans (one per row), aligned to df.index.
        - Filters may depend on indicator columns already being present
          on the DataFrame (e.g. an "EMA20 > EMA50" filter expects
          'ema_20' and 'ema_50' columns). They do NOT compute indicators
          themselves — that's the Indicator's job.
    """

    @property
    @abstractmethod
    def metadata(self) -> FilterMetadata:
        raise NotImplementedError

    @abstractmethod
    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        """Return a boolean Series, True where the condition holds."""
        raise NotImplementedError

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        merged = {**self.metadata.default_params, **(params or {})}
        return merged
