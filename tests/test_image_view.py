"""Tests for the interactive source-image view."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QPixmap

from textbeside.image_view import ImageView


def _sample_pixmap() -> QPixmap:
    root = Path(__file__).resolve().parents[1]
    return QPixmap(str(root / "examples" / "field-notes" / "field-notes-01.jpg"))


def test_image_starts_fitted(qapp) -> None:
    view = ImageView()
    view.resize(500, 400)
    view.show()
    view.set_image(_sample_pixmap())

    assert view.has_image
    assert view.is_fit_mode
    assert view.zoom_factor > 0

    view.close()


def test_actual_size_sets_100_percent(qapp) -> None:
    view = ImageView()
    view.resize(500, 400)
    view.show()
    view.set_image(_sample_pixmap())

    view.actual_size()

    assert not view.is_fit_mode
    assert view.zoom_percent == 100

    view.close()


def test_programmatic_zoom_is_clamped(qapp) -> None:
    view = ImageView()
    view.set_image(_sample_pixmap())

    view.set_zoom_factor(100)
    assert view.zoom_factor == view.MAX_ZOOM

    view.set_zoom_factor(0.001)
    assert view.zoom_factor == view.MIN_ZOOM

    view.close()
