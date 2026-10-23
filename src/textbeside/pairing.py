"""Resolve transcription counterparts without making filesystem changes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from textbeside.image_discovery import IMAGE_EXTENSIONS

TEXT_EXTENSIONS = (".md", ".txt")


class PairStatus(Enum):
    """The number of transcription choices associated with an image."""

    MISSING = "missing"
    MATCHED = "matched"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class PairResult:
    """An image and its zero, one, or multiple transcription candidates."""

    image_path: Path
    status: PairStatus
    candidates: tuple[Path, ...]

    @property
    def text_path(self) -> Path | None:
        """Return the unambiguous existing transcription, if any."""
        if self.status is PairStatus.MATCHED:
            return self.candidates[0]
        return None


def resolve_pair(image_path: Path) -> PairResult:
    """Inspect same-basename .md/.txt counterparts beside an image.

    Neither an absent transcription nor a conflict is resolved by guessing.
    This function performs no writes or text-file reads.
    """
    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image type: {image_path.name}")

    candidates = tuple(
        candidate
        for extension in TEXT_EXTENSIONS
        if (candidate := image_path.with_suffix(extension)).is_file()
    )
    if not candidates:
        status = PairStatus.MISSING
    elif len(candidates) == 1:
        status = PairStatus.MATCHED
    else:
        status = PairStatus.CONFLICT

    return PairResult(image_path, status, candidates)
