"""Regression tests for explicit image/transcription pairing."""

from pathlib import Path

import pytest

from textbeside.pairing import PairStatus, resolve_pair


def test_markdown_counterpart(tmp_path: Path) -> None:
    image = tmp_path / "page01.jpg"
    text = tmp_path / "page01.md"
    image.touch()
    text.write_text("Café", encoding="utf-8")

    result = resolve_pair(image)

    assert result.status is PairStatus.MATCHED
    assert result.candidates == (text,)
    assert result.text_path == text
    assert text.read_text(encoding="utf-8") == "Café"


def test_plain_text_counterpart(tmp_path: Path) -> None:
    image = tmp_path / "page02.png"
    text = tmp_path / "page02.txt"
    image.touch()
    text.touch()

    result = resolve_pair(image)

    assert result.status is PairStatus.MATCHED
    assert result.text_path == text


def test_missing_counterpart(tmp_path: Path) -> None:
    image = tmp_path / "page03.tif"
    image.touch()

    result = resolve_pair(image)

    assert result.status is PairStatus.MISSING
    assert result.candidates == ()
    assert result.text_path is None
    assert sorted(path.name for path in tmp_path.iterdir()) == ["page03.tif"]


def test_both_formats_report_conflict(tmp_path: Path) -> None:
    image = tmp_path / "page04.webp"
    md = tmp_path / "page04.md"
    txt = tmp_path / "page04.txt"
    for path in (image, md, txt):
        path.touch()

    result = resolve_pair(image)

    assert result.status is PairStatus.CONFLICT
    assert result.candidates == (md, txt)
    assert result.text_path is None


def test_multiple_dots_and_unrelated_files(tmp_path: Path) -> None:
    image = tmp_path / "record.1901.page2.jpeg"
    text = tmp_path / "record.1901.page2.md"
    unrelated = tmp_path / "record.md"
    for path in (image, text, unrelated):
        path.touch()

    result = resolve_pair(image)

    assert result.text_path == text
    assert result.candidates == (text,)


def test_directory_is_not_a_counterpart(tmp_path: Path) -> None:
    image = tmp_path / "page05.jpg"
    image.touch()
    (tmp_path / "page05.md").mkdir()

    assert resolve_pair(image).status is PairStatus.MISSING


def test_unsupported_image_type_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported image"):
        resolve_pair(tmp_path / "notes.pdf")
