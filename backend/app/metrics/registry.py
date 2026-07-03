"""
Metric registry singleton.

Same discovery pattern as indicators and strategies: drop a file in
app/metrics/ that registers itself, and it's picked up automatically.
"""

from app.core.registry import Registry, discover_package
from app.domain.interfaces.metric import Metric

metric_registry: Registry[Metric] = Registry(kind="metric")


def list_metric_definitions() -> list[dict]:
    """Metadata for every registered metric (for the API/UI)."""
    result = []
    for name, cls in metric_registry.all().items():
        meta = cls().metadata
        result.append(
            {
                "name": meta.name,
                "display_name": meta.display_name,
                "description": meta.description,
                "category": meta.category,
                "higher_is_better": meta.higher_is_better,
                "format": meta.format,
            }
        )
    return sorted(result, key=lambda x: x["name"])


def discover_metrics() -> None:
    discover_package("app.metrics")
