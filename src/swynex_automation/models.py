from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class FileRecord:
    source_path: Path
    name: str
    extension: str
    size: int = 0
    category: str = "Others"
    sha256: str | None = None
    status: str = "discovered"
    action: str = "pending"
    destination_path: Path | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "category": self.category,
            "sha256": self.sha256,
            "status": self.status,
            "action": self.action,
            "destination_path": str(self.destination_path) if self.destination_path else None,
            "error": self.error,
        }


@dataclass
class RunSummary:
    run_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source_dir: str = ""
    destination_dir: str = ""
    total_files: int = 0
    files_processed: int = 0
    files_skipped: int = 0
    duplicate_files: int = 0
    validation_failures: int = 0
    processing_errors: int = 0
    total_bytes: int = 0
    execution_duration_seconds: float = 0.0
    dry_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "source_dir": self.source_dir,
            "destination_dir": self.destination_dir,
            "total_files": self.total_files,
            "files_processed": self.files_processed,
            "files_skipped": self.files_skipped,
            "duplicate_files": self.duplicate_files,
            "validation_failures": self.validation_failures,
            "processing_errors": self.processing_errors,
            "total_bytes": self.total_bytes,
            "execution_duration_seconds": self.execution_duration_seconds,
            "dry_run": self.dry_run,
        }
