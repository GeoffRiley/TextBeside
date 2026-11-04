"""Folder opening, direct page selection and non-destructive rescanning."""

from pathlib import Path
from shutil import copyfile

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox

from textbeside.app import MainWindow


@pytest.fixture
def folder(qapp, tmp_path):
    source = (
        Path(__file__).resolve().parents[1] / "examples/field-notes/field-notes-01.jpg"
    )
    root = tmp_path / "source"
    root.mkdir()
    for n in (1, 2, 10):
        copyfile(source, root / f"page-{n}.jpg")
        (root / f"page-{n}.md").write_text(f"page {n}", encoding="utf-8")
    (root / "unrelated.pdf").write_bytes(b"not an image")
    (root / "subfolder").mkdir()
    window = MainWindow()
    yield window, root
    window.editor.document().setModified(False)
    window.close()


def listed(window):
    return [window.page_list.item(i).text() for i in range(window.page_list.count())]


def state(window):
    return (
        window.current_image_path,
        window.current_text_path,
        window.current_text_signature,
        window.editor.toPlainText(),
        window.editor.document().isModified(),
        window.new_transcription,
        listed(window),
        window.page_list.currentRow(),
        window.folder_label.text(),
    )


def test_open_folder_and_select_nonadjacent_page(folder):
    window, root = folder
    assert not window.rescan_action.isEnabled()
    assert window.open_folder(root)
    assert listed(window) == ["page-1.jpg", "page-2.jpg", "page-10.jpg"]
    assert window.folder_label.text() == str(root)
    assert window.page_list.currentRow() == 0
    assert window.editor.toPlainText() == "page 1"
    window.page_list.setCurrentRow(2)
    assert window.current_image_path == root / "page-10.jpg"
    assert window.current_text_path == root / "page-10.md"
    assert window.editor.toPlainText() == "page 10"
    assert not window.next_action.isEnabled()
    assert window.navigate_page(-1)
    assert window.page_list.currentRow() == 1


@pytest.mark.parametrize(
    "choice", [QMessageBox.Save, QMessageBox.Discard, QMessageBox.Cancel]
)
def test_list_selection_protects_unsaved_work(folder, monkeypatch, choice):
    window, root = folder
    window.open_folder(root)
    window.editor.setPlainText("edited café")
    window.editor.document().setModified(True)
    before = state(window)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: choice)
    window.page_list.setCurrentRow(2)
    if choice == QMessageBox.Cancel:
        assert state(window) == before
    else:
        assert window.current_image_path == root / "page-10.jpg"
        assert window.editor.toPlainText() == "page 10"
        assert window.page_list.currentRow() == 2
    assert (root / "page-1.md").read_text(encoding="utf-8") == (
        "edited café" if choice == QMessageBox.Save else "page 1"
    )


def test_rescan_retains_edits_and_reselection_recovers_missing_current(
    folder, monkeypatch
):
    window, root = folder
    window.open_folder(root)
    window.editor.setPlainText("unsaved")
    window.editor.document().setModified(True)
    before = state(window)[:6]
    (root / "page-1.jpg").unlink()
    copyfile(root / "page-2.jpg", root / "page-3.jpg")
    window.rescan_action.trigger()
    assert state(window)[:6] == before
    assert listed(window) == ["page-2.jpg", "page-3.jpg", "page-10.jpg"]
    assert window.page_list.currentRow() == -1
    assert not window.next_action.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Discard)
    window.page_list.setCurrentRow(1)
    assert window.current_image_path == root / "page-3.jpg"
    assert window.new_transcription
    assert window.editor.toPlainText() == ""


def test_list_missing_counterpart_creates_no_file(folder):
    window, root = folder
    (root / "page-10.md").unlink()
    window.open_folder(root)
    before = set(root.iterdir())
    window.page_list.setCurrentRow(2)
    assert window.new_transcription
    assert window.current_text_path is None
    assert window.editor.toPlainText() == ""
    assert set(root.iterdir()) == before


@pytest.mark.parametrize(
    "scenario",
    [
        "picker_cancel",
        "empty",
        "missing_folder",
        "corrupt_image",
        "conflict_cancel",
        "modified_cancel",
    ],
)
def test_failed_folder_open_retains_current_work(
    folder, monkeypatch, tmp_path, scenario
):
    window, root = folder
    window.open_folder(root)
    window.editor.setPlainText("unsaved")
    window.editor.document().setModified(True)
    before = state(window)
    target = tmp_path / "other"
    target.mkdir()
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: None)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: None)
    if scenario == "picker_cancel":
        monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a: "")
        window.open_folder_dialog()
    else:
        if scenario == "missing_folder":
            target.rmdir()
        elif scenario != "empty":
            copyfile(root / "page-1.jpg", target / "new.jpg")
            (target / "new.md").write_text("new", encoding="utf-8")
            if scenario == "corrupt_image":
                (target / "new.jpg").write_bytes(b"corrupt")
            elif scenario == "conflict_cancel":
                (target / "new.txt").write_text("alternate", encoding="utf-8")
                monkeypatch.setattr(window, "_choose_counterpart", lambda *a: None)
            else:
                monkeypatch.setattr(
                    QMessageBox, "question", lambda *a: QMessageBox.Cancel
                )
        assert not window.open_folder(target)
    assert state(window) == before


def test_failed_list_load_restores_selection(folder, monkeypatch):
    window, root = folder
    window.open_folder(root)
    before = state(window)
    (root / "page-10.jpg").write_bytes(b"corrupt")
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: None)
    window.page_list.setCurrentRow(2)
    assert state(window) == before


def test_rescan_error_keeps_existing_list_and_text(folder, monkeypatch):
    window, _root = folder
    window.open_folder(_root)
    before = state(window)
    errors = []

    def fail(*a):
        raise PermissionError("unreadable folder")

    monkeypatch.setattr("textbeside.app.discover_images", fail)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: errors.append(a))
    window.rescan_folder()
    assert state(window) == before
    assert errors


@pytest.mark.parametrize("suffix", [".md", ".txt"])
def test_folder_conflict_uses_explicit_choice(folder, monkeypatch, suffix):
    window, root = folder
    (root / "page-1.txt").write_text("alternate", encoding="utf-8")
    monkeypatch.setattr(
        window, "_choose_counterpart", lambda candidates: root / ("page-1" + suffix)
    )
    assert window.open_folder(root)
    assert window.current_text_path == root / ("page-1" + suffix)
    assert window.editor.toPlainText() == (
        "alternate" if suffix == ".txt" else "page 1"
    )


def test_failed_save_restores_list_selection(folder, monkeypatch):
    window, root = folder
    window.open_folder(root)
    window.editor.setPlainText("unsaved")
    window.editor.document().setModified(True)
    before = state(window)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Save)
    monkeypatch.setattr(window, "save_current_text", lambda: False)
    window.page_list.setCurrentRow(2)
    assert state(window) == before
