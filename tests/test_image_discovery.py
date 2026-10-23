"""Natural directory discovery for the upcoming paired-page workflow."""

from pathlib import Path

import pytest

from textbeside.image_discovery import discover_images


def test_numbered_images_sort_naturally(tmp_path: Path) -> None:
    for name in ("page10.png", "page2.png", "page1.png", "page11.jpg"):
        (tmp_path / name).touch()

    assert [path.name for path in discover_images(tmp_path)] == [
        "page1.png",
        "page2.png",
        "page10.png",
        "page11.jpg",
    ]


def test_discovery_ignores_other_files_and_subdirectories(tmp_path: Path) -> None:
    for name in ("scan2.TIF", "scan1.JpEg", "readme.md", "scan3.gif"):
        (tmp_path / name).touch()
    nested = tmp_path / "scan0.png"
    nested.mkdir()
    (nested / "page.jpg").touch()

    assert [path.name for path in discover_images(tmp_path)] == [
        "scan1.JpEg",
        "scan2.TIF",
    ]


def test_empty_directory(tmp_path: Path) -> None:
    assert discover_images(tmp_path) == []


def test_numeric_ties_have_deterministic_order(tmp_path: Path) -> None:
    for name in ("page02.png", "page2.png", "Page2.png"):
        (tmp_path / name).touch()

    first = [path.name for path in discover_images(tmp_path)]
    assert first == [path.name for path in discover_images(tmp_path)]
    assert len(first) == 3


def test_non_directory_raises(tmp_path: Path) -> None:
    file = tmp_path / "file.txt"
    file.touch()

    with pytest.raises(NotADirectoryError):
        discover_images(file)
