# SWYNEX Python Automation Tool

SWYNEX is a local file-organization utility with a command-line workflow and a read-only Flask dashboard for reviewing run reports. It discovers files, classifies them by extension, detects identical content with SHA-256, and can organize files into category folders.

## Features

- Recursive discovery with include and exclude patterns.
- Category folders such as `Documents` and `Images`.
- Configurable maximum file size. Oversized files are reported and left untouched.
- SHA-256 duplicate detection, with `report_only` and `skip_identical` policies.
- Dry-run previews and collision-safe destination names; existing files are not intentionally overwritten.
- CSV/JSON reports and per-file audit entries in `logs\swynex.log`.
- Local dashboard for file metrics, category counts, duplicate counts, run history, and report downloads.

The project classifies by file extension, not by inspecting file contents. The sample `photo.jpg` contains placeholder bytes and is not a valid JPEG. See [Limitations](#limitations) for additional details.

## Requirements and setup

Python 3.11 or newer is required.

In PowerShell, from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

To create the included sample inputs:

```powershell
python scripts\generate_sample_data.py
```

The sample generator writes into `input` and replaces sample files with the same names.

## Use the command line

Use `organized` as the example destination to keep the existing `output` folder separate:

```powershell
# Preview; source files and destination files remain unchanged.
python main.py --source .\input --destination .\organized --dry-run

# Apply the planned actions.
python main.py --source .\input --destination .\organized --execute
```

Typical CLI output:

```text
Discovered 5 files; planned 5 actions.
Dry run: True
```

The dry run still creates reports and log entries. In execute mode, files are placed in category subfolders:

```text
organized\
  Documents\
    copy.txt
    file_0.txt
    file_1.txt
    file_2.txt
  Images\
    photo.jpg
reports\
  swynex-<run-id>_<timestamp>.csv
  swynex-<run-id>_<timestamp>.json
logs\
  swynex.log
```

### Duplicate policies

Set `duplicate_policy` in `config/example_config.json`:

- `report_only` (default): mark byte-identical files as duplicates in the report and still organize every copy. Name collisions receive a numbered suffix instead of replacing an existing file.
- `skip_identical`: mark later identical files as skipped and leave their source files in place. Existing destination content is not changed.

Neither policy deletes duplicate files. Files larger than `max_file_size` are reported as validation failures and remain in the source. The limit is in bytes; files exactly at the configured limit are accepted.

## Web dashboard

Start the dashboard from the project root:

```powershell
python dashboard.py
```

By default it binds only to `127.0.0.1:5000`. Open <http://127.0.0.1:5000/> in a browser. To use a different configuration or port:

```powershell
python dashboard.py --config config\example_config.json --port 5050
```

The dashboard is read-only. It reads JSON run reports from the configured `report_dir`, shows the latest run's metrics and category counts, and lists history with JSON/CSV downloads. Run the CLI at least once to populate the report history. Do not expose it to an untrusted network: it has no authentication, and reports may include local paths and file hashes.

### Screenshot guidance

For a portfolio screenshot, generate a sample run, start the dashboard, and capture the page at a desktop browser width. Save the image as `docs/screenshots/dashboard.png`, then link it from this README if you choose to commit it. Capture only synthetic/sample data; reports can reveal local filenames and paths.

## Configuration

The example configuration is [config/example_config.json](config/example_config.json). Important settings:

| Setting | Purpose |
| --- | --- |
| `source_dir` | Files to discover |
| `destination_dir` | Category-organized output |
| `report_dir` | JSON/CSV history consumed by the dashboard |
| `max_file_size` | Largest accepted file size in bytes |
| `duplicate_policy` | `report_only` or `skip_identical` |
| `dry_run_default` | Default CLI mode when neither `--dry-run` nor `--execute` is supplied |
| `date_folders` | Add source modification-date folders below each category |
| `categories` | Extension-to-category mapping |

CLI `--source` and `--destination` override the matching configuration values.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the layer map and data flow. The CLI and dashboard share the existing `src/swynex_automation` package: the CLI runs discovery, planning, organizing, and reporting; the dashboard reads the resulting JSON/CSV reports and never initiates file operations.

## Tests, lint, and type checks

Run from the project root:

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy src main.py dashboard.py
```

## GitHub portfolio checklist

1. Review reports and logs for local paths or private filenames before publishing.
2. Create a repository on GitHub and ensure generated directories and virtual environments remain untracked (`.gitignore` already excludes them).
3. Initialize and publish from the project root:

   ```powershell
   git init
   git add .
   git commit -m "Prepare SWYNEX automation portfolio project"
   git branch -M main
   git remote add origin https://github.com/<your-account>/<your-repository>.git
   git push -u origin main
   ```

4. Add a concise repository description, topics such as `python`, `flask`, and `automation`, and a dashboard screenshot if desired.
5. Run the setup and validation commands above from a clean clone before sharing the repository.

## Limitations

- Classification is extension-based; file contents and image validity are not verified.
- SHA-256 duplicate detection reads each eligible file and files already in the destination, which can be I/O-intensive for large collections.
- The dashboard's run history comes from JSON reports in `report_dir`; malformed report files are reported in the UI and skipped.
- The dashboard is unauthenticated and intended for local use only. Do not bind it to a public interface without adding appropriate authentication and deployment protections.
- The application does not currently quarantine files or provide automatic cleanup/retention of reports.

## License

Released under the [MIT License](LICENSE).
