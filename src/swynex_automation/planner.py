from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .classifier import classify_file
from .hashing import sha256_file
from .metadata import extract_metadata
from .models import FileRecord
from .safety import safe_collision_name


def build_plan(files: list[Path], destination_dir: str | Path, categories: dict[str, list[str]] | None = None, date_folders: bool = False, dry_run: bool = True, duplicate_policy: str = "report_only", max_file_size: int | None = None) -> list[FileRecord]:
    if duplicate_policy not in {"report_only", "skip_identical"}:
        raise ValueError("duplicate_policy must be 'report_only' or 'skip_identical'.")
    if max_file_size is not None and max_file_size <= 0:
        raise ValueError("max_file_size must be greater than zero.")

    destination_root = Path(destination_dir)
    records: list[FileRecord] = []
    known_hashes: dict[str, Path] = {}
    if destination_root.exists():
        for existing_path in destination_root.rglob("*"):
            if existing_path.is_file() and not existing_path.is_symlink():
                known_hashes.setdefault(sha256_file(existing_path), existing_path)

    for file_path in files:
        metadata = extract_metadata(file_path)
        category = classify_file(file_path, categories)
        category_dir = destination_root / category
        resolved_category_dir = category_dir.resolve()
        resolved_destination_root = destination_root.resolve()
        if resolved_category_dir == resolved_destination_root:
            raise ValueError(f"Unsafe category directory: {category}")
        try:
            resolved_category_dir.relative_to(resolved_destination_root)
        except ValueError as exc:
            raise ValueError(f"Unsafe category directory: {category}") from exc
        dest_name = safe_collision_name(category_dir / file_path.name)
        if date_folders:
            date_dir = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC).strftime("%Y/%m/%d")
            dest_name = safe_collision_name(category_dir / date_dir / file_path.name)
        try:
            dest_name.parent.resolve().relative_to(resolved_destination_root)
        except ValueError as exc:
            raise ValueError(f"Unsafe destination path for category: {category}") from exc
        recorded_name = str(metadata["name"])
        recorded_size: int = int(metadata["size"])
        if max_file_size is not None and recorded_size > max_file_size:
            records.append(
                FileRecord(
                    source_path=file_path,
                    name=recorded_name,
                    extension=str(metadata["suffix"]),
                    size=recorded_size,
                    category=category,
                    destination_path=dest_name,
                    action="skip_too_large",
                    status="validation_failed",
                    error=f"File size {recorded_size} exceeds configured limit {max_file_size}.",
                )
            )
            continue

        file_hash = sha256_file(file_path)
        is_duplicate = file_hash in known_hashes
        known_hashes.setdefault(file_hash, file_path)
        if is_duplicate and duplicate_policy == "skip_identical":
            action = "skip_duplicate"
        elif is_duplicate:
            action = "report_duplicate"
        else:
            action = "dry_run_move" if dry_run else "move"
        record = FileRecord(
            source_path=file_path,
            name=recorded_name,
            extension=str(metadata["suffix"]),
            size=recorded_size,
            category=category,
            destination_path=dest_name,
            action=action,
            status="duplicate" if is_duplicate else "planned",
            sha256=file_hash,
        )
        records.append(record)
    return records
