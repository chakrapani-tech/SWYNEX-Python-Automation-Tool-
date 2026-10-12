from pathlib import Path

import pytest

from src.swynex_automation.safety import safe_collision_name, validate_paths


def test_validate_paths_accepts_source_and_destination(tmp_path: Path):
    source = tmp_path / "src"
    destination = tmp_path / "dest"
    source.mkdir()
    destination.mkdir()
    validate_paths(source, destination)


def test_validate_paths_rejects_same_directory(tmp_path: Path):
    source = tmp_path / "src"
    source.mkdir()
    with pytest.raises(ValueError):
        validate_paths(source, source)


def test_validate_paths_rejects_destination_nested_in_source(tmp_path: Path):
    source = tmp_path / "source"
    destination = source / "destination"
    destination.mkdir(parents=True)

    with pytest.raises(ValueError, match="Destination directory cannot be inside"):
        validate_paths(source, destination)


def test_validate_paths_rejects_source_nested_in_destination(tmp_path: Path):
    destination = tmp_path / "destination"
    source = destination / "source"
    source.mkdir(parents=True)

    with pytest.raises(ValueError, match="Source directory cannot be inside"):
        validate_paths(source, destination)


def test_safe_collision_name_resolves_duplicates(tmp_path: Path):
    target = tmp_path / "file.txt"
    target.write_text("first", encoding="utf-8")
    result = safe_collision_name(target)
    assert result.name == "file_1.txt"
