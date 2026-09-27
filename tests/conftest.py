"""Pytest configuration for Qt smoke tests."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Provide one QApplication instance for Qt tests."""
    return QApplication.instance() or QApplication([])
