"""Safe plain-text file operations for TextBeside."""

from __future__ import annotations

import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileSignature:
    """Lightweight fingerprint used to notice out-of-process file changes."""

    mtime_ns: int
    size: int


def file_signature(path: Path) -> FileSignature:
    """Return the current modification time and byte length for path."""
    stat = path.stat()
    return FileSignature(mtime_ns=stat.st_mtime_ns, size=stat.st_size)


def write_text_file_atomic(path: Path, text: str) -> FileSignature:
    """Atomically replace path with UTF-8 encoded text.

    The temporary file is created in the same directory so os.replace stays
    on the same filesystem. If any step fails before replacement, the original
    file is left untouched.
    """
    original_mode = stat.S_IMODE(path.stat().st_mode)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temp_path = Path(temp_name)

    try:
        os.chmod(temp_path, original_mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_path, path)
        return file_signature(path)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
