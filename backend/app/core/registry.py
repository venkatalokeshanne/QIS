"""
Generic, reusable registry.

This single class powers indicator discovery, filter discovery, and
strategy discovery. Each domain gets its own registry instance, but the
discovery mechanism (decorator registration + package scanning) is
written once here — avoiding the duplicated "scan folder, import
module, find class" logic that would otherwise be copy-pasted three
times.
"""

import importlib
import pkgutil
from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """A name -> class registry with decorator-based registration."""

    def __init__(self, kind: str):
        self._kind = kind
        self._items: dict[str, type[T]] = {}

    def register(self, name: str):
        """Class decorator: @registry.register('ema')"""

        def decorator(cls: type[T]) -> type[T]:
            if name in self._items:
                raise ValueError(
                    f"{self._kind} '{name}' is already registered "
                    f"(by {self._items[name].__module__}.{self._items[name].__name__})"
                )
            self._items[name] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[T]:
        if name not in self._items:
            raise KeyError(
                f"Unknown {self._kind} '{name}'. Available: {sorted(self._items)}"
            )
        return self._items[name]

    def all(self) -> dict[str, type[T]]:
        return dict(self._items)

    def names(self) -> list[str]:
        return sorted(self._items)


def discover_package(package_name: str) -> None:
    """
    Import every submodule (and sub-package) under `package_name` so
    that any `@registry.register(...)` decorators inside them execute.

    This is what lets us add a new indicator/strategy file and have it
    picked up automatically — no central import list to maintain.
    """
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        return
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_name = f"{package_name}.{module_name}"
        if is_pkg:
            discover_package(full_name)
        else:
            importlib.import_module(full_name)
