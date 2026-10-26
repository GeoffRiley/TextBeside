"""Manual pairing confirmation and transactional opening."""

from pathlib import Path

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox

from textbeside.app import MainWindow


@pytest.fixture
def working(qapp, tmp_path):
    window = MainWindow()
    image = (
        Path(__file__).resolve().parents[1] / "examples/field-notes/field-notes-01.jpg"
    )
    text = tmp_path / "current.md"
    text.write_text("original", encoding="utf-8")
    window.open_pair(image, text)
    window.editor.setPlainText("unsaved work")
    window.editor.document().setModified(True)
    yield window, image, text
    window.editor.document().setModified(False)
    window.close()


def snapshot(window):
    return (
        window.current_image_path,
        window.current_text_path,
        window.current_text_signature,
        window.new_transcription,
        window.editor.toPlainText(),
        window.editor.document().isModified(),
        window.image_path_label.text(),
        window.text_path_label.text(),
        window.image_view.has_image,
    )


def pick(monkeypatch, image, text):
    choices = iter([(str(image), ""), (str(text), "")])
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a: next(choices))


@pytest.mark.parametrize("stage", ["image", "text", "warning", "load", "save_cancel"])
def test_cancel_or_failure_preserves_work(working, tmp_path, monkeypatch, stage):
    window, image, _current = working
    target = tmp_path / "different.txt"
    target.write_text("destination", encoding="utf-8")
    before = snapshot(window)
    files = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    pick(
        monkeypatch,
        "" if stage == "image" else image,
        "" if stage == "text" else target,
    )
    monkeypatch.setattr(
        window, "_confirm_mismatched_pair", lambda *a: stage != "warning"
    )
    if stage == "load":
        monkeypatch.setattr(
            "textbeside.app.load_image",
            lambda p: (_ for _ in ()).throw(ValueError("unreadable")),
        )
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: None)

    def save_prompt(*a):
        assert stage == "save_cancel", (
            "must not prompt before cancellation or failed loading"
        )
        return QMessageBox.Cancel

    monkeypatch.setattr(QMessageBox, "question", save_prompt)
    window.open_pair_dialog()
    assert snapshot(window) == before
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == files


@pytest.mark.parametrize(
    "stem,warning",
    [("field-notes-01", False), ("FIELD-NOTES-01", True), ("unrelated", True)],
)
@pytest.mark.parametrize("decision", [QMessageBox.Save, QMessageBox.Discard])
def test_confirmed_open_and_unsaved_protection(
    working, tmp_path, monkeypatch, stem, warning, decision
):
    window, image, current = working
    target = tmp_path / (stem + ".txt")
    target.write_text("chosen destination", encoding="utf-8")
    pick(monkeypatch, image, target)
    warnings = []
    monkeypatch.setattr(
        window, "_confirm_mismatched_pair", lambda *a: warnings.append(a) or True
    )
    monkeypatch.setattr(QMessageBox, "question", lambda *a: decision)
    window.open_pair_dialog()
    assert bool(warnings) == warning
    assert window.current_text_path == target
    assert window.editor.toPlainText() == "chosen destination"
    assert not window.editor.document().isModified()
    assert current.read_text() == (
        "unsaved work" if decision == QMessageBox.Save else "original"
    )
    assert target.read_text() == "chosen destination"


def test_reopening_saved_current_file_keeps_latest_text(working, monkeypatch):
    window, image, current = working
    pick(monkeypatch, image, current)
    monkeypatch.setattr(window, "_confirm_mismatched_pair", lambda *a: True)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Save)
    window.open_pair_dialog()
    assert window.editor.toPlainText() == "unsaved work"
    assert current.read_text() == "unsaved work"


@pytest.mark.parametrize("action", ["open", "cancel", "escape", "close"])
def test_real_warning_requires_explicit_open(working, action):
    window, image, current = working

    def interact():
        box = window.findChild(QMessageBox)
        assert image.name in box.text() and current.name in box.text()
        assert box.textFormat() == Qt.PlainText
        assert box.defaultButton() == box.button(QMessageBox.Cancel)
        assert box.escapeButton() == box.button(QMessageBox.Cancel)
        if action == "open":
            next(b for b in box.buttons() if b.text() == "Open anyway").click()
        elif action == "cancel":
            box.button(QMessageBox.Cancel).click()
        elif action == "escape":
            box.reject()
        else:
            box.close()

    QTimer.singleShot(0, interact)
    assert window._confirm_mismatched_pair(image, current) == (action == "open")


def test_failed_save_aborts_open(working, tmp_path, monkeypatch):
    window, image, _current = working
    target = tmp_path / "different.txt"
    target.write_text("destination", encoding="utf-8")
    before = snapshot(window)
    pick(monkeypatch, image, target)
    monkeypatch.setattr(window, "_confirm_mismatched_pair", lambda *a: True)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Save)
    monkeypatch.setattr(window, "save_current_text", lambda: False)
    window.open_pair_dialog()
    assert snapshot(window) == before
