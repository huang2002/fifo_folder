from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import NamedTuple, Self

from .utils import SupportsGreaterThan

__all__ = [
    "FIFOItem",
    "FIFOManager",
]


class FIFOItem[DataType, KeyType: SupportsGreaterThan](NamedTuple):
    """Item class used in [FIFOManager](#fifomanager-objects).

    Attributes:
        data (DataType): Item data.
        key (KeyType): Item key.
    """
    data: DataType
    key: KeyType


class FIFOManager[DataType, KeyType: SupportsGreaterThan](ABC):
    """Base class for FIFO managers.

    Subclasses must implement the following methods:

    - `_get_data()`
    - `_get_key()`
    - `_get_extra_count()`
    - `_remove_item()`

    Args:
        sort_reverse (bool, optional): \
            Whether to sort items in descending order. (Default: `True`)

    Attributes:
        sort_reverse (bool): \
            Whether to sort items in decending order.
        items (list[FIFOItem[DataType, KeyType]]): \
            Items to manage, sorted in ascending order.
    """

    sort_reverse: bool
    items: list[FIFOItem[DataType, KeyType]]

    def __init__(self, *, sort_reverse: bool = True) -> None:
        self.items = []
        self.sort_reverse = sort_reverse

    @abstractmethod
    def _get_data(self) -> Iterable[DataType]:
        """Get data to manage."""

    @abstractmethod
    def _get_key(self, data: DataType) -> KeyType:
        """Get custom key to specific data."""

    @abstractmethod
    def _get_extra_count(self) -> int:
        """Get count of extra items to remove."""

    @abstractmethod
    def _remove_item(self, item: FIFOItem[DataType, KeyType]) -> None:
        """Remove specific item."""

    def load_items(self) -> Self:
        """Load all data to manage (without invoking `self.manage()`)."""
        self.items = list(
            sorted(
                (
                    FIFOItem(data=data, key=self._get_key(data))
                    for data in self._get_data()
                ),
                key=lambda item: item.key,  # type: ignore
                reverse=self.sort_reverse,
            )
        )
        return self

    def add(self, data: DataType) -> None:
        """Add a new item by providing its data."""
        new_item = FIFOItem(data=data, key=self._get_key(data))
        for i, item in enumerate(self.items):
            if new_item.key > item.key:
                self.items.insert(i, new_item)
                break
        else:
            self.items.append(new_item)

    def manage(self) -> list[FIFOItem[DataType, KeyType]]:
        """Remove and return extra items (from last to first)."""
        extra_count = self._get_extra_count()
        items = self.items
        removed_items: list[FIFOItem[DataType, KeyType]] = []
        for _ in range(extra_count):
            item = items.pop()
            self._remove_item(item)
            removed_items.append(item)
        return removed_items
