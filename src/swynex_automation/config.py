from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .safety import validate_paths


@dataclass
class AppConfig:
    source_dir: str
    destination_dir: str
    recursive: bool = True
    include_patterns: list[str] = field(default_factory=lambda: ["*.*"])
    exclude_patterns: list[str] = field(default_factory=lambda: ["__pycache__", ".git", "tmp", "temp", ".DS_Store"])
    max_file_size: int = 500 * 1024 * 1024
    duplicate_policy: str = "report_only"
    report_dir: str = "reports"
    log_level: str = "INFO"
    dry_run_default: bool = True
    quarantine_dir: str = "quarantine"
    date_folders: bool = False
    categories: dict[str, list[str]] = field(
        default_factory=lambda: {
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
            "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"],
            "Videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv"],
            "Audio": [".mp3", ".wav", ".flac", ".ogg"],
            "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
            "Source Code": [".py", ".js", ".ts", ".java", ".go", ".rs", ".c", ".cpp", ".cs"],
            "Spreadsheets": [".csv", ".xls", ".xlsx", ".ods"],
            "Presentations": [".ppt", ".pptx"],
            "Data Files": [".json", ".xml", ".yaml", ".yml"],
            "Executables": [".exe", ".msi", ".bat", ".sh"],
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_dir": self.source_dir,
            "destination_dir": self.destination_dir,
            "recursive": self.recursive,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "max_file_size": self.max_file_size,
            "duplicate_policy": self.duplicate_policy,
            "report_dir": self.report_dir,
            "log_level": self.log_level,
            "dry_run_default": self.dry_run_default,
            "quarantine_dir": self.quarantine_dir,
            "date_folders": self.date_folders,
            "categories": self.categories,
        }


def load_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path) if path else Path("config/example_config.json")
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        config = AppConfig(**payload)
    else:
        config = build_default_config()

    validate_config(config)
    return config


def build_default_config() -> AppConfig:
    root = Path.cwd()
    return AppConfig(
        source_dir=str(root / "input"),
        destination_dir=str(root / "organized"),
        report_dir=str(root / "reports"),
        quarantine_dir=str(root / "quarantine"),
    )


def validate_config(config: AppConfig) -> None:
    if not config.source_dir:
        raise ValueError("Source directory is required.")
    if not config.destination_dir:
        raise ValueError("Destination directory is required.")
    if config.max_file_size <= 0:
        raise ValueError("max_file_size must be greater than zero.")
    if config.duplicate_policy not in {"report_only", "skip_identical"}:
        raise ValueError("duplicate_policy must be 'report_only' or 'skip_identical'.")
    if config.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("Invalid logging level.")

    source = Path(config.source_dir)
    destination = Path(config.destination_dir)
    validate_paths(source, destination)
