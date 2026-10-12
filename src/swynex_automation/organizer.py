from __future__ import annotations

import shutil
from pathlib import Path

from .models import FileRecord
from .safety import safe_collision_name


def execute_plan(records: list[FileRecord], execute: bool = False) -> list[FileRecord]:
    for record in records:
        if record.status in {"validation_failed", "failed", "skipped"}:
            continue
        if record.status == "duplicate" and record.action == "skip_duplicate":
            if execute:
                record.status = "skipped"
            continue
        if record.destination_path is None:
            record.error = "No destination path defined."
            record.status = "failed"
            continue
        if not execute:
            if record.status != "duplicate":
                record.status = "planned"
                record.action = "dry_run_move"
            elif record.action == "report_duplicate":
                record.action = "dry_run_report_duplicate"
            continue

        destination = Path(record.destination_path)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            final_dest = safe_collision_name(destination)
            shutil.move(str(record.source_path), str(final_dest))
            record.destination_path = final_dest
            if record.status == "duplicate":
                record.action = "moved_duplicate"
            else:
                record.status = "processed"
                record.action = "moved"
        except OSError as exc:  # pragma: no cover - safety catch
            record.error = str(exc)
            record.status = "failed"
            record.action = "move_failed"
    return records
