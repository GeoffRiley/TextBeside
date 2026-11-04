"""A lazy page model: paths stay plain data until the view requests a row."""

from pathlib import Path

from PySide6.QtCore import QAbstractListModel, Qt


class PageListModel(QAbstractListModel):
    """Avoid constructing an item object for every image in large folders."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths: list[Path] = []

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.paths)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.paths):
            return None
        path = self.paths[index.row()]
        if role == Qt.DisplayRole:
            return path.name
        if role in (Qt.UserRole, Qt.ToolTipRole):
            return str(path)
        return None

    def replace(self, paths: list[Path]) -> None:
        """Swap a discovery snapshot without materializing per-row UI objects."""
        self.beginResetModel()
        self.paths = paths
        self.endResetModel()

    def row_for(self, path: Path | None) -> int:
        try:
            return self.paths.index(path)
        except ValueError:
            return -1
