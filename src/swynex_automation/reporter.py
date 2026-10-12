from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from .models import FileRecord, RunSummary


def write_reports(run: RunSummary, records: Iterable[FileRecord], report_dir: str | Path, formats: Iterable[str]) -> list[Path]:
    report_root = Path(report_dir)
    report_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    for fmt in formats:
        if fmt == "csv":
            output_path = report_root / f"{run.run_id}_{timestamp}.csv"
            with output_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["source_path", "name", "extension", "size", "category", "sha256", "status", "action", "destination_path", "error"])
                writer.writeheader()
                for record in records:
                    writer.writerow(record.to_dict())
        elif fmt == "json":
            output_path = report_root / f"{run.run_id}_{timestamp}.json"
            with output_path.open("w", encoding="utf-8") as handle:
                json.dump({"run": run.to_dict(), "records": [record.to_dict() for record in records]}, handle, indent=2)
        else:
            continue
        created.append(output_path)
    return created


def build_summary(records: list[FileRecord], run: RunSummary) -> RunSummary:
    run.total_files = len(records)
    run.files_processed = sum(
        1
        for record in records
        if record.status == "processed" or record.action == "moved_duplicate"
    )
    run.files_skipped = sum(1 for record in records if record.status == "skipped")
    run.duplicate_files = sum(
        1
        for record in records
        if record.status == "duplicate"
        or record.action in {"skip_duplicate", "moved_duplicate", "dry_run_report_duplicate"}
    )
    run.validation_failures = sum(1 for record in records if record.status == "validation_failed")
    run.processing_errors = sum(1 for record in records if record.status == "failed")
    run.total_bytes = sum(record.size for record in records)
    return run
