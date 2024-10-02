from typing import Any, Protocol

__all__ = [
    "SupportsGreaterThan",
]


class SupportsGreaterThan(Protocol):
    def __gt__(self, other: Any, /) -> bool: ...
