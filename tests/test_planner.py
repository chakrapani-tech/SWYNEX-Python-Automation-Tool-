from pathlib import Path

from src.swynex_automation.models import RunSummary
from src.swynex_automation.organizer import execute_plan
from src.swynex_automation.planner import build_plan
from src.swynex_automation.reporter import build_summary


def test_build_plan_classifies_into_category_subfolders(tmp_path: Path):
    source = tmp_path / "photo.JPG"
    source.write_bytes(b"not-decoded-as-an-image")

    record = build_plan([source], tmp_path / "organized")[0]

    assert record.category == "Images"
    assert record.destination_path == tmp_path / "organized" / "Images" / "photo.JPG"
    assert record.sha256 is not None


def test_build_plan_detects_duplicates_and_respects_skip_policy(tmp_path: Path):
    first = tmp_path / "first.txt"
    duplicate = tmp_path / "duplicate.txt"
    first.write_bytes(b"same bytes")
    duplicate.write_bytes(b"same bytes")
    destination = tmp_path / "organized"

    report_records = build_plan([first, duplicate], destination)
    skip_records = build_plan([first, duplicate], destination, duplicate_policy="skip_identical")

    assert report_records[0].status == "planned"
    assert report_records[1].status == "duplicate"
    assert report_records[1].action == "report_duplicate"
    assert report_records[0].sha256 == report_records[1].sha256
    assert skip_records[1].status == "duplicate"
    assert skip_records[1].action == "skip_duplicate"

    moved_records = execute_plan(report_records, execute=True)
    assert [record.action for record in moved_records] == ["moved", "moved_duplicate"]
    assert [record.status for record in moved_records] == ["processed", "duplicate"]
    assert (destination / "Documents" / "first.txt").read_bytes() == b"same bytes"
    assert (destination / "Documents" / "duplicate.txt").read_bytes() == b"same bytes"
    summary = build_summary(moved_records, RunSummary(run_id="report-only-run"))
    assert summary.files_processed == 2
    assert summary.duplicate_files == 1


def test_build_plan_detects_identical_existing_destination_content(tmp_path: Path):
    source = tmp_path / "incoming.txt"
    source.write_bytes(b"already present")
    existing = tmp_path / "organized" / "Documents" / "existing.txt"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(source.read_bytes())

    record = build_plan(
        [source],
        existing.parents[1],
        duplicate_policy="skip_identical",
    )[0]

    assert record.status == "duplicate"
    assert record.action == "skip_duplicate"


def test_skip_identical_leaves_duplicate_source_and_existing_destination_unchanged(tmp_path: Path):
    source = tmp_path / "incoming.txt"
    source.write_bytes(b"identical")
    destination_file = tmp_path / "organized" / "Documents" / "existing.txt"
    destination_file.parent.mkdir(parents=True)
    destination_file.write_bytes(b"identical")

    records = build_plan(
        [source],
        destination_file.parents[1],
        duplicate_policy="skip_identical",
    )
    result = execute_plan(records, execute=True)

    assert result[0].status == "skipped"
    assert result[0].action == "skip_duplicate"
    assert source.read_bytes() == b"identical"
    assert destination_file.read_bytes() == b"identical"


def test_report_only_keeps_destination_duplicate_without_overwrite(tmp_path: Path):
    source = tmp_path / "incoming.txt"
    source.write_bytes(b"same content")
    destination_file = tmp_path / "organized" / "Documents" / source.name
    destination_file.parent.mkdir(parents=True)
    destination_file.write_bytes(b"same content")

    result = execute_plan(
        build_plan([source], destination_file.parents[1], duplicate_policy="report_only"),
        execute=True,
    )

    assert result[0].status == "duplicate"
    assert result[0].action == "moved_duplicate"
    assert result[0].destination_path == destination_file.with_name("incoming_1.txt")
    assert destination_file.read_bytes() == b"same content"
    assert result[0].destination_path.read_bytes() == b"same content"
    assert not source.exists()


def test_build_plan_rejects_category_path_traversal(tmp_path: Path):
    source = tmp_path / "file.txt"
    source.write_text("content", encoding="utf-8")

    try:
        build_plan([source], tmp_path / "organized", categories={"..": [".txt"]})
    except ValueError as exc:
        assert "Unsafe category directory" in str(exc)
    else:
        raise AssertionError("unsafe category directory should be rejected")


def test_build_plan_rejects_empty_category_name(tmp_path: Path):
    source = tmp_path / "file.txt"
    source.write_text("content", encoding="utf-8")

    try:
        build_plan([source], tmp_path / "organized", categories={"": [".txt"]})
    except ValueError as exc:
        assert "Unsafe category directory" in str(exc)
    else:
        raise AssertionError("empty category directory should be rejected")


def test_build_plan_skips_files_larger_than_configured_limit(tmp_path: Path):
    small = tmp_path / "small.txt"
    large = tmp_path / "large.txt"
    small.write_bytes(b"1234")
    large.write_bytes(b"12345")

    records = build_plan(
        [small, large],
        tmp_path / "organized",
        max_file_size=4,
    )

    assert [record.status for record in records] == ["planned", "validation_failed"]
    assert records[0].sha256 is not None
    assert records[1].sha256 is None
    assert records[1].action == "skip_too_large"
    assert "exceeds configured limit 4" in (records[1].error or "")
    result = execute_plan(records, execute=True)
    assert small.exists() is False
    assert large.exists()
    assert result[1].status == "validation_failed"
