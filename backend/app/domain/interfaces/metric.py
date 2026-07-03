"""
Metric contract.

A Metric turns a MetricsContext (trades + derived series) into a single
number describing one facet of performance. Metrics are independent of
strategies entirely — they only ever see Trade objects and a starting
capital, which is what lets every strategy share identical reporting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.metrics.context import MetricsContext


@dataclass(frozen=True)
class MetricMetadata:
    name: str
    display_name: str
    description: str = ""
    category: str = "general"
    higher_is_better: bool = True
    # Format hint for the frontend table (e.g. "currency", "percent", "ratio", "count", "duration_minutes")
    format: str = "number"
    extra: dict[str, Any] = field(default_factory=dict)


class Metric(ABC):
    """
    Abstract base class for all metrics.

    Contract:
        - `calculate` receives a fully-built MetricsContext and returns
          a single float, or None if undefined for this set of trades
          (e.g. profit factor with zero losing trades).
    """

    @property
    @abstractmethod
    def metadata(self) -> MetricMetadata:
        raise NotImplementedError

    @abstractmethod
    def calculate(self, context: MetricsContext) -> float | None:
        raise NotImplementedError
