"""
Indicator registry singleton.

Importing this module triggers discovery of every file under
app/indicators/ — so adding a new indicator is just "create one file
that registers itself," with no edits needed here.
"""

from app.core.registry import Registry, discover_package
from app.domain.interfaces.indicator import Indicator

indicator_registry: Registry[Indicator] = Registry(kind="indicator")


def get_indicator(name: str) -> Indicator:
    """Instantiate and return an indicator by its registered name."""
    cls = indicator_registry.get(name)
    return cls()


def list_indicators() -> list[dict]:
    """Return metadata for every registered indicator (for the API/UI)."""
    result = []
    for name, cls in indicator_registry.all().items():
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


def discover_indicators() -> None:
    discover_package("app.indicators")
