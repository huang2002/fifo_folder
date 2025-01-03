import os
import sys
import time
from pathlib import Path

import pytest

from fifo_folder import FIFOFolder

from .utils import touch


@pytest.fixture()
def test_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:

    monkeypatch.chdir(os.path.dirname(__file__))

    (tmp_path / "0.txt").write_text("0" * 512)

    time.sleep(0.1)
    (tmp_path / "2.txt").write_text("1" * 1024)

    time.sleep(0.1)
    (tmp_path / "1.txt").write_text("1")

    time.sleep(0.1)
    touch(tmp_path / "0.txt")

    time.sleep(0.1)
    touch(tmp_path / "1.txt")

    time.sleep(0.1)
    touch(tmp_path / "2.txt", mtime=False)

    return tmp_path


def test_sort_key_default(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path)
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    if sys.platform == "win32":
        assert os.path.basename(fifo_folder.items[0].data.path) == "1.txt"
        assert os.path.basename(fifo_folder.items[1].data.path) == "2.txt"
        assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"
    else:
        assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
        assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
        assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_sort_key_path(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path, sort_key="path")
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_sort_key_birthtime(test_path: Path) -> None:
    if "birthtime" not in dir(os.stat_result):
        pytest.skip("birthtime not available on os.stat_result")
    fifo_folder = FIFOFolder(test_path, sort_key="birthtime")
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_sort_key_ctime(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path, sort_key="ctime")
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    if sys.platform == "win32":
        assert os.path.basename(fifo_folder.items[0].data.path) == "1.txt"
        assert os.path.basename(fifo_folder.items[1].data.path) == "2.txt"
        assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"
    else:
        assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
        assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
        assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_sort_key_mtime(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path, sort_key="mtime")
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "0.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "2.txt"


def test_sort_key_atime(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path, sort_key="atime")
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_sort_key_size(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path, sort_key="size")
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "0.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "1.txt"
