# Architecture

SWYNEX keeps file operations in its existing processing package and separates presentation from execution.

## Processing flow

1. `main.py` resolves CLI arguments and configuration.
2. `config.py` validates configured paths and policies.
3. `discovery.py` finds eligible source files.
4. `planner.py` checks each file's size before hashing, classifies by suffix, creates category destinations, and compares SHA-256 fingerprints against the current batch and destination tree.
5. `organizer.py` either leaves the plan untouched in dry-run mode or executes collision-safe moves. Oversized and policy-skipped files stay in the source.
6. `reporter.py` builds run totals and writes CSV/JSON reports. `logging_setup.py` records per-file actions.

## Dashboard flow

`dashboard.py` starts a local Flask application built by `src/swynex_automation/dashboard.py`. It reads the existing JSON reports, derives category and duplicate counts, and renders the HTML/CSS in `templates/` and `static/`. Its report-download route confines responses to files below the configured report directory. The dashboard does not call discovery, planning, or organizer code and cannot initiate file moves.

## Safety characteristics

- Source and destination paths must be distinct and must not contain one another.
- The configured size limit is checked before hashing.
- SHA-256 duplicates are either retained (`report_only`) or left at their source (`skip_identical`); neither policy deletes files.
- Existing destination names are resolved with a numbered suffix rather than intentionally overwritten.
- The dashboard binds to loopback by default and is read-only.

The system favors explicit validation, readable reports, and reusable processing modules over hidden side effects.
