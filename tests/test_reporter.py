from pathlib import Path

from src.swynex_automation.models import FileRecord, RunSummary
from src.swynex_automation.reporter import build_summary, write_reports


def test_write_reports_creates_files(tmp_path: Path):
    run = RunSummary(run_id="run-1", source_dir="src", destination_dir="dest")
    records = []
    created = write_reports(run, records, tmp_path, ["csv", "json"])
    assert len(created) == 2
    assert all(path.exists() for path in created)


def test_build_summary_counts_files():
    run = RunSummary(run_id="run-2")
    records = [
        FileRecord(source_path=Path("a.txt"), name="a.txt", extension=".txt", size=10, status="processed"),
        FileRecord(source_path=Path("b.txt"), name="b.txt", extension=".txt", size=20, status="duplicate"),
    ]
    summary = build_summary(records, run)
    assert summary.total_files == 2
    assert summary.files_processed == 1
    assert summary.duplicate_files == 1
    assert summary.total_bytes == 30
