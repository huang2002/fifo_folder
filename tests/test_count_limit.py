import os
import time
from pathlib import Path

import pytest

from fifo_folder import FIFOFolder


@pytest.fixture()
def test_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:

    monkeypatch.chdir(os.path.dirname(__file__))

    (tmp_path / "0.txt").write_text("")

    time.sleep(0.1)
    (tmp_path / "1.txt").write_text("1" * 1024)

    return tmp_path


def test_count_limit(test_path: Path) -> None:

    fifo_folder = FIFOFolder(test_path, count_limit=2)
    fifo_folder.load_items()

    assert len(fifo_folder.items) == 2
    assert os.path.basename(fifo_folder.items[0].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "0.txt"

    removed_items = fifo_folder.manage()
    assert len(removed_items) == 0
    assert len(fifo_folder.items) == 2
    assert os.path.basename(fifo_folder.items[0].data.path) == "1.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "0.txt"

    time.sleep(1)
    (test_path / "2.txt").write_text("2")
    fifo_folder.load_items()

    removed_items = fifo_folder.manage()
    assert len(fifo_folder.items) == 2
    assert len(removed_items) == 1
    assert os.path.basename(removed_items[0].data.path) == "0.txt"
    assert os.path.basename(fifo_folder.items[0].data.path) == "2.txt"
    assert os.path.basename(fifo_folder.items[1].data.path) == "1.txt"
