"""Smoke tests for the first TextBeside window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from textbeside.app import MainWindow


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
    assert window.image_view.has_image
    assert window.image_view.is_fit_mode
    assert not window.editor.document().isModified()

    window.close()



def test_save_updates_disk_and_clears_modified_state(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    image_path = root / "examples" / "field-notes" / "field-notes-01.jpg"
    text_path = tmp_path / "working-copy.md"
    text_path.write_text("original\n", encoding="utf-8")

    window = MainWindow()
    window.open_pair(image_path, text_path)
    window.editor.setPlainText("updated café — exact editor text")

    assert window.editor.document().isModified()
    assert "Modified" in window.text_path_label.text()

    assert window.save_current_text()

    assert text_path.read_bytes() == "updated café — exact editor text".encode("utf-8")
    assert not window.editor.document().isModified()
    assert "Saved" in window.text_path_label.text()

    window.close()


def test_external_change_is_not_overwritten_without_confirmation(
    qapp: QApplication,
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = Path(__file__).resolve().parents[1]
    image_path = root / "examples" / "field-notes" / "field-notes-01.jpg"
    text_path = tmp_path / "working-copy.md"
    text_path.write_text("original", encoding="utf-8")

    window = MainWindow()
    window.open_pair(image_path, text_path)
    window.editor.setPlainText("editor version")

    text_path.write_text("external version with different length", encoding="utf-8")
    monkeypatch.setattr(window, "_confirm_external_overwrite", lambda: False)

    assert not window.save_current_text()
    assert text_path.read_text(encoding="utf-8") == "external version with different length"
    assert window.editor.toPlainText() == "editor version"
    assert window.editor.document().isModified()

    window.editor.document().setModified(False)
    window.close()


def test_save_failure_keeps_editor_modified(
    qapp: QApplication,
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = Path(__file__).resolve().parents[1]
    image_path = root / "examples" / "field-notes" / "field-notes-01.jpg"
    text_path = tmp_path / "working-copy.md"
    text_path.write_text("original", encoding="utf-8")

    window = MainWindow()
    window.open_pair(image_path, text_path)
    window.editor.setPlainText("unsaved editor text")

    def fail_save(path: Path, text: str):
        raise OSError("simulated save failure")

    monkeypatch.setattr("textbeside.app.write_text_file_atomic", fail_save)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: None)

    assert not window.save_current_text()
    assert window.editor.toPlainText() == "unsaved editor text"
    assert window.editor.document().isModified()
    assert text_path.read_text(encoding="utf-8") == "original"

    window.editor.document().setModified(False)
    window.close()
