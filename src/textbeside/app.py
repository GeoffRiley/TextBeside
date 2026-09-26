"""Minimal split-view TextBeside prototype."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

TEXT_EXTENSIONS = {".md", ".txt"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def read_text_file(path: Path) -> str:
    """Return a supported transcription file as UTF-8 text."""
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError("Transcription files must use .md or .txt.")
    return path.read_text(encoding="utf-8")


def load_image(path: Path) -> QPixmap:
    """Load a supported image into a pixmap."""
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image type.")

    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        raise ValueError(f"Could not load image: {path.name}")
    return pixmap


class MainWindow(QMainWindow):
    """The first TextBeside split-view window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TextBeside")
        self.resize(1100, 700)

        self.current_text_path: Path | None = None
        self.current_image_path: Path | None = None

        self.text_path_label = QLabel("Text: no file selected")
        self.text_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Open a Markdown or text file to begin transcription.")

        self.image_path_label = QLabel("Image: no file selected")
        self.image_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.image_label = QLabel("Open an image to display it here.")
        self.image_label.setAlignment(Qt.AlignCenter)

        image_scroll = QScrollArea()
        image_scroll.setWidget(self.image_label)
        image_scroll.setWidgetResizable(True)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._pane(self.text_path_label, self.editor))
        splitter.addWidget(self._pane(self.image_path_label, image_scroll))
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([550, 550])
        self.splitter = splitter
        self.setCentralWidget(splitter)

        self._create_actions()
        self.statusBar().showMessage("Ready")

    @staticmethod
    def _pane(header: QLabel, content: QWidget) -> QWidget:
        pane = QWidget()
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(header)
        layout.addWidget(content, 1)
        return pane

    def _create_actions(self) -> None:
        open_pair_action = QAction("&Open pair…", self)
        open_pair_action.setShortcut(QKeySequence.Open)
        open_pair_action.triggered.connect(self.open_pair_dialog)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(open_pair_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

    def open_pair_dialog(self) -> None:
        """Choose an image and transcription file without directory scanning."""
        if not self._confirm_discard_if_modified():
            return

        image_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open source image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.tif *.tiff);;All files (*)",
        )
        if not image_name:
            return

        text_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open transcription",
            str(Path(image_name).parent),
            "Transcriptions (*.md *.txt);;All files (*)",
        )
        if not text_name:
            return

        try:
            self.open_pair(Path(image_name), Path(text_name))
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.critical(self, "Could not open pair", str(exc))

    def open_pair(self, image_path: Path, text_path: Path) -> None:
        """Load both files, then replace the visible pair only if both succeed."""
        text = read_text_file(text_path)
        pixmap = load_image(image_path)

        self.editor.setPlainText(text)
        self.editor.document().setModified(False)
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())

        self.current_text_path = text_path
        self.current_image_path = image_path
        self.text_path_label.setText(f"Text: {text_path.name}")
        self.text_path_label.setToolTip(str(text_path))
        self.image_path_label.setText(f"Image: {image_path.name}")
        self.image_path_label.setToolTip(str(image_path))

    def _confirm_discard_if_modified(self) -> bool:
        if not self.editor.document().isModified():
            return True

        answer = QMessageBox.question(
            self,
            "Discard unsaved changes?",
            "The current transcription has unsaved edits. "
            "Saving is not implemented in this prototype yet. "
            "Discard these edits?",
            QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        return answer == QMessageBox.Discard

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt API name
        if self._confirm_discard_if_modified():
            event.accept()
        else:
            event.ignore()


def main() -> int:
    """Launch TextBeside."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
