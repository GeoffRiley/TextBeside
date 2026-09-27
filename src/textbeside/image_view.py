"""Interactive image view for transcription source pages."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImageView(QGraphicsView):
    """Display one source image with pointer-centred zoom and drag panning."""

    zoom_changed = Signal(int)

    MIN_ZOOM = 0.10
    MAX_ZOOM = 8.00
    WHEEL_STEP = 1.20

    def __init__(self) -> None:
        super().__init__()

        scene = QGraphicsScene(self)
        self.setScene(scene)

        self._pixmap_item = QGraphicsPixmapItem()
        scene.addItem(self._pixmap_item)

        self._fit_mode = True
        self._has_image = False

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setAlignment(Qt.AlignCenter)

    @property
    def has_image(self) -> bool:
        """Whether a usable pixmap is currently displayed."""
        return self._has_image

    @property
    def zoom_factor(self) -> float:
        """Return the current view scale relative to source-image pixels."""
        return self.transform().m11()

    @property
    def zoom_percent(self) -> int:
        """Return the current view scale as a rounded percentage."""
        return round(self.zoom_factor * 100)

    @property
    def is_fit_mode(self) -> bool:
        """Whether resizing should continue to fit the whole image."""
        return self._fit_mode

    def set_image(self, pixmap: QPixmap) -> None:
        """Display *pixmap* and initially fit it to the viewport."""
        self._pixmap_item.setPixmap(pixmap)
        self.scene().setSceneRect(self._pixmap_item.boundingRect())
        self._has_image = not pixmap.isNull()

        if self._has_image:
            self.viewport().setCursor(Qt.OpenHandCursor)
            self.fit_image()
        else:
            self.resetTransform()
            self._emit_zoom()

    def fit_image(self) -> None:
        """Fit the entire source image in the available viewport."""
        if not self._has_image:
            return

        self.resetTransform()
        self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
        self._fit_mode = True
        self._emit_zoom()

    def actual_size(self) -> None:
        """Show the image at 100%, where one image pixel maps to one view unit."""
        if not self._has_image:
            return

        center = self.mapToScene(self.viewport().rect().center())
        self.resetTransform()
        self._fit_mode = False
        self.centerOn(center)
        self._emit_zoom()

    def set_zoom_factor(self, factor: float) -> None:
        """Set a clamped zoom factor, preserving the current view centre."""
        if not self._has_image:
            return

        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        center = self.mapToScene(self.viewport().rect().center())

        self.resetTransform()
        self.scale(factor, factor)
        self.centerOn(center)
        self._fit_mode = False
        self._emit_zoom()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom around the point beneath the mouse wheel pointer."""
        if not self._has_image or event.angleDelta().y() == 0:
            super().wheelEvent(event)
            return

        viewport_pos = event.position().toPoint()
        scene_pos_before = self.mapToScene(viewport_pos)

        requested = (
            self.zoom_factor * self.WHEEL_STEP
            if event.angleDelta().y() > 0
            else self.zoom_factor / self.WHEEL_STEP
        )
        target = max(self.MIN_ZOOM, min(self.MAX_ZOOM, requested))
        scale_factor = target / self.zoom_factor

        if scale_factor != 1.0:
            self.scale(scale_factor, scale_factor)
            scene_pos_after = self.mapToScene(viewport_pos)
            offset = scene_pos_after - scene_pos_before
            self.translate(offset.x(), offset.y())
            self._fit_mode = False
            self._emit_zoom()

        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Use a closed-hand cursor while the left button is panning."""
        if self._has_image and event.button() == Qt.LeftButton:
            self.viewport().setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Restore the open-hand cursor after panning."""
        super().mouseReleaseEvent(event)
        if self._has_image and event.button() == Qt.LeftButton:
            self.viewport().setCursor(Qt.OpenHandCursor)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Keep fitted images fitted while preserving manual zoom otherwise."""
        super().resizeEvent(event)
        if self._fit_mode and self._has_image:
            self.fit_image()

    def showEvent(self, event) -> None:
        """Use an open-hand cursor once the view is visible."""
        super().showEvent(event)
        if self._has_image:
            self.viewport().setCursor(Qt.OpenHandCursor)

    def _emit_zoom(self) -> None:
        self.zoom_changed.emit(self.zoom_percent)
