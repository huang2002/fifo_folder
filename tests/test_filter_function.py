import os
import time
from pathlib import Path

import pytest

from fifo_folder import FIFOFolder


@pytest.fixture()
def test_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:

    monkeypatch.chdir(os.path.dirname(__file__))

    (tmp_path / "0.txt").write_text("0" * 512)

    time.sleep(0.1)
    (tmp_path / "1.txt").write_text("1" * 1024)

    time.sleep(0.1)
    (tmp_path / "2.txt").write_text("2")

    return tmp_path


def test_filter_function_default(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path)
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_filter_function_none(test_path: Path) -> None:
    fifo_folder = FIFOFolder(test_path, filter_function=None)
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 3
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[2].data.path) == "0.txt"


def test_filter_function_lambda(test_path: Path) -> None:
    fifo_folder = FIFOFolder(
        test_path,
        filter_function=lambda item: item.data.path[-5] != "1",
    )
    fifo_folder.load_items()
    assert len(fifo_folder.items) == 2
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "0.txt"
