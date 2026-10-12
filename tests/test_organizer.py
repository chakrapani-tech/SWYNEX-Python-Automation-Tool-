from pathlib import Path

from src.swynex_automation.models import FileRecord
from src.swynex_automation.organizer import execute_plan


def test_execute_plan_dry_run_does_not_move(tmp_path: Path):
    source = tmp_path / "source.txt"
    source.write_text("hello", encoding="utf-8")
    destination = tmp_path / "destination"
    destination.mkdir()
    records = [FileRecord(source_path=source, name="source.txt", extension=".txt", size=5, action="dry_run_move", status="planned", destination_path=destination / "source.txt")]
    result = execute_plan(records, execute=False)
    assert result[0].status == "planned"
    assert source.exists()
    assert not (destination / "source.txt").exists()


def test_execute_plan_uses_collision_safe_name(tmp_path: Path):
    source = tmp_path / "source" / "same.txt"
    source.parent.mkdir()
    source.write_text("new content", encoding="utf-8")
    destination = tmp_path / "destination" / "Documents"
    destination.mkdir(parents=True)
    existing = destination / "same.txt"
    existing.write_text("existing content", encoding="utf-8")
    record = FileRecord(
        source_path=source,
        name=source.name,
        extension=".txt",
        destination_path=existing,
    )

    result = execute_plan([record], execute=True)

    assert result[0].status == "processed"
    assert result[0].destination_path == destination / "same_1.txt"
    assert existing.read_text(encoding="utf-8") == "existing content"
    assert (destination / "same_1.txt").read_text(encoding="utf-8") == "new content"
    assert not source.exists()
