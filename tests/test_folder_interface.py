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
    return [
        window.page_model.data(window.page_model.index(i))
        for i in range(window.page_model.rowCount())
    ]


def state(window):
    return (
        window.current_image_path,
        window.current_text_path,
        window.current_text_signature,
        window.editor.toPlainText(),
        window.editor.document().isModified(),
        window.new_transcription,
        listed(window),
        window.page_list.currentIndex().row(),
        window.folder_label.text(),
    )


def test_open_folder_and_select_nonadjacent_page(folder):
    window, root = folder
    assert not window.rescan_action.isEnabled()
    assert window.open_folder(root)
    assert listed(window) == ["page-1.jpg", "page-2.jpg", "page-10.jpg"]
    assert window.folder_label.text() == str(root)
    assert window.page_list.currentIndex().row() == 0
    assert window.editor.toPlainText() == "page 1"
    window.page_list.setCurrentIndex(window.page_model.index(2))
    assert window.current_image_path == root / "page-10.jpg"
    assert window.current_text_path == root / "page-10.md"
    assert window.editor.toPlainText() == "page 10"
    assert not window.next_action.isEnabled()
    assert window.navigate_page(-1)
    assert window.page_list.currentIndex().row() == 1


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
    window.page_list.setCurrentIndex(window.page_model.index(2))
    if choice == QMessageBox.Cancel:
        assert state(window) == before
    else:
        assert window.current_image_path == root / "page-10.jpg"
        assert window.editor.toPlainText() == "page 10"
        assert window.page_list.currentIndex().row() == 2
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
    assert window.page_list.currentIndex().row() == -1
    assert not window.next_action.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Discard)
    window.page_list.setCurrentIndex(window.page_model.index(1))
    assert window.current_image_path == root / "page-3.jpg"
    assert window.new_transcription
    assert window.editor.toPlainText() == ""


def test_list_missing_counterpart_creates_no_file(folder):
    window, root = folder
    (root / "page-10.md").unlink()
    window.open_folder(root)
    before = set(root.iterdir())
    window.page_list.setCurrentIndex(window.page_model.index(2))
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
    window.page_list.setCurrentIndex(window.page_model.index(2))
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
    window.page_list.setCurrentIndex(window.page_model.index(2))
    assert state(window) == before


@pytest.mark.parametrize("cancel", [True, False])
def test_successful_folder_keeps_discovered_list_if_rescan_fails(
    folder, monkeypatch, tmp_path, cancel
):
    from textbeside import app

    window, root = folder
    window.open_folder(root)
    other = tmp_path / "other"
    other.mkdir()
    for n in (1, 2):
        copyfile(root / "page-1.jpg", other / f"new-{n}.jpg")
    original = app.discover_images
    calls = 0

    def discover(directory):
        nonlocal calls
        calls += 1
        if calls > 1:
            if cancel:
                raise app.LoadingCancelled
            raise PermissionError("follow-up scan unavailable")
        return original(directory)

    monkeypatch.setattr(app, "discover_images", discover)
    assert window.open_folder(other)
    assert window.current_image_path == other / "new-1.jpg"
    assert window.folder_label.text() == str(other)
    assert listed(window) == ["new-1.jpg", "new-2.jpg"]
    assert window.page_list.currentIndex().row() == 0
    assert window.rescan_action.isEnabled()


@pytest.mark.parametrize("cancel", [True, False])
def test_manual_pair_in_new_folder_never_keeps_old_rows(
    folder, monkeypatch, tmp_path, cancel
):
    from textbeside import app

    window, root = folder
    window.open_folder(root)
    other = tmp_path / "other"
    other.mkdir()
    copyfile(root / "page-1.jpg", other / "new.jpg")
    (other / "new.md").write_text("new", encoding="utf-8")

    def fail(*a):
        if cancel:
            raise app.LoadingCancelled
        raise PermissionError("cannot list new directory")

    monkeypatch.setattr(app, "discover_images", fail)
    window.open_pair(other / "new.jpg", other / "new.md")
    assert window.current_image_path == other / "new.jpg"
    assert window.folder_label.text() == str(other)
    assert listed(window) == []
    assert not window.previous_action.isEnabled()
    assert not window.next_action.isEnabled()


def test_cancelled_blocked_read_does_not_spawn_retry_workers(folder):
    from threading import Event

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QProgressDialog

    from textbeside.app import LoadingCancelled

    window, _root = folder
    started, release = Event(), Event()
    calls = []

    def blocked():
        calls.append(True)
        started.set()
        release.wait(5)
        return "late result"

    timer = QTimer()

    def cancel():
        if started.is_set():
            dialog = window.findChild(QProgressDialog)
            if dialog:
                dialog.cancel()

    timer.timeout.connect(cancel)
    timer.start(10)
    try:
        with pytest.raises(LoadingCancelled):
            window._run_file_task(blocked)
        worker = window._outstanding_worker
        for _ in range(5):
            with pytest.raises(LoadingCancelled, match="still finishing"):
                window._run_file_task(blocked)
            assert window._outstanding_worker is worker
        assert len(calls) == 1
        assert not window._file_task_active
    finally:
        timer.stop()
        release.set()
        window._outstanding_worker.join(timeout=2)
    assert window._run_file_task(lambda: "fresh result") == "fresh result"


def test_large_folder_uses_lazy_batched_model(folder, monkeypatch):
    from PySide6.QtWidgets import QListView

    window, root = folder
    window.current_image_path = root / "page-0.jpg"
    paths = [root / f"page-{i}.jpg" for i in range(100_000)]
    calls = []
    original = window.page_model.data

    def data(*args):
        calls.append(True)
        return original(*args)

    monkeypatch.setattr(window.page_model, "data", data)
    window._set_page_list(paths)
    assert window.page_model.paths is paths
    assert window.page_model.rowCount() == 100_000
    assert window.page_list.layoutMode() == QListView.Batched
    assert window.page_list.uniformItemSizes()
    assert len(calls) < 1000  # rows aren't all materialized during publication
    assert window.page_model.data(window.page_model.index(99999)) == "page-99999.jpg"


def test_parent_watch_recovers_recreated_folder(folder):
    from shutil import rmtree

    from PySide6.QtCore import QEventLoop, QTimer

    window, root = folder
    window.open_folder(root)
    source = root / "page-1.jpg"
    image_bytes = source.read_bytes()
    assert str(root.parent) in window._directory_watcher.directories()
    rmtree(root)
    window._refresh_navigation()
    root.mkdir()
    (root / "returned.jpg").write_bytes(image_bytes)
    loop = QEventLoop()
    poll = QTimer()
    poll.timeout.connect(
        lambda: loop.quit() if listed(window) == ["returned.jpg"] else None
    )
    deadline = QTimer()
    deadline.setSingleShot(True)
    deadline.timeout.connect(loop.quit)
    poll.start(20)
    deadline.start(3000)
    loop.exec()
    poll.stop()
    deadline.stop()
    assert listed(window) == ["returned.jpg"]
    assert str(root) in window._directory_watcher.directories()
    assert not window.watch_status_label.text()


def test_failed_watch_is_visible_and_rescan_available(folder, monkeypatch):
    window, root = folder
    monkeypatch.setattr(window._directory_watcher, "addPath", lambda path: False)
    assert window.open_folder(root)
    assert "Automatic page updates unavailable" in window.watch_status_label.text()
    assert "F5" in window.watch_status_label.text()
    assert window.rescan_action.isEnabled()
    window.rescan_folder()
    assert listed(window) == ["page-1.jpg", "page-2.jpg", "page-10.jpg"]
