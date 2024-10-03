from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import NamedTuple, Self

from .utils import SupportsComparison

__all__ = [
    "FIFOItem",
    "FIFOManager",
]


class FIFOItem[DataType, KeyType: SupportsComparison](NamedTuple):
    """Item class used in [FIFOManager](#fifomanager-objects).

    Attributes:
        data (DataType): Item data.
        key (KeyType): Item key.
    """
    data: DataType
    key: KeyType


type FIFOFilter[ItemType: FIFOItem] = Callable[[ItemType], bool]
"""Filter function type used in [FIFOManager](#fifomanager-objects)."""


class FIFOManager[DataType, KeyType: SupportsComparison](ABC):
    """Base class for FIFO managers.

    Subclasses must implement the following methods:

    - `_get_data()`
    - `_get_key()`
    - `_get_extra_count()`
    - `_remove_item()`

    Args:
        sort_reverse (bool, optional): \
            Whether to sort items in descending order. (Default: `True`)
        filter_function (FIFOFilter[FIFOItem[DataType, KeyType]] | None, optional): \
            If a function is provided, it will be used to filter the items
            returned by `_get_data()`. The function should return `True` for
            items to keep and `False` for items to ignore. (Default: `None`)

    Attributes:
        sort_reverse (bool): \
            Whether to sort items in decending order.
        items (list[FIFOItem[DataType, KeyType]]): \
            Items to manage, sorted in ascending order.
        filter_function (FIFOFilter[FIFOItem[DataType, KeyType]] | None): \
            If a function is provided, it will be used to filter the items
            returned by `_get_data()`. The function should return `True` for
            items to keep and `False` for items to ignore.
    """

    sort_reverse: bool
    filter_function: FIFOFilter[FIFOItem[DataType, KeyType]] | None
    items: list[FIFOItem[DataType, KeyType]]

    def __init__(
        self,
        *,
        sort_reverse: bool = True,
        filter_function: FIFOFilter[FIFOItem[DataType, KeyType]] | None = None,
    ) -> None:
        self.items = []
        self.sort_reverse = sort_reverse
        self.filter_function = filter_function

    @abstractmethod
    def _get_data(self) -> Iterable[DataType]:
        """Get data to manage."""
        raise NotImplementedError()

    @abstractmethod
    def _get_key(self, data: DataType) -> KeyType:
        """Get custom key to specific data."""
        raise NotImplementedError()

    @abstractmethod
    def _get_extra_count(self) -> int:
        """Get count of extra items to remove."""
        raise NotImplementedError()

    @abstractmethod
    def _remove_item(self, item: FIFOItem[DataType, KeyType]) -> None:
        """Remove specific item."""
        raise NotImplementedError()

    def load_items(self) -> Self:
        """Load the items to manage. (Won't automatically invoke `self.manage()`.)"""
        iterable = (
            FIFOItem(data=data, key=self._get_key(data))
            for data in self._get_data()
        )
        if self.filter_function:
            iterable = filter(self.filter_function, iterable)
        self.items = list(
            sorted(
                iterable,
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
