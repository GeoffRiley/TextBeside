"""Smoke tests for the first TextBeside window."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from textbeside.app import MainWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance() or QApplication([])
    return app


def test_main_window_has_editable_horizontal_split(qapp: QApplication) -> None:
    window = MainWindow()

    assert window.splitter.orientation() == Qt.Horizontal
    assert window.splitter.count() == 2
    assert not window.editor.isReadOnly()

    window.close()


def test_sample_pair_opens_without_conversion(qapp: QApplication) -> None:
    root = Path(__file__).resolve().parents[1]
    sample_dir = root / "examples" / "field-notes"
    image_path = sample_dir / "field-notes-01.jpg"
    text_path = sample_dir / "field-notes-01.md"

    window = MainWindow()
    window.open_pair(image_path, text_path)

    assert window.current_image_path == image_path
    assert window.current_text_path == text_path
    assert image_path.name in window.image_path_label.text()
    assert text_path.name in window.text_path_label.text()
    assert window.editor.toPlainText() == text_path.read_text(encoding="utf-8")
    assert not window.image_label.pixmap().isNull()
    assert not window.editor.document().isModified()

    window.close()
