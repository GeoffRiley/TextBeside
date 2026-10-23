"""Discover source images without modifying the user's directory."""

from __future__ import annotations

import re
from pathlib import Path

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"})
_NUMBERS = re.compile(r"(\d+)")


def natural_sort_key(name: str) -> tuple:
    """Sort embedded decimal numbers numerically, with deterministic ties."""
    parts = _NUMBERS.split(name.casefold())
    key = tuple((1, int(part)) if part.isdecimal() else (0, part) for part in parts)
    return key, name.casefold(), name


def discover_images(directory: Path) -> list[Path]:
    """Return supported files immediately inside *directory* in natural order.

    Raises OSError for an inaccessible or missing directory, and
    NotADirectoryError when *directory* is not a directory.
    """
    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda path: natural_sort_key(path.name),
    )
