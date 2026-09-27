"""Pytest configuration for Qt smoke tests."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Provide one QApplication instance for Qt tests."""
    return QApplication.instance() or QApplication([])
