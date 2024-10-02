import os
import time

__all__ = [
    "touch",
]


def touch(
    path: str | os.PathLike,
    *,
    atime: bool = True,
    mtime: bool = True,
) -> None:
    now = time.time()
    os.utime(path, (
        now if atime else os.path.getatime(path),
        now if mtime else os.path.getmtime(path),
    ))
