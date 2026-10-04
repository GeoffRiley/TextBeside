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
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from textbeside.file_ops import FileSignature, file_signature, write_text_file_atomic
from textbeside.image_view import ImageView

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
        self.current_text_signature: FileSignature | None = None

        self.text_path_label = QLabel("Text: no file selected")
        self.text_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(
            "Open a Markdown or text file to begin transcription."
        )
        self.editor.document().modificationChanged.connect(self._update_text_label)

        self.image_path_label = QLabel("Image: no file selected")
        self.image_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.image_view = ImageView()
        self.image_view.zoom_changed.connect(self._update_image_label)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._pane(self.text_path_label, self.editor))
        splitter.addWidget(self._pane(self.image_path_label, self.image_view))
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

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_current_text)

        fit_image_action = QAction("&Fit image", self)
        fit_image_action.setShortcut("Ctrl+0")
        fit_image_action.triggered.connect(self.fit_image)

        actual_size_action = QAction("&100%", self)
        actual_size_action.setShortcut("Ctrl+1")
        actual_size_action.triggered.connect(self.actual_size)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(open_pair_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(fit_image_action)
        view_menu.addAction(actual_size_action)

    def open_pair_dialog(self) -> None:
        """Choose an image and transcription file without directory scanning."""
        if not self._confirm_save_or_discard_if_modified():
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

        self.current_text_path = text_path
        self.current_image_path = image_path
        self.current_text_signature = file_signature(text_path)

        self.editor.setPlainText(text)
        self.editor.document().setModified(False)
        self._update_text_label(False)
        self.text_path_label.setToolTip(str(text_path))
        self.image_path_label.setToolTip(str(image_path))
        self.image_view.set_image(pixmap)

    def _update_text_label(self, modified: bool | None = None) -> None:
        """Show the current transcription filename and save state."""
        if self.current_text_path is None:
            self.text_path_label.setText("Text: no file selected")
            return

        if modified is None:
            modified = self.editor.document().isModified()

        state = "Modified" if modified else "Saved"
        self.text_path_label.setText(
            f"Text: {self.current_text_path.name} · {state}"
        )

    def save_current_text(self) -> bool:
        """Safely save the active transcription if one is open."""
        if self.current_text_path is None:
            return False

        try:
            current_signature = file_signature(self.current_text_path)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Could not save transcription",
                f"Could not inspect the current file before saving:\n{exc}",
            )
            return False

        if (
            self.current_text_signature is not None
            and current_signature != self.current_text_signature
            and not self._confirm_external_overwrite()
        ):
            return False

        try:
            new_signature = write_text_file_atomic(
                self.current_text_path,
                self.editor.toPlainText(),
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Could not save transcription",
                f"The transcription was not saved. Your edits remain in the editor.\n\n{exc}",
            )
            return False

        self.current_text_signature = new_signature
        self.editor.document().setModified(False)
        self._update_text_label(False)
        return True

    def _confirm_external_overwrite(self) -> bool:
        """Require explicit confirmation before overwriting an externally changed file."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Transcription changed on disk")
        box.setText(
            "The transcription file has changed outside TextBeside since it was opened."
        )
        box.setInformativeText(
            "Overwrite the disk version with the text currently in the editor?"
        )
        overwrite_button = box.addButton(
            "Overwrite",
            QMessageBox.ButtonRole.AcceptRole,
        )
        box.addButton(QMessageBox.Cancel)
        box.setDefaultButton(QMessageBox.Cancel)
        box.exec()
        return box.clickedButton() is overwrite_button

    def _update_image_label(self, zoom_percent: int) -> None:
        """Show the current image filename and zoom level."""
        if self.current_image_path is None:
            self.image_path_label.setText(f"Image: no file selected · {zoom_percent}%")
            return

        self.image_path_label.setText(
            f"Image: {self.current_image_path.name} · {zoom_percent}%"
        )

    def fit_image(self) -> None:
        """Fit the current image in its pane."""
        self.image_view.fit_image()

    def actual_size(self) -> None:
        """Show the current image at 100%."""
        self.image_view.actual_size()

    def _confirm_save_or_discard_if_modified(self) -> bool:
        if not self.editor.document().isModified():
            return True

        answer = QMessageBox.question(
            self,
            "Save changes?",
            "The current transcription has unsaved edits.",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )

        if answer == QMessageBox.Save:
            return self.save_current_text()
        if answer == QMessageBox.Discard:
            return True
        return False

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._confirm_save_or_discard_if_modified():
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
