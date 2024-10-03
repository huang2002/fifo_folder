from typing import Any, Protocol

__all__ = [
    "SupportsComparison",
]


class SupportsComparison(Protocol):
    def __gt__(self, other: Any, /) -> bool: ...
    def __lt__(self, other: Any, /) -> bool: ...
