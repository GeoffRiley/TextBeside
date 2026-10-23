"""Safe plain-text file operations for TextBeside."""

from __future__ import annotations

import errno
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


def _exclusive_create_fallback(path: Path, text: str) -> FileSignature:
    """Create on filesystems without hard links, never replacing a target.

    A failed write leaves a partial file in place: deleting the destination
    would risk deleting a different process's replacement of that name.
    """
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
        info = os.fstat(handle.fileno())
    return FileSignature(mtime_ns=info.st_mtime_ns, size=info.st_size)


def create_text_file_exclusive(path: Path, text: str) -> FileSignature:
    """Publish new UTF-8 text without replacing another file.

    Prefer a fully synchronised private temporary file, published via a
    no-clobber hard link. Fall back to O_EXCL creation where hard links are
    unsupported. Fallback write errors preserve partial files for recovery.
    """
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
            info = os.fstat(handle.fileno())
            signature = FileSignature(mtime_ns=info.st_mtime_ns, size=info.st_size)

        try:
            os.link(temp_path, path)
        except OSError as exc:
            unsupported = {
                errno.ENOSYS,
                errno.EPERM,
                errno.EOPNOTSUPP,
                errno.ENOTSUP,
            }
            # Windows may report unsupported operations with a WinError
            # unrelated to errno (ERROR_INVALID_FUNCTION / NOT_SUPPORTED).
            if exc.errno not in unsupported and getattr(exc, "winerror", None) not in (
                1,
                50,
            ):
                raise
            return _exclusive_create_fallback(path, text)
        return signature
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            # Cleanup must never turn a published transcription into a
            # reported save failure.
            pass
