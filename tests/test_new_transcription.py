"""Starting a new transcription without an existing text file."""

import errno
import os
import stat
from pathlib import Path
from shutil import copyfile

import pytest
from PySide6.QtWidgets import QInputDialog, QMessageBox

from textbeside.app import MainWindow
from textbeside.file_ops import create_text_file_exclusive, file_signature


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


@pytest.mark.parametrize(
    "choice,suffix",
    [
        (".md (Markdown)", ".md"),
        (".txt (plain text)", ".txt"),
    ],
)
def test_first_save_creates_chosen_format(
    qapp, source_image: Path, monkeypatch, choice: str, suffix: str
) -> None:
    window = MainWindow()
    window.open_image_only(source_image)
    window.editor.setPlainText("Café — transcription")
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: (choice, True))

    assert window.save_current_text()
    target = source_image.with_suffix(suffix)
    assert target.read_bytes() == "Café — transcription".encode()
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
    window.editor.document().setModified(True)
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: ("", False))
    assert not window.save_current_text()
    assert window.editor.toPlainText() == "Work in progress"
    assert window.editor.document().isModified()
    assert not source_image.with_suffix(".md").exists()
    window.editor.document().setModified(False)
    window.close()


def test_existing_counterpart_prevents_new_work(qapp, source_image: Path) -> None:
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
    window.editor.document().setModified(True)
    unexpected = source_image.with_suffix(".txt")
    unexpected.write_text("someone else's work", encoding="utf-8")
    monkeypatch.setattr(
        QInputDialog, "getItem", lambda *a, **k: (".md (Markdown)", True)
    )
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


def test_failed_publish_does_not_delete_racing_target(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "new.md"
    original_link = os.link

    def concurrent_creation(source, destination):
        target.write_text("other process", encoding="utf-8")
        return original_link(source, destination)

    monkeypatch.setattr(os, "link", concurrent_creation)

    with pytest.raises(FileExistsError):
        create_text_file_exclusive(target, "our transcription")
    assert target.read_text(encoding="utf-8") == "other process"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["new.md"]


@pytest.mark.skipif(os.name == "nt", reason="Unix mode bits")
def test_created_file_is_private(tmp_path: Path) -> None:
    target = tmp_path / "private.md"
    create_text_file_exclusive(target, "private material")
    assert stat.S_IMODE(target.stat().st_mode) == 0o600


def test_signature_is_of_staged_file_even_if_target_replaced(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "replace.md"
    real_link = os.link

    def replace_after_publish(source, destination):
        real_link(source, destination)
        replacement = tmp_path / "replacement.tmp"
        replacement.write_text("external longer content", encoding="utf-8")
        os.replace(replacement, destination)

    monkeypatch.setattr(os, "link", replace_after_publish)
    signature = create_text_file_exclusive(target, "ours")

    assert target.read_text(encoding="utf-8") == "external longer content"
    assert signature.size == len("ours".encode())
    assert signature != file_signature(target)


def test_no_hardlinks_falls_back_to_exclusive_creation(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "fallback.md"

    def unsupported(*args, **kwargs):
        raise OSError(errno.EOPNOTSUPP, "hard links unavailable")

    monkeypatch.setattr(os, "link", unsupported)
    signature = create_text_file_exclusive(target, "fallback Café")
    assert target.read_text(encoding="utf-8") == "fallback Café"
    assert signature.size == len("fallback Café".encode())
    assert sorted(p.name for p in tmp_path.iterdir()) == ["fallback.md"]

    with pytest.raises(FileExistsError):
        create_text_file_exclusive(target, "overwrite attempt")
    assert target.read_text(encoding="utf-8") == "fallback Café"


def test_cleanup_failure_cannot_mask_completed_publication(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "completed.md"
    original_unlink = Path.unlink

    def blocked_unlink(path, *args, **kwargs):
        if path.suffix == ".tmp":
            raise PermissionError("simulated locked temporary file")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", blocked_unlink)
    signature = create_text_file_exclusive(target, "saved")
    assert target.read_text(encoding="utf-8") == "saved"
    assert signature.size == 5
