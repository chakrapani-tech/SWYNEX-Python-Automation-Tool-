from __future__ import annotations

from pathlib import Path


def validate_paths(source_dir: str | Path, destination_dir: str | Path) -> None:
    source = Path(source_dir).expanduser().resolve()
    destination = Path(destination_dir).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source}")
    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(f"Destination path is not a directory: {destination}")
    if source == destination:
        raise ValueError("Source and destination directories must be different.")

    try:
        source.relative_to(destination)
    except ValueError:
        pass
    else:
        raise ValueError("Source directory cannot be inside the destination directory.")

    try:
        destination.relative_to(source)
    except ValueError:
        pass
    else:
        raise ValueError("Destination directory cannot be inside the source directory.")


def safe_collision_name(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    while True:
        candidate = target_path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def directory_is_unsafe(candidate_dir: str | Path, source_dir: str | Path) -> bool:
    candidate = Path(candidate_dir).expanduser().resolve()
    source = Path(source_dir).expanduser().resolve()
    return candidate == source or source in candidate.parents or candidate in source.parents
