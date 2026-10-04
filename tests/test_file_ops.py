"""Tests for safe plain-text file operations."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from textbeside.file_ops import file_signature, write_text_file_atomic


def test_atomic_save_writes_utf8_and_preserves_permissions(tmp_path: Path) -> None:
    path = tmp_path / "transcription.md"
    path.write_text("old text\n", encoding="utf-8")
    path.chmod(0o640)

    signature = write_text_file_atomic(path, "café — naïve\n")

    assert path.read_bytes() == "café — naïve\n".encode("utf-8")
    assert signature == file_signature(path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o640


def test_atomic_save_failure_leaves_original_intact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "transcription.txt"
    path.write_text("original", encoding="utf-8")

    def fail_replace(source: Path | str, destination: Path | str) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(OSError, match="simulated replace failure"):
        write_text_file_atomic(path, "new text")

    assert path.read_text(encoding="utf-8") == "original"
    assert not list(tmp_path.glob(".transcription.txt.*.tmp"))
