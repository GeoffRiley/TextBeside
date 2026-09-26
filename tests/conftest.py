"""Pytest configuration for Qt smoke tests."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
