from __future__ import annotations

import fnmatch
from pathlib import Path


def discover_files(source_dir: str | Path, recursive: bool = True, include_patterns: list[str] | None = None, exclude_patterns: list[str] | None = None) -> list[Path]:
    source = Path(source_dir)
    include = include_patterns or ["*.*"]
    exclude = exclude_patterns or []
    discovered: list[Path] = []

    if recursive:
        iterator = source.rglob("*")
    else:
        iterator = source.iterdir()

    for path in iterator:
        if not path.is_file() or path.is_symlink():
            continue
        name = path.name
        if any(part in name for part in (".tmp", ".temp", "~$")):
            continue
        if any(fnmatch.fnmatch(name, pattern) for pattern in exclude):
            continue
        if not any(fnmatch.fnmatch(name, pattern) for pattern in include):
            continue
        if any(part in str(path.relative_to(source)).split("\\") for part in exclude):
            continue
        discovered.append(path)
    return sorted(discovered)
