"""Integration checks for adjacent paired-page navigation."""

from pathlib import Path
from shutil import copyfile

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QInputDialog, QMessageBox

from textbeside.app import MainWindow


@pytest.fixture
def pages(qapp, tmp_path):
    source = (
        Path(__file__).resolve().parents[1] / "examples/field-notes/field-notes-01.jpg"
    )
    images = [tmp_path / f"page-{n}.jpg" for n in (1, 2, 10)]
    for image in images:
        copyfile(source, image)
    images[0].with_suffix(".md").write_text("first", encoding="utf-8")
    images[2].with_suffix(".txt").write_text("last", encoding="utf-8")
    window = MainWindow()
    window.open_pair(images[0], images[0].with_suffix(".md"))
    yield window, images
    window.editor.document().setModified(False)
    window.close()


def state(window):
    return (
        window.current_image_path,
        window.current_text_path,
        window.current_text_signature,
        window.new_transcription,
        window.editor.toPlainText(),
        window.editor.document().isModified(),
        window.image_path_label.text(),
        window.text_path_label.text(),
    )


def edit(window):
    window.editor.setPlainText("unsaved café")
    window.editor.document().setModified(True)


def test_order_missing_counterpart_and_boundaries(pages):
    window, images = pages
    assert not window.previous_action.isEnabled()
    assert window.next_action.isEnabled()
    assert not window.navigate_page(-1)
    before = set(images[0].parent.iterdir())
    window.next_action.trigger()
    assert window.current_image_path == images[1]
    assert window.new_transcription and window.current_text_path is None
    assert window.editor.toPlainText() == ""
    assert window.statusBar().currentMessage() == "Page 2 of 3"
    assert set(images[0].parent.iterdir()) == before
    assert window.navigate_page(1)
    assert window.current_text_path == images[2].with_suffix(".txt")
    assert window.editor.toPlainText() == "last"
    assert not window.next_action.isEnabled()
    assert not window.navigate_page(1)
    assert window.navigate_page(-1)
    assert window.navigate_page(-1)
    assert window.editor.toPlainText() == "first"


@pytest.mark.parametrize(
    "answer", [QMessageBox.Save, QMessageBox.Discard, QMessageBox.Cancel]
)
def test_unsaved_decisions(pages, monkeypatch, answer):
    window, images = pages
    destination = images[1].with_suffix(".md")
    destination.write_text("second page", encoding="utf-8")
    edit(window)
    before = state(window)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: answer)
    assert window.navigate_page(1) == (answer != QMessageBox.Cancel)
    if answer == QMessageBox.Cancel:
        assert state(window) == before
    else:
        assert window.current_image_path == images[1]
        assert window.current_text_path == destination
        assert not window.new_transcription
        assert window.editor.toPlainText() == "second page"
        assert not window.editor.document().isModified()
        assert window.image_view.has_image
    assert images[0].with_suffix(".md").read_text(encoding="utf-8") == (
        "unsaved café" if answer == QMessageBox.Save else "first"
    )


@pytest.mark.parametrize("choice", ["md", "txt", "cancel"])
def test_conflict_requires_choice(pages, monkeypatch, choice):
    window, images = pages
    for suffix in (".md", ".txt"):
        images[1].with_suffix(suffix).write_text(suffix, encoding="utf-8")
    before = state(window)

    def choose():
        box = window.findChild(QMessageBox)
        if box is None or not box.isVisible():
            QTimer.singleShot(10, choose)
            return
        assert box.defaultButton() == box.button(QMessageBox.Cancel)
        assert box.escapeButton() == box.button(QMessageBox.Cancel)
        if choice == "cancel":
            box.close()
        else:
            next(b for b in box.buttons() if b.text() == f"page-2.{choice}").click()

    QTimer.singleShot(0, choose)
    assert window.navigate_page(1) == (choice != "cancel")
    if choice == "cancel":
        assert state(window) == before
    else:
        assert window.current_text_path == images[1].with_suffix("." + choice)
        assert window.editor.toPlainText() == "." + choice


@pytest.mark.parametrize(
    "failure",
    ["image", "text", "directory", "current_missing", "after_discard", "pair_changed"],
)
def test_failure_retains_current_work(pages, monkeypatch, failure):
    window, images = pages
    edit(window)
    before = state(window)
    errors = []
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: errors.append(a))

    def discard(*a):
        if failure == "after_discard":
            images[1].unlink()
        elif failure == "pair_changed":
            images[1].with_suffix(".txt").write_text("appeared")
        else:
            pytest.fail("loading failure must precede discard prompt")
        return QMessageBox.Discard

    monkeypatch.setattr(QMessageBox, "question", discard)
    if failure == "image":
        images[1].write_bytes(b"not an image")
    elif failure == "text":
        images[1].with_suffix(".txt").write_bytes(b"\xff")
    elif failure == "directory":

        def inaccessible(*a):
            raise PermissionError("unreadable directory")

        monkeypatch.setattr("textbeside.app.discover_images", inaccessible)
    elif failure == "current_missing":
        images[0].unlink()
    assert not window.navigate_page(1)
    assert state(window) == before
    assert errors


@pytest.mark.parametrize("new_text", [False, True])
def test_failed_or_cancelled_save_aborts_navigation(pages, monkeypatch, new_text):
    window, images = pages
    if new_text:
        assert window.navigate_page(1)
        monkeypatch.setattr(QInputDialog, "getItem", lambda *a: ("", False))
    else:
        monkeypatch.setattr(window, "save_current_text", lambda: False)
    edit(window)
    before = state(window)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Save)
    assert not window.navigate_page(1)
    assert state(window) == before
    assert not images[1].with_suffix(".md").exists()


def test_manual_mismatch_anchors_to_image_not_text(pages, tmp_path):
    window, images = pages
    unrelated = tmp_path / "unrelated.md"
    unrelated.write_text("manual")
    window.open_pair(images[1], unrelated)
    assert window.navigate_page(1)
    assert window.current_image_path == images[2]
    assert window.current_text_path == images[2].with_suffix(".txt")
    assert unrelated.read_text(encoding="utf-8") == "manual"


def test_no_current_image(qapp):
    window = MainWindow()
    assert not window.previous_action.isEnabled()
    assert not window.next_action.isEnabled()
    assert not window.navigate_page(1)
    window.close()


def test_external_overwrite_refusal_stops_navigation(pages, monkeypatch):
    window, images = pages
    edit(window)
    before = state(window)
    images[0].with_suffix(".md").write_text("external longer replacement")
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Save)
    monkeypatch.setattr(window, "_confirm_external_overwrite", lambda: False)
    assert not window.navigate_page(1)
    assert state(window) == before
    assert (
        images[0].with_suffix(".md").read_text(encoding="utf-8")
        == "external longer replacement"
    )


def test_navigation_saves_new_transcription(pages, monkeypatch):
    window, images = pages
    assert window.navigate_page(1)
    edit(window)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Save)
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a: (".txt (plain text)", True))
    assert window.navigate_page(1)
    assert images[1].with_suffix(".txt").read_text(encoding="utf-8") == "unsaved café"
    assert window.navigate_page(-1)
    assert not window.new_transcription
    assert window.editor.toPlainText() == "unsaved café"


def test_two_sample_pages(qapp):
    root = Path(__file__).resolve().parents[1] / "examples/field-notes"
    window = MainWindow()
    first, second = root / "field-notes-01.jpg", root / "field-notes-02.jpg"
    window.open_pair(first, first.with_suffix(".md"))
    assert window.navigate_page(1)
    assert window.current_image_path == second
    assert window.editor.toPlainText() == second.with_suffix(".md").read_text(
        encoding="utf-8"
    )
    assert window.navigate_page(-1)
    assert window.current_image_path == first
    window.close()


def wait_for(predicate, timeout=3000):
    from PySide6.QtCore import QEventLoop

    loop = QEventLoop()
    timer = QTimer()
    timer.timeout.connect(lambda: loop.quit() if predicate() else None)
    deadline = QTimer()
    deadline.setSingleShot(True)
    deadline.timeout.connect(loop.quit)
    timer.start(10)
    deadline.start(timeout)
    if not predicate():
        loop.exec()
    timer.stop()
    deadline.stop()
    assert predicate(), "timed out waiting for Qt event"


def test_added_last_page_enables_next_without_reopening(pages):
    window, images = pages
    assert window.navigate_page(1)
    assert window.navigate_page(1)
    assert not window.next_action.isEnabled()
    new_page = images[0].parent / "page-11.jpg"
    copyfile(images[0], new_page)
    wait_for(window.next_action.isEnabled)
    assert window.statusBar().currentMessage() == "Page 3 of 4"
    assert window.navigate_page(1)
    assert window.current_image_path == new_page
    assert not window.next_action.isEnabled()
    new_page.unlink()
    wait_for(lambda: not window.previous_action.isEnabled())
    assert window.current_image_path == new_page
    assert window.new_transcription


@pytest.mark.parametrize("phase", ["discovery", "load", "revalidation"])
def test_stalled_navigation_remains_cancellable(pages, monkeypatch, phase):
    from threading import Event, get_ident

    from PySide6.QtWidgets import QProgressDialog

    from textbeside import app

    window, _images = pages
    edit(window)
    before = state(window)
    started, release, finished = Event(), Event(), Event()
    ui_thread = get_ident()
    worker_threads = []
    original = app.discover_images if phase == "discovery" else app.load_page_data
    calls = 0

    def stalled(*args):
        nonlocal calls
        calls += 1
        worker_threads.append(get_ident())
        if phase != "revalidation" or calls == 2:
            started.set()
            release.wait(5)
        try:
            return original(*args)
        finally:
            if started.is_set():
                finished.set()

    target = "discover_images" if phase == "discovery" else "load_page_data"
    monkeypatch.setattr(app, target, stalled)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Discard)
    ticks = []
    timer = QTimer()

    def cancel_when_started():
        ticks.append(True)
        if started.is_set():
            progress = window.findChild(QProgressDialog)
            if progress is not None:
                progress.cancel()

    timer.timeout.connect(cancel_when_started)
    timer.start(10)
    try:
        assert not window.navigate_page(1)
        assert state(window) == before
        assert ticks and worker_threads
        assert all(thread != ui_thread for thread in worker_threads)
    finally:
        timer.stop()
        release.set()
    wait_for(finished.is_set)
    assert state(window) == before  # late completion cannot publish a page
