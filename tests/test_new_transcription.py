"""Starting a new transcription without an existing text file."""

from pathlib import Path
from shutil import copyfile

import pytest
from PySide6.QtWidgets import QMessageBox, QInputDialog

from textbeside.app import MainWindow
from textbeside.file_ops import create_text_file_exclusive


@pytest.fixture
def source_image(tmp_path: Path) -> Path:
    root = Path(__file__).resolve().parents[1]
    source = root / "examples" / "field-notes" / "field-notes-01.jpg"
    destination = tmp_path / "new-page.jpg"
    copyfile(source, destination)
    return destination


def test_open_image_only_keeps_directory_unchanged(qapp, source_image: Path) -> None:
    window = MainWindow()
    window.open_image_only(source_image)

    assert window.new_transcription
    assert window.current_text_path is None
    assert window.editor.toPlainText() == ""
    assert window.image_view.has_image
    assert list(source_image.parent.iterdir()) == [source_image]
    window.close()


@pytest.mark.parametrize("choice,suffix", [
    (".md (Markdown)", ".md"),
    (".txt (plain text)", ".txt"),
])
def test_first_save_creates_chosen_format(
    qapp, source_image: Path, monkeypatch, choice: str, suffix: str
) -> None:
    window = MainWindow()
    window.open_image_only(source_image)
    window.editor.setPlainText("Café — transcription")
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: (choice, True))

    assert window.save_current_text()
    target = source_image.with_suffix(suffix)
    assert target.read_bytes() == "Café — transcription".encode("utf-8")
    assert window.current_text_path == target
    assert not window.new_transcription
    assert not window.editor.document().isModified()
    window.close()


def test_first_save_cancellation_preserves_editor(
    qapp, source_image: Path, monkeypatch
) -> None:
    window = MainWindow()
    window.open_image_only(source_image)
    window.editor.setPlainText("Work in progress")
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: ("", False))
    assert not window.save_current_text()
    assert window.editor.toPlainText() == "Work in progress"
    assert window.editor.document().isModified()
    assert not source_image.with_suffix(".md").exists()
    window.editor.document().setModified(False)
    window.close()


def test_existing_counterpart_prevents_new_work(
    qapp, source_image: Path
) -> None:
    source_image.with_suffix(".md").write_text("existing", encoding="utf-8")
    window = MainWindow()
    with pytest.raises(ValueError, match="already has"):
        window.open_image_only(source_image)
    assert window.current_image_path is None
    window.close()


def test_counterpart_appearing_before_save_is_not_overwritten(
    qapp, source_image: Path, monkeypatch
) -> None:
    window = MainWindow()
    window.open_image_only(source_image)
    window.editor.setPlainText("My new transcription")
    unexpected = source_image.with_suffix(".txt")
    unexpected.write_text("someone else's work", encoding="utf-8")
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: (".md (Markdown)", True))
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)

    assert not window.save_current_text()
    assert unexpected.read_text(encoding="utf-8") == "someone else's work"
    assert not source_image.with_suffix(".md").exists()
    assert window.editor.document().isModified()
    window.editor.document().setModified(False)
    window.close()


def test_exclusive_creation_cannot_overwrite_existing(tmp_path: Path) -> None:
    path = tmp_path / "first.md"
    path.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError):
        create_text_file_exclusive(path, "replacement")
    assert path.read_text(encoding="utf-8") == "original"
