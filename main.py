from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from src.swynex_automation.config import (
    AppConfig,
    build_default_config,
    load_config,
    validate_config,
)
from src.swynex_automation.discovery import discover_files
from src.swynex_automation.logging_setup import configure_logging
from src.swynex_automation.models import RunSummary
from src.swynex_automation.organizer import execute_plan
from src.swynex_automation.planner import build_plan
from src.swynex_automation.reporter import build_summary, write_reports


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SWYNEX Intelligent File Processing & Automation Platform")
    parser.add_argument("--config", type=str, help="Path to JSON configuration file")
    parser.add_argument("--source", type=str, help="Source directory to scan")
    parser.add_argument("--destination", type=str, help="Destination directory for organized files")
    parser.add_argument("--dry-run", action="store_true", help="Preview planned actions without modifying files")
    parser.add_argument("--execute", action="store_true", help="Apply the planned organization actions")
    parser.add_argument("--report-format", nargs="+", default=["csv", "json"], help="Output formats: csv json")
    return parser.parse_known_args(argv)[0]


def _resolve_config(args: argparse.Namespace) -> AppConfig:
    if args.config:
        config = load_config(args.config)
    else:
        config = build_default_config()

    if args.source:
        config.source_dir = args.source
    if args.destination:
        config.destination_dir = args.destination
    if args.dry_run:
        config.dry_run_default = True
    if args.execute:
        config.dry_run_default = False
    validate_config(config)
    return config


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        config = _resolve_config(args)
    except (ValueError, FileNotFoundError, OSError, TypeError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    log_dir = Path(config.report_dir).parent / "logs"
    logger = configure_logging(config.log_level, log_dir)
    logger.info("Starting SWYNEX automation run")

    if args.dry_run and args.execute:
        print("Dry-run and execute cannot both be specified.", file=sys.stderr)
        return 2

    execute_mode = args.execute or (not args.dry_run and not config.dry_run_default)
    if not args.dry_run and not args.execute and config.dry_run_default:
        execute_mode = False

    run = RunSummary(
        run_id=f"swynex-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}",
        source_dir=config.source_dir,
        destination_dir=config.destination_dir,
        dry_run=not execute_mode,
    )

    try:
        files = discover_files(config.source_dir, config.recursive, config.include_patterns, config.exclude_patterns)
        records = build_plan(
            files,
            config.destination_dir,
            config.categories,
            config.date_folders,
            dry_run=not execute_mode,
            duplicate_policy=config.duplicate_policy,
            max_file_size=config.max_file_size,
        )
        records = execute_plan(records, execute=execute_mode)
        for record in records:
            logger.info(
                "File action: status=%s action=%s source=%s destination=%s sha256=%s error=%s",
                record.status,
                record.action,
                record.source_path,
                record.destination_path,
                record.sha256,
                record.error,
            )
        run = build_summary(records, run)
        write_reports(run, records, config.report_dir, args.report_format)
        print(f"Discovered {len(files)} files; planned {len(records)} actions.")
        print(f"Dry run: {not execute_mode}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        logger.exception("Processing failed")
        print(f"Processing error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
