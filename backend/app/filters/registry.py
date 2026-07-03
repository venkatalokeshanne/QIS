"""
Filter registry singleton. Same discovery pattern as indicators and
strategies — drop a file in app/filters/ that registers itself.
"""

from app.core.registry import Registry, discover_package
from app.domain.interfaces.filter import Filter

filter_registry: Registry[Filter] = Registry(kind="filter")


def get_filter(name: str) -> Filter:
    cls = filter_registry.get(name)
    return cls()


def list_filters() -> list[dict]:
    result = []
    for name, cls in filter_registry.all().items():
        meta = cls().metadata
        result.append(
            {
                "name": meta.name,
                "display_name": meta.display_name,
                "description": meta.description,
                "category": meta.category,
                "default_params": meta.default_params,
            }
        )
    return sorted(result, key=lambda x: x["name"])


def discover_filters() -> None:
    discover_package("app.filters")
