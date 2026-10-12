import csv
import json
from pathlib import Path

from main import _parse_args, main


def test_parse_args_defaults():
    args = _parse_args([])
    assert args is not None


def test_cli_dry_run_execute_reports_and_audit_log(tmp_path: Path):
    source = tmp_path / "input"
    destination = tmp_path / "organized"
    reports = tmp_path / "reports"
    source.mkdir()
    (source / "alpha.txt").write_bytes(b"identical text")
    (source / "copy.txt").write_bytes(b"identical text")
    (source / "photo.jpg").write_bytes(b"not a decoded JPG")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "source_dir": str(source),
                "destination_dir": str(destination),
                "report_dir": str(reports),
                "duplicate_policy": "skip_identical",
                "dry_run_default": True,
            }
        ),
        encoding="utf-8",
    )

    assert main(["--config", str(config_path), "--dry-run"]) == 0
    assert sorted(path.name for path in source.iterdir()) == ["alpha.txt", "copy.txt", "photo.jpg"]
    assert not destination.exists()
    dry_run_json = next(reports.glob("*.json"))
    dry_run_payload = json.loads(dry_run_json.read_text(encoding="utf-8"))
    assert dry_run_payload["run"]["dry_run"] is True
    assert {
        record["category"]: Path(record["destination_path"]).parts[-2]
        for record in dry_run_payload["records"]
    } == {"Documents": "Documents", "Images": "Images"}
    csv_rows = csv.DictReader(next(reports.glob("*.csv")).read_text(encoding="utf-8").splitlines())
    assert len(list(csv_rows)) == 3

    assert main(["--config", str(config_path), "--execute"]) == 0
    assert (destination / "Documents" / "alpha.txt").read_bytes() == b"identical text"
    assert (destination / "Images" / "photo.jpg").read_bytes() == b"not a decoded JPG"
    assert (source / "copy.txt").read_bytes() == b"identical text"
    assert len(list(reports.glob("*.json"))) == 2
    assert len(list(reports.glob("*.csv"))) == 2
    audit_log = (tmp_path / "logs" / "swynex.log").read_text(encoding="utf-8")
    assert "File action:" in audit_log
    assert "skip_duplicate" in audit_log


def test_cli_enforces_max_file_size_without_moving_oversized_file(tmp_path: Path):
    source = tmp_path / "input"
    source.mkdir()
    large_file = source / "large.txt"
    large_file.write_bytes(b"exceeds")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "source_dir": str(source),
                "destination_dir": str(tmp_path / "organized"),
                "report_dir": str(tmp_path / "reports"),
                "max_file_size": 3,
            }
        ),
        encoding="utf-8",
    )

    assert main(["--config", str(config_path), "--execute"]) == 0
    assert large_file.read_bytes() == b"exceeds"
    report = json.loads(next((tmp_path / "reports").glob("*.json")).read_text(encoding="utf-8"))
    file_record = report["records"][0]
    assert file_record["status"] == "validation_failed"
    assert file_record["sha256"] is None
    assert report["run"]["validation_failures"] == 1
