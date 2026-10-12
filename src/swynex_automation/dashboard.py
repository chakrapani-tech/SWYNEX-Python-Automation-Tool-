from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template, send_file


@dataclass(frozen=True)
class DashboardRun:
    run: dict[str, Any]
    category_counts: dict[str, int]
    duplicate_count: int
    json_name: str
    csv_name: str | None


def load_dashboard_runs(report_dir: str | Path) -> tuple[list[DashboardRun], list[str]]:
    report_root = Path(report_dir).expanduser().resolve()
    runs: list[DashboardRun] = []
    errors: list[str] = []
    if not report_root.exists():
        return runs, errors
    if not report_root.is_dir():
        raise NotADirectoryError(f"Report path is not a directory: {report_root}")

    for report_path in sorted(report_root.glob("*.json"), reverse=True):
        try:
            report_path.resolve().relative_to(report_root)
        except ValueError:
            errors.append(f"{report_path.name}: report resolves outside the configured report directory.")
            continue
        try:
            with report_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{report_path.name}: {exc}")
            continue

        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("run"), dict)
            or not isinstance(payload.get("records"), list)
        ):
            errors.append(f"{report_path.name}: report must contain a run object and records array.")
            continue

        category_counts: dict[str, int] = {}
        duplicate_count = 0
        for record in payload["records"]:
            if not isinstance(record, dict):
                continue
            category = record.get("category")
            if isinstance(category, str):
                category_counts[category] = category_counts.get(category, 0) + 1
            if (
                record.get("status") == "duplicate"
                or record.get("action") in {"skip_duplicate", "moved_duplicate", "dry_run_report_duplicate"}
            ):
                duplicate_count += 1

        csv_path = report_path.with_suffix(".csv")
        csv_name = csv_path.name if csv_path.is_file() else None
        runs.append(
            DashboardRun(
                run=payload["run"],
                category_counts=dict(sorted(category_counts.items())),
                duplicate_count=duplicate_count,
                json_name=report_path.name,
                csv_name=csv_name,
            )
        )

    runs.sort(
        key=lambda item: str(item.run.get("started_at", "")),
        reverse=True,
    )
    return runs, errors


def create_app(report_dir: str | Path) -> Flask:
    report_root = Path(report_dir).expanduser().resolve()
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")

    @app.get("/")
    def index():
        runs, errors = load_dashboard_runs(report_root)
        return render_template("dashboard.html", runs=runs, errors=errors)

    @app.get("/reports/<path:filename>")
    def download_report(filename: str):
        report_path = (report_root / filename).resolve()
        try:
            report_path.relative_to(report_root)
        except ValueError:
            abort(404)
        if report_path.suffix.lower() not in {".json", ".csv"} or not report_path.is_file():
            abort(404)
        return send_file(report_path, as_attachment=True, download_name=report_path.name)

    return app
