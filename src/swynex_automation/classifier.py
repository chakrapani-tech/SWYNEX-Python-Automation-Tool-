from __future__ import annotations

from pathlib import Path

DEFAULT_CATEGORIES = {
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


def classify_file(path: str | Path, categories: dict[str, list[str]] | None = None) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    mapping = categories or DEFAULT_CATEGORIES
    for category, exts in mapping.items():
        if suffix in {ext.lower() for ext in exts}:
            return category
    return "Others"


def classify_by_name(path: str | Path, patterns: dict[str, list[str]] | None = None) -> str:
    file_path = Path(path)
    name = file_path.name.lower()
    mapping = patterns or {}
    for category, entries in mapping.items():
        for entry in entries:
            if entry.lower() in name:
                return category
    return "Others"
