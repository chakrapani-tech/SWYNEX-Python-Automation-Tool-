from __future__ import annotations

import csv
import json
from pathlib import Path

from src.swynex_automation.dashboard import create_app, load_dashboard_runs


def _write_report(report_dir: Path, run_id: str, started_at: str) -> None:
    payload = {
        "run": {
            "run_id": run_id,
            "started_at": started_at,
            "total_files": 3,
            "files_processed": 2,
            "dry_run": False,
        },
        "records": [
            {"category": "Documents", "status": "processed", "action": "moved"},
            {"category": "Images", "status": "duplicate", "action": "moved_duplicate"},
            {"category": "Documents", "status": "skipped", "action": "skip_duplicate"},
        ],
    }
    (report_dir / f"{run_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    with (report_dir / f"{run_id}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id"])
        writer.writerow([run_id])


def test_dashboard_shows_metrics_category_counts_history_and_report_links(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    _write_report(reports, "older-run", "2026-10-11T10:00:00+00:00")
    _write_report(reports, "latest-run", "2026-10-12T10:00:00+00:00")
    app = create_app(reports)
    app.testing = True

    response = app.test_client().get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "FILES PROCESSED" in page
    assert "latest-run" in page
    assert "older-run" in page
    assert "Documents" in page
    assert "Images" in page
    assert ">2</strong>" in page
    assert "/reports/latest-run.json" in page
    assert "/reports/latest-run.csv" in page
    assert app.test_client().get("/static/dashboard.css").status_code == 200


def test_dashboard_download_is_confined_to_reports_directory(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "run.json").write_text("{}", encoding="utf-8")
    outside = tmp_path / "private.txt"
    outside.write_text("private", encoding="utf-8")
    app = create_app(reports)
    app.testing = True
    client = app.test_client()

    assert client.get("/reports/run.json").status_code == 200
    assert client.get("/reports/../private.txt").status_code == 404
    assert client.get("/reports/private.json").status_code == 404


def test_dashboard_reports_malformed_history_without_hiding_valid_runs(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    _write_report(reports, "valid-run", "2026-10-12T10:00:00+00:00")
    (reports / "broken.json").write_text("{not json", encoding="utf-8")

    runs, errors = load_dashboard_runs(reports)

    assert [run.run["run_id"] for run in runs] == ["valid-run"]
    assert len(errors) == 1
    assert "broken.json" in errors[0]
