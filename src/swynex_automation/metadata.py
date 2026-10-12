from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def extract_metadata(path: str | Path) -> dict[str, str | int]:
    file_path = Path(path)
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "suffix": file_path.suffix.lower(),
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
        "absolute_path": str(file_path.resolve()),
    }
