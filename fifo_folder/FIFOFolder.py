import os
from collections.abc import Iterable
from math import inf, nan
from typing import Literal, NamedTuple, override

from .FIFOManager import FIFOItem, FIFOManager

__all__ = [
    "FileData",
    "FileSortKey",
    "FileKey",
    "FIFOFolder",
]


class FileData(NamedTuple):
    """Item data for use in [FIFOFolder](#fifofolder-objects).

    Attributes:
        path (str): Absolute path to the file.
        birthtime (float): The birth time of the file.
        ctime (float): The creation time of the file.
        mtime (float): The last modification time of the file.
        atime (float): The last access time of the file.
        size (int): The size of the file in bytes.
    """

    path: str
    birthtime: float
    ctime: float
    mtime: float
    atime: float
    size: int


type FileSortKey = Literal[
    "path",
    "birthtime",
    "ctime",
    "mtime",
    "atime",
    "size",
]
"""Available sort keys for use in [FIFOFolder](#fifofolder-objects)."""

type FileKey = str | int | float


def _create_file_data(path: str) -> FileData:
    stat_result = os.stat(path)
    return FileData(
        path=path,
        birthtime=getattr(stat_result, "st_birthtime", nan),
        ctime=stat_result.st_ctime,
        mtime=stat_result.st_mtime,
        atime=stat_result.st_atime,
        size=stat_result.st_size,
    )


class FIFOFolder(FIFOManager[FileData, FileKey]):
    """FIFO folder mananger.

    This manages files in specific folder based on queue-like principles.

    Args:
        base_path (os.PathLike | str): \
            Path to the folder to manage.
        sort_key (FileSortKey, optional): \
            Key to sort files by. (Default: `"ctime"`)
        count_limit (int | float, optional): \
            Limit of files to keep. (Default: `inf`)
        total_size_limit (int | float, optional): \
            Limit of total bytes of files to keep. (Default: `inf`)
        sort_key_limit (FileKey | None, optional): \
            Keep files whose keys are greater than or equal to this limit.
            If set to some value other than `None`,
            this limit must be consistent with `sort_key`.
            `None` disables this limit. (Default: `None`)
        **kwargs: \
            Additional arguments for [`FIFOManager`](#fifomanager-objects).

    Attributes:
        base_path (os.PathLike | str): \
            Path to target folder.
        sort_key (FileSortKey): \
            The key used to sort file items.
        count_limit (int | float): \
            Keep up to this amount of files.
        total_size_limit (int | float): \
            Keep sum of file sizes (in bytes) no greater than this limit.
        sort_key_limit (FileKey | None): \
            The key used to limit file items by sort key.
            Keep files where `key >= sort_key_limit` if `self.sort_reverse` is true;
            `<=` otherwise.
    """

    base_path: os.PathLike | str
    sort_key: FileSortKey
    count_limit: int | float
    total_size_limit: int | float
    sort_key_limit: FileKey | None

    def __init__(
        self,
        base_path: os.PathLike | str,
        *,
        sort_key: FileSortKey = "ctime",
        count_limit: int | float = inf,
        total_size_limit: int | float = inf,
        sort_key_limit: FileKey | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.base_path = base_path
        self.sort_key = sort_key
        self.count_limit = count_limit
        self.total_size_limit = total_size_limit
        self.sort_key_limit = sort_key_limit

    @override
    def _get_data(self) -> Iterable[FileData]:
        base_path = self.base_path
        return (
            _create_file_data(absolute_path)
            for absolute_path in (
                os.path.join(base_path, file_path)
                for file_path in os.listdir(base_path)
            )
            if os.path.isfile(absolute_path)
        )

    @override
    def _get_key(self, data: FileData) -> FileKey:
        return getattr(data, self.sort_key)

    @override
    def _get_extra_count(self) -> int:
        count_limit = self.count_limit
        total_size_limit = self.total_size_limit
        sort_key_limit = self.sort_key_limit
        sort_reverse = self.sort_reverse
        type_sort_limit = (
            type(sort_key_limit) if sort_key_limit is not None else None
        )
        total_size = 0
        for i, item in enumerate(self.items):
            if i >= count_limit:
                break
            if sort_key_limit is not None:
                type_item_key = type(item.key)
                if type_item_key != type_sort_limit:
                    raise TypeError(
                        f"cannot compare {type_item_key!r} "
                        f"with {type_sort_limit!r}"
                    )
                elif (
                    item.key < sort_key_limit  # type: ignore
                    if sort_reverse
                    else item.key > sort_key_limit  # type: ignore
                ):
                    break
            total_size += item.data.size
            if total_size > total_size_limit:
                break
        else:
            return 0
        return len(self.items) - i

    @override
    def _remove_item(self, item: FIFOItem[FileData, FileKey]) -> None:
        os.remove(item.data.path)
